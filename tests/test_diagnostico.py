"""Pruebas del panel de diagnóstico (tarea 7.3)."""
import importlib.util
import json
import os
import sys

import pytest

import datos
from componentes.diagnostico import NOMBRES_VARIABLES, figura_pesos, registro_inferencia, resumen_metricas

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METRICAS = json.load(open(os.path.join(RAIZ, 'data', 'processed', 'metricas.json'), encoding='utf-8'))


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


def test_grafica_7_usa_los_pesos_de_metricas_json():
    fig = figura_pesos(METRICAS)
    barras = fig.data[0]
    assert barras.orientation == 'h'
    esperado = {NOMBRES_VARIABLES[k]: v for k, v in METRICAS['peso_variables'].items()}
    assert dict(zip(barras.customdata, barras.x)) == esperado          # nombre completo en el tooltip
    assert all(e.split('  ')[1][0] in '+−' for e in barras.y)          # el valor va junto al nombre corto
    # la variable de mayor efecto queda arriba (al final de la lista en Plotly)
    assert abs(barras.x[-1]) == max(abs(v) for v in esperado.values())


def test_colores_segun_el_signo():
    fig = figura_pesos(METRICAS)
    for valor, color in zip(fig.data[0].x, fig.data[0].marker.color):
        assert color == ('#B8461F' if valor >= 0 else '#2E75A9')


def test_resumen_de_metricas():
    texto = resumen_metricas(METRICAS)
    assert '0,307' in texto and '0,318' in texto and 'entrenado hasta 1991' in texto


def test_registro_de_la_ultima_inferencia(dashboard):
    *_, registro, _, _, _ = dashboard.calcular_desde('est-calcular', 'Canada', 2000, 10)
    texto = _texto(registro_inferencia(registro))
    assert 'país Canada' in texto and 'año base 2000' in texto and 'horizonte 10' in texto
    assert f"{registro['tiempo_ms']} ms" in texto
    assert '-3,85 °C' in texto and '2010' in texto
    assert '"valor_real": -1.89' in texto          # JSON completo


def test_registro_con_error(dashboard):
    *_, registro, _, _, _ = dashboard.calcular_desde('est-calcular', 'Atlantis', 2012, 5)
    assert 'error: Elige un país de la lista.' in _texto(registro_inferencia(registro))


def test_sin_inferencias_todavia():
    assert 'Todavía no hay inferencias' in _texto(registro_inferencia(None))


def test_panel_al_final_del_dashboard(dashboard):
    contenido = dashboard.layout()
    ids = [getattr(c, 'id', None) for c in contenido.children]
    assert 'panel-diagnostico' in ids
    assert ids.index('panel-diagnostico') > ids.index('tarjeta-grafica-estimacion')
    assert dashboard.actualizar_diagnostico(None) is not None
