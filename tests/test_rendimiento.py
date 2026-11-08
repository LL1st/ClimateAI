"""Pruebas de rendimiento de los callbacks principales (tarea 8.1, RNF-01).

Cada callback se llama directamente con un caso pesado (por ejemplo, Rusia con todo el
periodo) y se mide también la serialización a JSON de su salida, que es lo que Dash envía
al navegador. Se toma el peor de 3 intentos. Falla si alguno pasa de 3 s.
"""
import importlib.util
import json
import os
import sys
import time

import plotly.utils
import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIMITE_S = 3.0
INTENTOS = 3
TODO = {'pais': 'Russia', 'anio_inicio': 1900, 'anio_fin': 2012}
AB = {'a': 'Russia', 'b': 'Brazil'}


@pytest.fixture(scope='module')
def paginas():
    nombre = 'climateai_app'
    if nombre not in sys.modules:
        spec = importlib.util.spec_from_file_location(nombre, os.path.join(RAIZ, 'app', 'app.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[nombre] = mod
        spec.loader.exec_module(mod)
    return {n: sys.modules[f'pages.{n}'] for n in ('dashboard', 'temperaturas', 'global_estaciones', 'anomalias')}


# (nombre, función que recibe las páginas y ejecuta el callback)
CASOS = [
    ('mapa por año (1900)', lambda p: p['dashboard'].actualizar_mapa(1900, AB)),
    ('mapa por año (2012)', lambda p: p['dashboard'].actualizar_mapa(2012, AB)),
    ('estimación (botón)', lambda p: p['dashboard'].calcular_desde('est-calcular', 'Russia', 2012, 10)),
    ('estimación (ejemplo Canadá)', lambda p: p['dashboard'].calcular_desde('ejemplo-canada', None, None, None)),
    ('KPIs del Dashboard (filtros)', lambda p: p['dashboard'].actualizar_kpis(TODO)),
    ('selección A/B en el mapa', lambda p: p['dashboard'].nueva_seleccion(
        'mapa', {'points': [{'curveNumber': 0, 'customdata': ['Brazil', '', '']}]}, 'comparar', {'a': 'Russia', 'b': None})),
    ('comparación de dos países', lambda p: p['dashboard'].comparar(AB, TODO)),
    ('página Temperaturas (filtros)', lambda p: p['temperaturas'].actualizar(TODO)),
    ('página Global y estaciones (filtros)', lambda p: p['global_estaciones'].actualizar(TODO)),
    ('página Anomalías (filtros)', lambda p: p['anomalias'].actualizar(TODO, p['anomalias'].TODOS)),
    ('diagnóstico (registro)', lambda p: p['dashboard'].actualizar_diagnostico(
        p['dashboard'].calcular_desde('est-calcular', 'Mexico', 2012, 5)[3])),
]


def _medir(funcion):
    """Peor tiempo de INTENTOS ejecuciones, incluida la serialización a JSON que hace Dash."""
    peor = 0.0
    for _ in range(INTENTOS):
        t0 = time.perf_counter()
        salida = funcion()
        json.dumps(salida, cls=plotly.utils.PlotlyJSONEncoder)
        peor = max(peor, time.perf_counter() - t0)
    return peor


@pytest.mark.parametrize('nombre, callback', CASOS, ids=[c[0] for c in CASOS])
def test_callback_en_menos_de_3_s(paginas, nombre, callback):
    segundos = _medir(lambda: callback(paginas))
    print(f'\n  {nombre}: {segundos * 1000:.0f} ms')
    assert segundos < LIMITE_S, f'{nombre} tardó {segundos:.2f} s (límite {LIMITE_S} s)'


def test_carga_de_paginas_en_menos_de_3_s(paginas):
    """Abrir cada página arma su layout (el Dashboard calcula el mapa inicial)."""
    for nombre, pagina in paginas.items():
        segundos = _medir(pagina.layout)
        assert segundos < LIMITE_S, f'abrir {nombre} tardó {segundos:.2f} s'
