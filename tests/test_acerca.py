"""Pruebas de la página «Acerca del proyecto» (tarea 7.4)."""
import importlib.util
import json
import os
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC = os.path.join(RAIZ, 'data', 'processed')
METRICAS = json.load(open(os.path.join(PROC, 'metricas.json'), encoding='utf-8'))
HORIZONTES = json.load(open(os.path.join(PROC, 'mae_por_horizonte.json'), encoding='utf-8'))


@pytest.fixture(scope='module')
def texto():
    nombre = 'climateai_app'
    if nombre not in sys.modules:
        spec = importlib.util.spec_from_file_location(nombre, os.path.join(RAIZ, 'app', 'app.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[nombre] = mod
        spec.loader.exec_module(mod)

    def _t(nodo):
        if isinstance(nodo, (str, int, float)):
            return str(nodo)
        if isinstance(nodo, (list, tuple)):
            return ' '.join(_t(n) for n in nodo)
        hijos = getattr(nodo, 'children', None)
        return '' if hijos is None else _t(hijos)
    return _t(sys.modules['pages.acerca'].layout())


def _c(valor, dec):
    return f'{valor:.{dec}f}'.replace('.', ',')


@pytest.mark.parametrize('seccion', ['Qué es ClimateAI', 'Datos', 'Modelo', 'Métricas', 'Limitaciones',
                                     'Licencia y créditos'])
def test_tiene_todas_las_secciones(texto, seccion):
    assert seccion in texto


def test_datos(texto):
    assert 'Berkeley Earth' in texto and '232 países' in texto and '1900 a 2012' in texto
    assert '1951 y 1980' in texto and 'CO₂' in texto


def test_modelo_y_metricas_salen_de_los_json(texto):
    assert 'regresión lineal' in texto and 'promedio de los 5 años anteriores' in texto
    for clave in ['linea_base_promedio_5a', 'regresion_lineal', 'random_forest']:
        r = METRICAS['resultados'][clave]
        assert f"{_c(r['mae'], 3)} °C" in texto and _c(r['r2'], 4) in texto
    for v in HORIZONTES.values():
        assert f"{_c(v['mae_modelo'], 3)} °C" in texto
    assert '18.899' in texto and '4.872' in texto and f"{METRICAS['anomalias']} años-país" in texto


def test_limitaciones(texto):
    assert 'no pronósticos oficiales' in texto
    assert f"{_c(HORIZONTES['1']['mae_modelo'], 2)} °C a un año" in texto
    assert f"{_c(HORIZONTES['10']['mae_modelo'], 2)} °C a diez años" in texto
    assert 'No predice desastres naturales' in texto


def test_licencia(texto):
    assert 'Creative Commons BY-NC 4.0' in texto and 'Natural Earth' in texto
