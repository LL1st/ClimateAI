"""Pruebas del panel de comparación de dos países (tarea 6.1, RF-07)."""
import importlib.util
import os
import sys

import pandas as pd
import pytest
from dash import no_update

import datos
from componentes.comparacion import figura_comparacion, resumen_comparacion
from componentes.mapa import COLOR_AB

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = pd.read_csv(os.path.join(RAIZ, 'data', 'processed', 'clima_pais_anio.csv'))


@pytest.fixture(scope='module')
def dashboard():
    nombre = 'climateai_app'
    if nombre not in sys.modules:
        spec = importlib.util.spec_from_file_location(nombre, os.path.join(RAIZ, 'app', 'app.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[nombre] = mod
        spec.loader.exec_module(mod)
    return sys.modules['pages.dashboard']


def _texto(nodo):
    if isinstance(nodo, (str, int, float)):
        return str(nodo)
    if isinstance(nodo, (list, tuple)):
        return ' '.join(_texto(n) for n in nodo)
    hijos = getattr(nodo, 'children', None)
    return '' if hijos is None else _texto(hijos)


# ---------- RF-07: la diferencia coincide con un cálculo a mano en 3 casos ----------

@pytest.mark.parametrize('a, b, inicio, fin', [
    ('Mexico', 'Canada', 1900, 2012),
    ('India', 'Spain', 1950, 2000),
    ('Finland', 'Brazil', 1980, 2012),
])
def test_rf07_diferencia_a_mano(a, b, inicio, fin):
    da = CSV[(CSV.pais == a) & CSV.anio.between(inicio, fin)]
    db = CSV[(CSV.pais == b) & CSV.anio.between(inicio, fin)]
    comunes = sorted(set(da.anio) & set(db.anio))
    a_mano = (da[da.anio.isin(comunes)].temp_media_anual_c.sum() / len(comunes)
              - db[db.anio.isin(comunes)].temp_media_anual_c.sum() / len(comunes))
    r = resumen_comparacion(datos.serie_pais(a, inicio, fin), datos.serie_pais(b, inicio, fin))
    assert r['diferencia'] == pytest.approx(a_mano)
    assert r['anios_comunes'] == len(comunes)


def test_cambio_igual_al_kpi_variacion():
    s = datos.serie_pais('Mexico', 1900, 2012).sort_values('anio').temp_media_anual_c.tolist()
    r = resumen_comparacion(datos.serie_pais('Mexico', 1900, 2012), datos.serie_pais('Canada', 1900, 2012))
    assert r['cambio_a'] == pytest.approx(sum(s[-10:]) / 10 - sum(s[:10]) / 10)


def test_diferencia_solo_en_anios_comunes():
    # Heard Island empieza en 1948: la diferencia usa 1948-2012, no todo 1900-2012
    r = resumen_comparacion(datos.serie_pais('Mexico'), datos.serie_pais('Heard Island And Mcdonald Islands'))
    assert r['anios_comunes'] == 65


def test_grafica_a_naranja_continua_y_b_azul_punteada():
    fig = figura_comparacion('Mexico', datos.serie_pais('Mexico'), 'Canada', datos.serie_pais('Canada'))
    a, b = fig.data
    assert a.name == 'A · Mexico' and a.line.color == COLOR_AB['a'] and a.line.dash == 'solid'
    assert b.name == 'B · Canada' and b.line.color == COLOR_AB['b'] and b.line.dash == 'dash'
    assert len(fig.layout.annotations) == 2          # último valor de cada línea


# ---------- panel en el Dashboard ----------

def test_panel_con_dos_paises(dashboard):
    cuerpo, nota = dashboard.comparar({'a': 'Mexico', 'b': 'Canada'}, {'anio_inicio': 1950, 'anio_fin': 2000})
    texto = _texto(cuerpo)
    assert 'Diferencia A − B' in texto and 'Cambio en A' in texto and 'Cambio en B' in texto
    assert nota == 'Temperatura media anual · 1950–2000'


@pytest.mark.parametrize('seleccion', [{'a': 'Mexico', 'b': None}, {'a': None, 'b': None}])
def test_mensaje_si_falta_un_pais(dashboard, seleccion):
    cuerpo, _ = dashboard.comparar(seleccion, None)
    assert 'para comparar' in _texto(cuerpo) and 'Elige' in _texto(cuerpo)


def test_mensaje_si_no_hay_datos_en_el_periodo(dashboard):
    cuerpo, _ = dashboard.comparar({'a': 'Mexico', 'b': 'Heard Island And Mcdonald Islands'},
                                   {'anio_inicio': 1900, 'anio_fin': 1940})
    assert 'no tiene datos en el periodo' in _texto(cuerpo)


def test_comparar_sustituye_a_la_estimacion(dashboard):
    sel = {'a': 'Mexico', 'b': 'Canada'}
    assert dashboard.alternar_panel('comparar', sel) == (True, True, False, 'Mexico', 'Canada')
    assert dashboard.alternar_panel('explorar', None) == (False, False, True, None, None)


def test_selectores_sincronizados_con_el_mapa(dashboard):
    # el mapa cambió el Store -> los selectores toman sus valores
    assert dashboard.sincronizar('paises-ab', {'a': 'Mexico', 'b': 'Canada'}, None, None) == \
        (no_update, 'Mexico', 'Canada')
    # el usuario cambió el selector B -> el Store cambia
    assert dashboard.sincronizar('comp-b', {'a': 'Mexico', 'b': 'Canada'}, 'Mexico', 'India') == \
        ({'a': 'Mexico', 'b': 'India'}, no_update, no_update)
    # elegir el mismo país en A y B deja B vacío
    assert dashboard.sincronizar('comp-b', {'a': 'Mexico', 'b': 'Canada'}, 'Mexico', 'Mexico') == \
        ({'a': 'Mexico', 'b': None}, no_update, None)
    # sin cambios reales no se escribe nada
    assert dashboard.sincronizar('comp-a', {'a': 'Mexico', 'b': 'Canada'}, 'Mexico', 'Canada') == \
        (no_update, no_update, no_update)
