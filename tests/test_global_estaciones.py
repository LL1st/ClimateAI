"""Pruebas de la página «Global y estaciones» (tarea 5.3, RF-09)."""
import importlib.util
import os
import sys
import time

import pandas as pd
import pytest

import datos

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC = os.path.join(RAIZ, 'data', 'processed')
CSV_ANUAL = pd.read_csv(os.path.join(PROC, 'clima_pais_anio.csv'))
CSV_GLOBAL = pd.read_csv(os.path.join(PROC, 'global_anio.csv'))
CSV_MES = pd.read_csv(os.path.join(PROC, 'temperatura_pais_mes.csv'))


@pytest.fixture(scope='module')
def pagina():
    nombre = 'climateai_app'
    if nombre not in sys.modules:
        spec = importlib.util.spec_from_file_location(nombre, os.path.join(RAIZ, 'app', 'app.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[nombre] = mod
        spec.loader.exec_module(mod)
    return sys.modules['pages.global_estaciones']


def _punto(fig, nombre, anio):
    t = next(t for t in fig.data if t.name == nombre)
    return dict(zip(list(t.x), list(t.y)))[anio]


# ---------- RF-09: 5 de 5 valores revisados coinciden con los CSV (cálculo a mano desde los archivos) ----------

def test_rf09_anomalia_anual_del_pais(pagina):
    _, fig4, *_ = pagina.contenido({'pais': 'India', 'anio_inicio': 1900, 'anio_fin': 2012})
    fila = CSV_ANUAL[(CSV_ANUAL.pais == 'India') & (CSV_ANUAL.anio == 2005)].iloc[0]
    assert _punto(fig4, 'India', 2005) == pytest.approx(fila.temp_media_anual_c - fila.ref_1951_1980_c)


def test_rf09_anomalia_global(pagina):
    _, fig4, *_ = pagina.contenido({'pais': 'India', 'anio_inicio': 1900, 'anio_fin': 2012})
    ref = CSV_GLOBAL[CSV_GLOBAL.anio.between(1951, 1980)].temp_global_tierra_c.mean()
    real = CSV_GLOBAL[CSV_GLOBAL.anio == 1998].temp_global_tierra_c.iloc[0]
    assert _punto(fig4, 'Global terrestre', 1998) == pytest.approx(real - ref)


@pytest.mark.parametrize('pais, anio, mes', [('Mexico', 1990, 7), ('Finland', 1940, 1), ('Canada', 2010, 3)])
def test_rf09_celdas_del_mapa_de_calor(pagina, pais, anio, mes):
    *_, fig5, _ = pagina.contenido({'pais': pais, 'anio_inicio': 1900, 'anio_fin': 2012})
    m = CSV_MES[(CSV_MES.pais == pais) & (CSV_MES.mes == mes)]
    esperado = m[m.anio == anio].temp_c.iloc[0] - m[m.anio.between(1951, 1980)].temp_c.mean()
    h = fig5.data[0]
    fila = list(h.y).index(['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'][mes - 1])
    columna = list(h.x).index(anio)
    assert h.z[fila][columna] == pytest.approx(esperado)


# ---------- comportamiento ----------

def test_la_referencia_mensual_no_depende_del_filtro(pagina):
    """Filtrar 2000–2012 no cambia la anomalía de 2005: la referencia siempre es 1951–1980."""
    *_, completo, _ = pagina.contenido({'pais': 'Mexico', 'anio_inicio': 1900, 'anio_fin': 2012})
    *_, corto, _ = pagina.contenido({'pais': 'Mexico', 'anio_inicio': 2000, 'anio_fin': 2012})
    valor = lambda fig: fig.data[0].z[0][list(fig.data[0].x).index(2005)]
    assert valor(corto) == pytest.approx(valor(completo))
    assert list(corto.data[0].x) == list(range(2000, 2013))


def test_global_se_recorta_al_periodo(pagina):
    _, fig4, *_ = pagina.contenido({'pais': 'Mexico', 'anio_inicio': 1950, 'anio_fin': 1990})
    t = next(t for t in fig4.data if t.name == 'Global terrestre')
    assert min(t.x) == 1950 and max(t.x) == 1990


def test_kpis(pagina):
    kpis, *_ = pagina.contenido({'pais': 'Mexico', 'anio_inicio': 1900, 'anio_fin': 2012})
    assert len(kpis) == 3


def test_periodo_sin_datos_no_rompe(pagina):
    _, fig4, _, fig5, _ = pagina.contenido({'pais': 'Heard Island And Mcdonald Islands', 'anio_inicio': 1900,
                                             'anio_fin': 1940})
    assert fig5.layout.annotations[0].text == 'Sin datos mensuales en el periodo elegido'
    # la global sí tiene datos en 1900–1940
    assert any(t.name == 'Global terrestre' and len(t.x) == 41 for t in fig4.data)


def test_responde_en_menos_de_3_s(pagina):
    t0 = time.perf_counter()
    pagina.actualizar({'pais': 'Russia', 'anio_inicio': 1900, 'anio_fin': 2012})
    assert time.perf_counter() - t0 < 3
