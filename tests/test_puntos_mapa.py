"""Pruebas de data/processed/puntos_mapa.csv (tarea 2.2). Leen el CSV ya generado:
no necesitan geopandas ni internet."""
import ast
import os

import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUNTOS = pd.read_csv(os.path.join(RAIZ, 'data', 'processed', 'puntos_mapa.csv'), keep_default_na=False)
PAISES = pd.read_csv(os.path.join(RAIZ, 'data', 'processed', 'paises_iso3.csv'), keep_default_na=False)
CON_CODIGO = set(PAISES.iso3) - {''}


def _sin_datos():
    # se lee del script sin importarlo (importarlo exigiría geopandas)
    with open(os.path.join(RAIZ, 'scripts', 'generar_puntos_mapa.py'), encoding='utf-8') as f:
        arbol = ast.parse(f.read())
    for nodo in arbol.body:
        if (isinstance(nodo, ast.Assign) and isinstance(nodo.targets[0], ast.Name)
                and nodo.targets[0].id == 'SIN_DATOS'):
            return set(ast.literal_eval(nodo.value))
    raise AssertionError('SIN_DATOS no está en el script')


def test_columnas_y_cantidad():
    assert list(PUNTOS.columns) == ['lat', 'lon', 'iso3']
    assert 3000 <= len(PUNTOS) <= 10000


def test_coordenadas_validas_y_sin_repetidos():
    assert PUNTOS.lat.between(-60, 85).all()
    assert PUNTOS.lon.between(-180, 180).all()
    assert not PUNTOS.duplicated().any()


def test_casi_todos_los_paises_tienen_punto():
    con_punto = CON_CODIGO & set(PUNTOS.iso3)
    assert len(con_punto) / len(CON_CODIGO) >= 0.95


def test_todo_codigo_es_nuestro_o_sin_datos():
    assert set(PUNTOS.iso3) <= CON_CODIGO | _sin_datos()


def test_ultramar_separado_de_su_pais():
    guf = PUNTOS[PUNTOS.iso3 == 'GUF']
    assert not guf.empty and (guf.lon < -50).all()          # Guayana Francesa en Sudamérica
    assert (PUNTOS[PUNTOS.iso3 == 'FRA'].lon > -10).all()    # Francia solo en Europa
    assert (PUNTOS[PUNTOS.iso3 == 'NOR'].lat < 72).all()     # Svalbard aparte de Noruega
