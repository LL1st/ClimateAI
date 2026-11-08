"""Carga única de los datos de ClimateAI (data/processed).

Los archivos se leen una sola vez, al importar este módulo. Las páginas y los callbacks
solo llaman a estas funciones; nunca leen CSV por su cuenta (regla 2 de CLAUDE.md).
Cada función devuelve una copia, para que nadie modifique la caché por accidente.
"""
import json
import os

import pandas as pd

_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'processed')


def _csv(nombre):
    return pd.read_csv(os.path.join(_DIR, nombre), encoding='utf-8')


def _json(nombre):
    with open(os.path.join(_DIR, nombre), encoding='utf-8') as f:
        return json.load(f)


# --- caché en memoria (se llena una vez) ---
_PAIS_ANIO = _csv('clima_pais_anio.csv')
_MENSUAL = _csv('temperatura_pais_mes.csv')
_GLOBAL = _csv('global_anio.csv')
_ANOMALIAS = _csv('anomalias.csv')
_METRICAS = _json('metricas.json')
_MAE_HORIZONTE = _json('mae_por_horizonte.json')

_PAISES = sorted(_PAIS_ANIO.pais.unique())
ANIO_MIN = int(_PAIS_ANIO.anio.min())   # 1900
ANIO_MAX = int(_PAIS_ANIO.anio.max())   # 2012


def _rango(df, anio_inicio, anio_fin):
    if anio_inicio is not None:
        df = df[df.anio >= anio_inicio]
    if anio_fin is not None:
        df = df[df.anio <= anio_fin]
    return df


# --- funciones públicas ---

def lista_paises():
    """Nombres de los 232 países (en inglés, como vienen de Berkeley Earth), en orden alfabético."""
    return list(_PAISES)


def serie_pais(pais, anio_inicio=None, anio_fin=None):
    """Serie anual de un país: anio, temp_media_anual_c, incertidumbre_c, ref_1951_1980_c, etc.
    Devuelve un DataFrame vacío si el país no existe."""
    df = _rango(_PAIS_ANIO[_PAIS_ANIO.pais == pais], anio_inicio, anio_fin)
    return df.reset_index(drop=True).copy()


def valores_anio(anio):
    """Temperatura media de cada país en un año (para el mapa): pais, temp_media_anual_c."""
    df = _PAIS_ANIO.loc[_PAIS_ANIO.anio == anio, ['pais', 'temp_media_anual_c']]
    return df.reset_index(drop=True).copy()


def serie_global(anio_inicio=None, anio_fin=None):
    """Temperatura global anual: anio, temp_global_tierra_c, temp_global_tierra_oceano_c (1900–2015)."""
    return _rango(_GLOBAL, anio_inicio, anio_fin).reset_index(drop=True).copy()


def mensual_pais(pais, anio_inicio=None, anio_fin=None):
    """Datos mensuales de un país (para el mapa de calor): anio, mes, temp_c."""
    df = _rango(_MENSUAL[_MENSUAL.pais == pais], anio_inicio, anio_fin)
    return df[['anio', 'mes', 'temp_c']].reset_index(drop=True).copy()


def anomalias(pais=None, anio_inicio=None, anio_fin=None):
    """Años atípicos detectados por Isolation Forest, ordenados por año.
    Sin país, devuelve los de todos los países."""
    df = _ANOMALIAS if pais is None else _ANOMALIAS[_ANOMALIAS.pais == pais]
    return _rango(df, anio_inicio, anio_fin).sort_values(['anio', 'pais']).reset_index(drop=True).copy()


def metricas():
    """Contenido de metricas.json (resultados del entrenamiento y peso de las variables)."""
    return json.loads(json.dumps(_METRICAS))


def mae_por_horizonte():
    """MAE del modelo y de la línea base por horizonte, con llaves enteras de 1 a 10."""
    return {int(h): dict(v) for h, v in _MAE_HORIZONTE.items()}


def tabla_pais_anio():
    """Tabla completa país-año (para pruebas y para la tabla de la página Temperaturas)."""
    return _PAIS_ANIO.copy()
