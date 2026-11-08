"""Pruebas del contrato de predecir() (tarea 0.2). El contrato está descrito en CLAUDE.md."""
import time

import pytest

from modelo.inferencia import predecir

LLAVES_CONTRATO = {
    'pais', 'anio_base', 'anio_objetivo', 'prediccion', 'serie_estimada', 'mae_modelo',
    'clase_etiqueta', 'cambio_vs_1951_1980', 'confianza_o_score', 'valor_real', 'aviso', 'error', 'tiempo_ms',
}
LIMITE_S = 3  # RNF-01


def test_mexico_5_anios_devuelve_todo_el_contrato():
    r = predecir({'pais': 'Mexico', 'horizonte_anios': 5})
    assert set(r) == LLAVES_CONTRATO
    assert r['error'] is None
    assert r['anio_objetivo'] == r['anio_base'] + 5
    assert isinstance(r['prediccion'], float)
    assert len(r['serie_estimada']) == 5
    assert r['serie_estimada'][-1] == r['prediccion']
    assert r['mae_modelo'] > 0
    assert r['clase_etiqueta'] in {'Riesgo bajo', 'Riesgo medio', 'Riesgo alto'}
    assert r['aviso']


@pytest.mark.parametrize('entrada', [
    pytest.param({'pais': 'Atlantis', 'horizonte_anios': 5}, id='pais_inexistente'),
    pytest.param({'pais': 'Mexico', 'horizonte_anios': 0}, id='horizonte_0'),
    pytest.param({'pais': 'Mexico', 'horizonte_anios': 11}, id='horizonte_11'),
    pytest.param({}, id='entrada_vacia'),
    pytest.param({'pais': 'Mexico', 'anio_base': 1850, 'horizonte_anios': 5}, id='anio_base_sin_datos'),
])
def test_entrada_invalida_devuelve_error_sin_excepcion(entrada):
    r = predecir(entrada)  # si lanzara una excepción, la prueba fallaría aquí
    assert r['prediccion'] is None
    assert isinstance(r['error'], str) and r['error']
    assert isinstance(r['tiempo_ms'], int)


def test_canada_2000_a_10_anios_trae_valor_real():
    r = predecir({'pais': 'Canada', 'anio_base': 2000, 'horizonte_anios': 10})
    assert r['error'] is None
    assert r['anio_objetivo'] == 2010
    assert isinstance(r['valor_real'], float)


@pytest.mark.parametrize('entrada', [
    {'pais': 'Mexico', 'horizonte_anios': 5},
    {'pais': 'Canada', 'anio_base': 2000, 'horizonte_anios': 10},
    {'pais': 'India', 'anio_base': 1995, 'horizonte_anios': 5},
    {'pais': 'Atlantis', 'horizonte_anios': 5},
])
def test_cada_llamada_tarda_menos_de_3_s(entrada):
    t0 = time.perf_counter()
    predecir(entrada)
    assert time.perf_counter() - t0 < LIMITE_S
