"""Pruebas de la página «Anomalías» (tarea 7.2)."""
import importlib.util
import os
import sys
import time

import pandas as pd
import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = pd.read_csv(os.path.join(RAIZ, 'data', 'processed', 'anomalias.csv'))


@pytest.fixture(scope='module')
def pagina():
    nombre = 'climateai_app'
    if nombre not in sys.modules:
        spec = importlib.util.spec_from_file_location(nombre, os.path.join(RAIZ, 'app', 'app.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[nombre] = mod
        spec.loader.exec_module(mod)
    return sys.modules['pages.anomalias']


def _texto(nodo):
    if isinstance(nodo, (str, int, float)):
        return str(nodo)
    if isinstance(nodo, (list, tuple)):
        return ' '.join(_texto(n) for n in nodo)
    hijos = getattr(nodo, 'children', None)
    return '' if hijos is None else _texto(hijos)


TODO = {'pais': 'Finland', 'anio_inicio': 1900, 'anio_fin': 2012}


def test_todos_los_paises_y_todo_el_periodo(pagina):
    kpis, _, _, filas, _ = pagina.contenido(TODO, pagina.TODOS)
    assert len(filas) == len(CSV) == 476
    texto = _texto(kpis)
    assert '476' in texto and str(CSV.pais.nunique()) in texto and '1900–2012' in texto


def test_filtro_por_pais_y_anios(pagina):
    kpis, _, _, filas, nota = pagina.contenido({'pais': 'Mexico', 'anio_inicio': 1950, 'anio_fin': 2000}, 'Finland')
    esperado = CSV[(CSV.pais == 'Finland') & CSV.anio.between(1950, 2000)]
    assert len(filas) == len(esperado) > 0
    assert {f['pais'] for f in filas} == {'Finland'}
    assert all(1950 <= f['anio'] <= 2000 for f in filas)
    assert nota.startswith('Finland · 1950–2000')


def test_filas_ordenadas_y_con_formato(pagina):
    *_, filas, _ = pagina.contenido(TODO, pagina.TODOS)
    primera = CSV.sort_values('puntaje', ascending=False).iloc[0]
    assert (filas[0]['pais'], filas[0]['anio']) == (primera.pais, primera.anio)
    assert filas[0]['estado'] == 'Revisar' and filas[0]['variable'] == 'Temperatura'
    assert filas[0]['desvio'][0] in '+−' and filas[0]['desvio'].endswith(' °C')


def test_motivo_segun_el_signo(pagina):
    assert 'más cálido' in pagina.motivo(1.5)
    assert 'más frío' in pagina.motivo(-2.4)


def test_grafica_6_del_pais_de_la_barra_lateral(pagina):
    _, fig, nota, *_ = pagina.contenido(TODO, pagina.TODOS)
    marcas = next(t for t in fig.data if t.name == 'Anomalía detectada')
    esperados = sorted(CSV[CSV.pais == 'Finland'].anio)
    assert sorted(marcas.x) == esperados
    assert nota.startswith('Finland (país de la barra lateral)')


def test_recuadro_de_interpretacion(pagina):
    texto = _texto(pagina.layout())
    assert 'Cómo interpretar estos avisos' in texto
    assert 'Isolation Forest señala observaciones aisladas' in texto
    assert 'No predice desastres naturales' in texto


def test_sin_anomalias_no_rompe(pagina):
    kpis, fig, _, filas, _ = pagina.contenido({'pais': 'Mexico', 'anio_inicio': 1900, 'anio_fin': 2012}, 'Mexico')
    assert filas == [] and '0' in _texto(kpis)


def test_responde_en_menos_de_3_s(pagina):
    t0 = time.perf_counter()
    pagina.actualizar(TODO, pagina.TODOS)
    assert time.perf_counter() - t0 < 3
