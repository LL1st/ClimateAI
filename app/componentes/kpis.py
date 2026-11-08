"""Fila de 4 KPIs del Dashboard (tarea 5.1). Reaccionan a los filtros globales de país y años.

- Temperatura media: promedio anual del país en el periodo.
- Variación del periodo: promedio de los últimos 10 años menos el de los primeros 10
  (con periodos de menos de 20 años, la mitad final menos la mitad inicial).
- Cambio frente a 1951–1980: promedio del periodo menos el promedio de referencia del país.
- Anomalías: años atípicos de anomalias.csv dentro del periodo.
"""
import dash_bootstrap_components as dbc
import pandas as pd

from componentes.formato import con_signo, num
from componentes.tarjeta_kpi import tarjeta_kpi

VENTANA = 10


def calcular_kpis(serie, anomalias):
    """serie: datos.serie_pais(pais, inicio, fin). anomalias: datos.anomalias(pais, inicio, fin).
    Devuelve un dict con los valores (None cuando no hay datos)."""
    if serie is None or serie.empty:
        return {'media': None, 'variacion': None, 'ventana': None, 'cambio_ref': None,
                'referencia': None, 'anomalias': 0, 'anio_inicio': None, 'anio_fin': None}
    temps = serie.sort_values('anio').temp_media_anual_c.reset_index(drop=True)
    ventana = min(VENTANA, len(temps) // 2)
    variacion = float(temps.tail(ventana).mean() - temps.head(ventana).mean()) if ventana >= 1 else None
    media = float(temps.mean())
    referencia = serie.ref_1951_1980_c.iloc[0]
    referencia = None if pd.isna(referencia) else float(referencia)
    return {
        'media': media,
        'variacion': variacion,
        'ventana': ventana,
        'cambio_ref': None if referencia is None else media - referencia,
        'referencia': referencia,
        'anomalias': int(len(anomalias)),
        'anio_inicio': int(serie.anio.min()),
        'anio_fin': int(serie.anio.max()),
    }


def fila_kpis(pais, k):
    """Las 4 tarjetas a partir de calcular_kpis(). Con «Sin datos» cuando el periodo está vacío."""
    periodo = f"{k['anio_inicio']}–{k['anio_fin']}" if k['anio_inicio'] else 'sin datos en el periodo'
    if k['media'] is None:
        valores = ('Sin datos',) * 3
    else:
        valores = (f"{num(k['media'])} °C",
                   f"{con_signo(k['variacion'])} °C" if k['variacion'] is not None else '—',
                   f"{con_signo(k['cambio_ref'])} °C" if k['cambio_ref'] is not None else '—')
    ventana = k['ventana'] or VENTANA
    tarjetas = [
        tarjeta_kpi('Temperatura media', valores[0], f'{pais} · {periodo}', icono_nombre='termometro',
                    tono='naranja', id='kpi-media'),
        tarjeta_kpi('Variación del periodo', valores[1],
                    f'Últimos {ventana} años frente a los primeros {ventana}', icono_nombre='tendencia',
                    tono='azul', id='kpi-variacion'),
        tarjeta_kpi('Cambio frente a 1951–1980', valores[2],
                    f"Referencia: {num(k['referencia'])} °C" if k['referencia'] is not None else 'Sin referencia',
                    icono_nombre='barras', tono='verde', id='kpi-cambio'),
        tarjeta_kpi('Anomalías', str(k['anomalias']), 'Años atípicos por revisar', icono_nombre='alerta',
                    tono='aviso', id='kpi-anomalias'),
    ]
    return [dbc.Col(t, sm=6, xl=3) for t in tarjetas]
