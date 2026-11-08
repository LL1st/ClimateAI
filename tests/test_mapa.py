"""Pruebas del mapa por año (tarea 3.1). El efecto lupa (assets/mapa_lupa.js) se revisa en el navegador."""
import importlib.util
import math
import os
import random
import sys
import time

import pandas as pd
import plotly.graph_objects as go
import pytest

import datos
from componentes.mapa import FACTOR_CHICO, TAMANO_PUNTO, clase_temperatura, figura_mapa

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_mapa_anio_un_registro_por_punto():
    puntos = pd.read_csv(os.path.join(RAIZ, 'data', 'processed', 'puntos_mapa.csv'), keep_default_na=False)
    df = datos.mapa_anio(2012)
    assert len(df) == len(puntos)
    assert {'lat', 'lon', 'iso3', 'pais', 'temp'} <= set(df.columns)
    mexico = datos.serie_pais('Mexico', 2012, 2012).temp_media_anual_c.iloc[0]
    assert (df[df.iso3 == 'MEX'].temp == mexico).all()


def test_ca03_diez_tooltips_coinciden_con_el_dataset():
    df = datos.mapa_anio(1990)
    fig = figura_mapa(df)
    custom = fig.data[0].customdata
    reales = datos.valores_anio(1990).set_index('pais').temp_media_anual_c
    con_dato = [i for i, c in enumerate(custom) if c[1] != 'Sin datos']
    for i in random.Random(42).sample(con_dato, 10):
        pais, texto, _ = custom[i]
        assert texto == f'{reales[pais]:.2f} °C'.replace('.', ',')


def test_clases_en_los_bordes():
    assert clase_temperatura(14.9) == 'Baja'
    assert clase_temperatura(15) == 'Media'
    assert clase_temperatura(25) == 'Media'
    assert clase_temperatura(25.1) == 'Alta'
    assert clase_temperatura(float('nan')) == 'Sin datos'
    assert clase_temperatura(None) == 'Sin datos'


def test_paises_sin_datos_en_gris():
    df = datos.mapa_anio(2012)
    fig = figura_mapa(df)
    colores = dict(zip(df.iso3, fig.data[0].marker.color))
    assert colores['SDS'] == '#C9CFD5'                         # Sudán del Sur
    assert df[df.iso3 == 'SDS'].pais.iloc[0] == 'South Sudan'


def test_figura_de_puntos_con_tamano_base_y_relleno_chico():
    df = datos.mapa_anio(2012)
    fig = figura_mapa(df)
    assert isinstance(fig.data[0], go.Scattergeo)
    tamanos = list(fig.data[0].marker.size)
    esperados = [TAMANO_PUNTO * (FACTOR_CHICO if r else 1) for r in df.relleno]
    assert tamanos == esperados
    assert fig.layout.geo.projection.type == 'equirectangular'
    assert fig.layout.meta['paso'] == 4 and len(fig.layout.meta['factores']) == len(df)


def test_respaldo_coropletico_sin_puntos(monkeypatch):
    monkeypatch.setattr(datos, 'HAY_PUNTOS', False)
    df = datos.mapa_anio(2012)
    assert 'lat' not in df.columns
    assert isinstance(figura_mapa(df).data[0], go.Choropleth)


@pytest.fixture(scope='module')
def pagina_dashboard():
    nombre = 'climateai_app'
    if nombre not in sys.modules:
        spec = importlib.util.spec_from_file_location(nombre, os.path.join(RAIZ, 'app', 'app.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[nombre] = mod
        spec.loader.exec_module(mod)
    return sys.modules['pages.dashboard']


@pytest.mark.parametrize('anio', [1900, 1950, 2012])
def test_callback_del_anio_tarda_menos_de_3_s(pagina_dashboard, anio):
    t0 = time.perf_counter()
    fig, texto = pagina_dashboard.actualizar_mapa(anio, {'a': 'Mexico', 'b': 'Canada'})
    assert time.perf_counter() - t0 < 3
    assert texto == str(anio) and len(fig.data[0].lat) > 900
