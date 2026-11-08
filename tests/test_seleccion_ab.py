"""Pruebas de la selección de países A y B en el mapa (tarea 3.2)."""
import importlib.util
import os
import sys

import pytest
from dash import no_update

import datos
from componentes.mapa import COLOR_AB, SELECCION_VACIA, elegir_pais, figura_mapa

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope='module')
def dashboard():
    nombre = 'climateai_app'
    if nombre not in sys.modules:
        spec = importlib.util.spec_from_file_location(nombre, os.path.join(RAIZ, 'app', 'app.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[nombre] = mod
        spec.loader.exec_module(mod)
    return sys.modules['pages.dashboard']


def _clic(pais, curva=0):
    return {'points': [{'curveNumber': curva, 'customdata': [pais, '20,00 °C', 'Media']}]}


# --- regla de clics ---

def test_primer_clic_a_segundo_b_tercero_reemplaza_b():
    sel = elegir_pais(None, 'Mexico')
    assert sel == {'a': 'Mexico', 'b': None}
    sel = elegir_pais(sel, 'Canada')
    assert sel == {'a': 'Mexico', 'b': 'Canada'}
    sel = elegir_pais(sel, 'India')
    assert sel == {'a': 'Mexico', 'b': 'India'}


def test_clic_repetido_no_cambia_nada():
    sel = {'a': 'Mexico', 'b': 'Canada'}
    assert elegir_pais(sel, 'Mexico') == sel
    assert elegir_pais(sel, 'Canada') == sel
    assert elegir_pais({'a': 'Mexico', 'b': None}, 'Mexico') == {'a': 'Mexico', 'b': None}


# --- callback (lógica sin Dash) ---

def test_en_modo_explorar_el_clic_no_elige(dashboard):
    assert dashboard.nueva_seleccion('mapa', _clic('Mexico'), 'explorar', dict(SELECCION_VACIA)) is no_update


def test_cinco_clics_en_modo_comparar(dashboard):
    sel = dict(SELECCION_VACIA)
    esperado = [('Mexico', None), ('Mexico', 'Canada'), ('Mexico', 'Brazil'), ('Mexico', 'India'), ('Mexico', 'Spain')]
    for pais, (a, b) in zip(['Mexico', 'Canada', 'Brazil', 'India', 'Spain'], esperado):
        sel = dashboard.nueva_seleccion('mapa', _clic(pais), 'comparar', sel)
        assert sel == {'a': a, 'b': b}


def test_clics_que_se_ignoran(dashboard):
    sel = {'a': 'Mexico', 'b': None}
    assert dashboard.nueva_seleccion('mapa', _clic('South Sudan'), 'comparar', sel) is no_update   # sin datos
    assert dashboard.nueva_seleccion('mapa', _clic('Canada', curva=1), 'comparar', sel) is no_update  # marca A/B
    assert dashboard.nueva_seleccion('mapa', None, 'comparar', sel) is no_update


def test_limpiar(dashboard):
    sel = {'a': 'Mexico', 'b': 'Canada'}
    assert dashboard.nueva_seleccion('limpiar-ab', None, 'comparar', sel) == SELECCION_VACIA


# --- marcas en el mapa ---

def test_marcas_a_y_b_en_un_punto_de_cada_pais():
    df = datos.mapa_anio(2012)
    fig = figura_mapa(df, {'a': 'Mexico', 'b': 'Canada'}, datos.posicion_pais)
    marcas = fig.data[1]
    assert list(marcas.text) == ['<b>A</b>', '<b>B</b>']
    assert list(marcas.marker.color) == [COLOR_AB['a'], COLOR_AB['b']]
    for pais, lat, lon in zip(['Mexico', 'Canada'], marcas.lat, marcas.lon):
        assert ((df.pais == pais) & (df.lat == lat) & (df.lon == lon)).any()


def test_sin_seleccion_la_traza_de_marcas_va_vacia():
    fig = figura_mapa(datos.mapa_anio(2012), dict(SELECCION_VACIA), datos.posicion_pais)
    assert len(fig.data) == 2 and len(fig.data[1].lat) == 0


def test_mostrar_seleccion(dashboard):
    chips, oculto, limpiar_desactivado = dashboard.mostrar_seleccion('explorar', dict(SELECCION_VACIA))
    assert oculto and limpiar_desactivado
    chips, oculto, limpiar_desactivado = dashboard.mostrar_seleccion('comparar', {'a': 'Mexico', 'b': None})
    assert not oculto and not limpiar_desactivado
