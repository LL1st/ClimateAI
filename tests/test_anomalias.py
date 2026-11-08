"""Prueba de las 5 anomalías introducidas (tarea 7.1, criterio CA-08).

Se toma una COPIA en memoria de clima_pais_anio.csv, se suman +3 °C a 5 pares país-año
conocidos, se recalculan las variables derivadas como en preparar_datos.py y se vuelve a
correr el Isolation Forest con la misma configuración de modelo/entrenar.py. Al menos 4 de
los 5 años alterados deben quedar marcados. Los archivos originales no se modifican.
"""
import os
import re

import pandas as pd
import pytest
from sklearn.ensemble import IsolationForest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(RAIZ, 'data', 'processed', 'clima_pais_anio.csv')
ENTRENAR = os.path.join(RAIZ, 'modelo', 'entrenar.py')

# Misma configuración que modelo/entrenar.py (la prueba de abajo verifica que no haya cambiado)
X = ['anio', 'temp_media_5a_c', 'cambio_anio_anterior_c', 'tendencia_c']
VARIABLES_ISO = ['objetivo_cambio_c', 'cambio_anio_anterior_c']
CONTAMINACION, SEMILLA = 0.02, 42

ALTERADOS = [('Mexico', 1985), ('Canada', 1970), ('India', 1960), ('Spain', 1995), ('Brazil', 1975)]
SUMA_C = 3.0


def recalcular_derivadas(df):
    """Variables derivadas de preparar_datos.py (solo con años anteriores, sin fuga)."""
    partes = []
    for pais, d in df.groupby('pais', sort=False):
        d = d.sort_values('anio').copy()
        s = d.set_index('anio').temp_media_anual_c.reindex(range(d.anio.min(), d.anio.max() + 1))
        prev = s.shift(1)
        m5, m10 = prev.rolling(5, min_periods=5).mean(), prev.rolling(10, min_periods=10).mean()
        d['temp_anio_anterior_c'] = d.anio.map(prev)
        d['temp_media_5a_c'] = d.anio.map(m5)
        d['temp_media_10a_c'] = d.anio.map(m10)
        partes.append(d)
    out = pd.concat(partes).loc[df.index]          # mismo orden de filas que el CSV
    out['cambio_anio_anterior_c'] = out.temp_anio_anterior_c - out.temp_media_5a_c
    out['tendencia_c'] = out.temp_media_5a_c - out.temp_media_10a_c
    return out


def detectar(df):
    """Isolation Forest como en entrenar.py. Devuelve el conjunto de (pais, anio) marcados."""
    m = df.dropna(subset=X).sort_values('anio').reset_index(drop=True)
    m['objetivo_cambio_c'] = m.temp_media_anual_c - m.temp_media_5a_c
    iso = IsolationForest(contamination=CONTAMINACION, random_state=SEMILLA).fit(m[VARIABLES_ISO])
    marcados = m[iso.predict(m[VARIABLES_ISO]) == -1]
    return set(zip(marcados.pais, marcados.anio))


@pytest.fixture(scope='module')
def original():
    return pd.read_csv(CSV)


def test_la_configuracion_coincide_con_entrenar_py():
    codigo = open(ENTRENAR, encoding='utf-8').read()
    assert re.search(r"IsolationForest\(contamination=0\.02, random_state=42\)", codigo)
    assert "X = ['anio', 'temp_media_5a_c', 'cambio_anio_anterior_c', 'tendencia_c']" in codigo
    assert "m[['objetivo_cambio_c', 'cambio_anio_anterior_c']]" in codigo


def test_recalcular_no_cambia_los_datos_sin_alterar(original):
    """Sanidad: recalcular las derivadas sobre los datos originales da lo mismo que el CSV."""
    re_calc = recalcular_derivadas(original)
    for col in ['temp_media_5a_c', 'cambio_anio_anterior_c', 'tendencia_c']:
        pd.testing.assert_series_equal(re_calc[col].round(3), original[col].round(3), check_names=False,
                                       atol=0.002)


def test_ninguno_de_los_5_es_anomalia_antes_de_alterarlo(original):
    antes = detectar(original)
    assert not (set(ALTERADOS) & antes)


def test_ca08_al_menos_4_de_5_anomalias_introducidas(original):
    copia = original.copy()
    for pais, anio in ALTERADOS:
        fila = (copia.pais == pais) & (copia.anio == anio)
        assert fila.sum() == 1, f'{pais} {anio} no está en el dataset'
        copia.loc[fila, 'temp_media_anual_c'] += SUMA_C
    despues = detectar(recalcular_derivadas(copia))
    detectados = [par for par in ALTERADOS if par in despues]
    assert len(detectados) >= 4, f'solo se detectaron {detectados}'


def test_el_csv_original_no_cambio(original):
    assert pd.read_csv(CSV).equals(original)
