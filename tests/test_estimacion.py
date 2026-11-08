"""Pruebas de la tarjeta de estimación (4.1: RF-01, RF-02, RF-03 y RNF-02) y de la gráfica 3 y los ejemplos (4.2: RF-05)."""
import importlib.util
import os
import sys
import time

import pytest
from dash import no_update

from componentes.chip_riesgo import chip_riesgo
from componentes.tarjeta_estimacion import EJEMPLOS, resultado_estimacion
from modelo.inferencia import predecir

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


def _texto(nodo):
    if isinstance(nodo, (str, int, float)):
        return str(nodo)
    if isinstance(nodo, (list, tuple)):
        return ' '.join(_texto(n) for n in nodo)
    hijos = getattr(nodo, 'children', None)
    return '' if hijos is None else _texto(hijos)


CASOS = [('Mexico', 2012, 5), ('Canada', 2000, 10), ('India', 1995, 5)]


@pytest.mark.parametrize('pais, anio, horizonte', CASOS)
def test_tres_casos_dan_tarjeta_completa(dashboard, pais, anio, horizonte):
    texto = _texto(dashboard.calcular_desde('est-calcular', pais, anio, horizonte)[0])
    r = predecir({'pais': pais, 'anio_base': anio, 'horizonte_anios': horizonte})
    assert f"{r['prediccion']:.2f} °C".replace('.', ',') in texto
    assert '± ' in texto and 'error medio (MAE)' in texto          # regla 3: siempre con margen
    assert r['clase_etiqueta'] in texto                              # chip de riesgo con texto
    assert 'frente a 1951–1980' in texto
    assert r['aviso'] in texto                                       # regla 3: siempre con aviso
    assert 'Sin estimación' not in texto


def test_canada_muestra_real_y_error(dashboard):
    texto = _texto(dashboard.calcular_desde('est-calcular', 'Canada', 2000, 10)[0])
    assert 'Real: −1,89 °C' in texto or 'Real: -1,89 °C' in texto
    assert 'Error: 1,96 °C' in texto


@pytest.mark.parametrize('pais, anio, horizonte', [
    ('Heard Island And Mcdonald Islands', 1950, 5),   # sin 10 años previos
    ('Mexico', 1850, 5),                               # año base sin datos
    ('Atlantis', 2012, 5),                             # país inexistente
    ('Mexico', 2012, None),                            # horizonte vacío
])
def test_entrada_invalida_muestra_mensaje_sin_romper(dashboard, pais, anio, horizonte):
    salida = dashboard.calcular_desde('est-calcular', pais, anio, horizonte)
    texto = _texto(salida[0])
    r = predecir(dashboard.armar_entrada(pais, anio, horizonte))
    assert 'Sin estimación para este país' in texto
    assert r['error'] in texto
    assert '± ' not in texto


def test_resultado_sin_prediccion_no_rompe():
    texto = _texto(resultado_estimacion({'prediccion': None, 'error': None}))
    assert 'Sin estimación para este país' in texto


@pytest.mark.parametrize('etiqueta, nivel', [('Riesgo bajo', 'bajo'), ('Riesgo medio', 'medio'), ('Riesgo alto', 'alto')])
def test_chip_riesgo_color_y_texto(etiqueta, nivel):
    chip = chip_riesgo(etiqueta)
    assert chip.children == etiqueta
    assert f'chip-riesgo-{nivel}' in chip.className


def test_callback_tarda_menos_de_3_s(dashboard):
    t0 = time.perf_counter()
    dashboard.calcular_desde('est-calcular', 'Mexico', 2012, 10)
    assert time.perf_counter() - t0 < 3


def test_pais_a_se_copia_al_formulario(dashboard):
    assert dashboard.copiar_pais_a({'a': 'Canada', 'b': None}) == 'Canada'
    assert dashboard.copiar_pais_a({'a': None, 'b': None}) is no_update


# ---------- 4.2: gráfica 3, casos de ejemplo y registro de la última inferencia ----------

def _trazas(fig):
    return {t.name.split(' (')[0]: t for t in fig.data}


@pytest.mark.parametrize('clave, entrada', [(c, e) for c, _, e in EJEMPLOS])
def test_ejemplo_llena_el_formulario_y_calcula(dashboard, clave, entrada):
    tarjeta, fig, titulo, registro, pais, anio, horizonte = dashboard.calcular_desde(f'ejemplo-{clave}', 'Atlantis', None, None)
    assert (pais, anio, horizonte) == (entrada['pais'], entrada['anio_base'], entrada['horizonte_anios'])
    assert 'Sin estimación' not in _texto(tarjeta)
    assert entrada['pais'] in titulo
    assert registro['entrada'] == entrada and registro['salida']['error'] is None
    assert isinstance(registro['tiempo_ms'], int)


@pytest.mark.parametrize('pais, anio, horizonte', CASOS)
def test_grafica_coincide_con_la_tarjeta(dashboard, pais, anio, horizonte):
    _, fig, _, registro, *_ = dashboard.calcular_desde('est-calcular', pais, anio, horizonte)
    r = registro['salida']
    t = _trazas(fig)
    assert {'Histórico', 'Estimación', '± MAE'} <= set(t)
    # la estimación termina en la predicción de la tarjeta, en el año objetivo
    assert list(t['Estimación'].x)[-1] == r['anio_objetivo']
    assert list(t['Estimación'].y)[1:] == r['serie_estimada']
    assert list(t['Histórico'].x)[-1] == anio
    # la banda va de -MAE a +MAE alrededor de la estimación
    y_banda = list(t['± MAE'].y)
    assert max(y_banda) == pytest.approx(max(r['serie_estimada']) + r['mae_modelo'])


def test_valores_reales_cuando_existen(dashboard):
    _, fig, *_ = dashboard.calcular_desde('est-calcular', 'Canada', 2000, 10)
    real = _trazas(fig)['Real']
    assert list(real.x)[-1] == 2010 and round(list(real.y)[-1], 2) == -1.89
    _, fig, *_ = dashboard.calcular_desde('est-calcular', 'Mexico', 2012, 5)
    assert 'Real' not in _trazas(fig)          # 2013-2017 no tienen dato


def test_grafica_sin_estimacion(dashboard):
    _, fig, titulo, registro, *_ = dashboard.calcular_desde('est-calcular', 'Atlantis', 2012, 5)
    assert fig.layout.annotations[0].text == 'Sin estimación para mostrar'
    assert titulo == '' and registro['salida']['error']
