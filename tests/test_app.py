"""Pruebas del esqueleto de la app (tarea 1.2)."""
import importlib.util
import os
import sys

import dash
import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope='module')
def modulo_app():
    # se carga por ruta para no confundir app/app.py con la carpeta app/
    nombre = 'climateai_app'
    if nombre not in sys.modules:
        spec = importlib.util.spec_from_file_location(nombre, os.path.join(RAIZ, 'app', 'app.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[nombre] = mod
        spec.loader.exec_module(mod)
    return sys.modules[nombre]


def _componentes(nodo):
    """Recorre el árbol de componentes y devuelve todos los nodos."""
    yield nodo
    hijos = getattr(nodo, 'children', None)
    if isinstance(hijos, (list, tuple)):
        for h in hijos:
            yield from _componentes(h)
    elif hijos is not None:
        yield from _componentes(hijos)


def _ids(nodo):
    return {getattr(c, 'id', None) for c in _componentes(nodo)} - {None}


def _texto(nodo):
    return ' '.join(str(c) for c in _componentes(nodo) if isinstance(c, (str, int, float)))


def test_cinco_paginas_con_sus_rutas(modulo_app):
    rutas = {p['path']: p['name'] for p in dash.page_registry.values()}
    assert rutas == {'/': 'Dashboard', '/temperaturas': 'Temperaturas',
                     '/global-y-estaciones': 'Global y estaciones', '/anomalias': 'Anomalías',
                     '/acerca': 'Acerca del proyecto'}


def test_layout_tiene_filtros_sidebar_y_aviso(modulo_app):
    ids = _ids(modulo_app.app.layout)
    assert {'filtros', 'sidebar', 'menu', 'filtro-pais', 'filtro-anios', 'aviso-transparencia'} <= ids
    assert 'proyecto académico' in _texto(modulo_app.app.layout)


def test_dashboard_muestra_datos_y_modelo_cargados(modulo_app):
    pagina = next(p for p in dash.page_registry.values() if p['path'] == '/')
    contenido = pagina['layout']()
    texto = _texto(contenido)
    assert '232 países' in texto
    assert '± ' in texto and '°C' in texto      # la estimación lleva su margen
    assert 'Sin estimación' not in texto


def test_filtros_iniciales(modulo_app):
    assert modulo_app.armar_filtros('Mexico', [1900, 2012]) == {'pais': 'Mexico', 'anio_inicio': 1900, 'anio_fin': 2012}
    assert modulo_app.armar_filtros('Canada', None) == {'pais': 'Canada', 'anio_inicio': 1900, 'anio_fin': 2012}
