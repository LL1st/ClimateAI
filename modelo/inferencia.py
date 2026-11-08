"""Contrato de inferencia de ClimateAI: predecir(datos_entrada) -> dict.
El dashboard solo importa esta función. Nunca lanza excepciones hacia la interfaz."""
import os, time, joblib, pandas as pd

_BASE = os.path.dirname(os.path.abspath(__file__))
_PAQ = joblib.load(os.path.join(_BASE, 'modelo_clima.joblib'))            # se carga una sola vez
_DATOS = pd.read_csv(os.path.join(_BASE, '..', 'data', 'processed', 'clima_pais_anio.csv'))
_ULTIMO_ANIO = int(_DATOS.anio.max())
import json
_MAE_H = {int(k): v['mae_modelo'] for k, v in json.load(open(os.path.join(_BASE, '..', 'data', 'processed', 'mae_por_horizonte.json'))).items()}  # error medido por horizonte
AVISO = 'Estimación académica basada en patrones históricos. No es un pronóstico oficial.'

def _riesgo(cambio):
    return 'Riesgo bajo' if cambio < 0.5 else ('Riesgo medio' if cambio <= 1.0 else 'Riesgo alto')

def _error(msg, t0):
    return {'prediccion': None, 'error': msg, 'tiempo_ms': round((time.perf_counter() - t0) * 1000)}

def predecir(datos_entrada: dict) -> dict:
    t0 = time.perf_counter()
    try:
        pais = datos_entrada.get('pais')
        h = datos_entrada.get('horizonte_anios')
        serie = _DATOS[_DATOS.pais == pais].set_index('anio').temp_media_anual_c if pais else None
        if not pais or serie is None or serie.empty:
            return _error('Elige un país de la lista.', t0)
        base = datos_entrada.get('anio_base', int(serie.index.max()))
        if not isinstance(h, int) or not 1 <= h <= 10:
            return _error('El horizonte debe ser un número entero de 1 a 10 años.', t0)
        if not isinstance(base, int) or base not in serie.index:
            return _error(f'No hay dato de {pais} para el año base {base}.', t0)
        hist = serie.loc[:base]
        if len(hist) < 10 or list(hist.index[-10:]) != list(range(base - 9, base + 1)):
            return _error('Este país no tiene 10 años seguidos de datos antes del año base; no se puede estimar.', t0)
        valores = list(hist.values[-10:])
        modelo, X = _PAQ['modelo'], _PAQ['variables']
        estimada = []
        for paso in range(1, h + 1):
            m5, m10, prev = sum(valores[-5:]) / 5, sum(valores[-10:]) / 10, valores[-1]
            fila = pd.DataFrame([[base + paso, m5, prev - m5, m5 - m10]], columns=X)
            temp = m5 + float(modelo.predict(fila)[0])
            estimada.append(round(temp, 2)); valores.append(temp)
        objetivo = base + h
        ref = float(_DATOS[_DATOS.pais == pais].ref_1951_1980_c.iloc[0])
        cambio = estimada[-1] - ref
        salida = {'pais': pais, 'anio_base': base, 'anio_objetivo': objetivo, 'prediccion': estimada[-1],
                  'serie_estimada': estimada, 'mae_modelo': _MAE_H.get(h, _PAQ['mae']), 'clase_etiqueta': _riesgo(cambio),
                  'cambio_vs_1951_1980': round(cambio, 2), 'confianza_o_score': _MAE_H.get(h, _PAQ['mae']),
                  'valor_real': round(float(serie[objetivo]), 2) if objetivo in serie.index else None,
                  'aviso': AVISO, 'error': None}
        salida['tiempo_ms'] = round((time.perf_counter() - t0) * 1000)
        return salida
    except Exception as e:                                     # RNF-02: la interfaz nunca se rompe
        return _error(f'No se pudo calcular la estimación ({type(e).__name__}).', t0)
