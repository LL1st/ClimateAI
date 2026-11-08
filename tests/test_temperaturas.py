"""Pruebas de la página «Explorador de temperaturas» (tarea 5.2)."""
import importlib.util
import os
import sys
import time

import pytest

import datos
from componentes.explorador import PAISES_REFERENCIA, filas_tabla, valor_referencia

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = datos.tabla_pais_anio()


@pytest.fixture(scope='module')
def pagina():
    nombre = 'climateai_app'
    if nombre not in sys.modules:
        spec = importlib.util.spec_from_file_location(nombre, os.path.join(RAIZ, 'app', 'app.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[nombre] = mod
        spec.loader.exec_module(mod)
    return sys.modules['pages.temperaturas']


def _texto(nodo):
    if isinstance(nodo, (str, int, float)):
        return str(nodo)
    if isinstance(nodo, (list, tuple)):
        return ' '.join(_texto(n) for n in nodo)
    hijos = getattr(nodo, 'children', None)
    return '' if hijos is None else _texto(hijos)


FILTROS = {'pais': 'Finland', 'anio_inicio': 1950, 'anio_fin': 2000}


def test_tabla_coincide_con_el_csv(pagina):
    *_, filas, nota = pagina.contenido(FILTROS)
    d = CSV[(CSV.pais == 'Finland') & CSV.anio.between(1950, 2000)]
    assert len(filas) == len(d) == 51
    assert [f['anio'] for f in filas] == sorted(d.anio, reverse=True)
    f1990 = next(f for f in filas if f['anio'] == 1990)
    real = d[d.anio == 1990].iloc[0]
    assert f1990['temp'] == f'{real.temp_media_anual_c:.2f} °C'.replace('.', ',')
    assert f1990['incertidumbre'] == f'± {real.incertidumbre_c:.2f}'.replace('.', ',')


def test_columna_anomalia(pagina):
    *_, filas, _ = pagina.contenido(FILTROS)
    an = datos.anomalias('Finland', 1950, 2000)
    marcadas = {f['anio'] for f in filas if f['anomalia'] == 'Sí'}
    assert marcadas == set(an.anio) and len(marcadas) > 0


def test_grafica_con_serie_y_anomalias(pagina):
    _, fig, nota, *_ = pagina.contenido(FILTROS)
    nombres = [t.name for t in fig.data]
    assert 'Temperatura media' in nombres and 'Anomalía detectada' in nombres
    linea = next(t for t in fig.data if t.name == 'Temperatura media')
    assert list(linea.x) == list(range(1950, 2001))
    assert nota == 'Temperatura media anual · Finland · 1950–2000'


def test_kpis_de_la_pagina(pagina):
    kpis, *_ = pagina.contenido(FILTROS)
    texto = _texto(kpis)
    d = CSV[(CSV.pais == 'Finland') & CSV.anio.between(1950, 2000)]
    assert f'{d.temp_media_anual_c.mean():.2f} °C'.replace('.', ',') in texto
    assert '51 años' in texto and 'de los 51 del periodo' in texto


def test_referencia_cuatro_paises_mas_el_filtrado(pagina):
    _, _, _, barras, *_ = pagina.contenido(FILTROS)
    texto = _texto(barras)
    for p in PAISES_REFERENCIA + ['Finland']:
        assert p in texto
    assert len(barras) == 5
    _, _, _, barras_mx, *_ = pagina.contenido({'pais': 'Mexico', 'anio_inicio': 1900, 'anio_fin': 2012})
    assert len(barras_mx) == 4                       # México ya es de referencia


def test_valor_referencia_es_el_ultimo_anio_del_periodo():
    anio, temp = valor_referencia(datos.serie_pais('Spain', 1900, 1980))
    assert anio == 1980
    assert temp == pytest.approx(CSV[(CSV.pais == 'Spain') & (CSV.anio == 1980)].temp_media_anual_c.iloc[0])


def test_periodo_sin_datos_no_rompe(pagina):
    kpis, fig, _, barras, _, filas, _ = pagina.contenido(
        {'pais': 'Heard Island And Mcdonald Islands', 'anio_inicio': 1900, 'anio_fin': 1940})
    assert filas == [] and 'Sin datos' in _texto(kpis)
    assert fig.layout.annotations[0].text == 'Sin datos en el periodo elegido'


def test_responde_en_menos_de_3_s(pagina):
    t0 = time.perf_counter()
    pagina.actualizar({'pais': 'Russia', 'anio_inicio': 1900, 'anio_fin': 2012})
    assert time.perf_counter() - t0 < 3


def test_filas_tabla_vacia():
    assert filas_tabla(datos.serie_pais('Atlantis'), set()) == []


def test_etiquetas_de_anio_solo_con_pocas_anomalias(pagina):
    _, pocas, *_ = pagina.contenido({'pais': 'Finland', 'anio_inicio': 1950, 'anio_fin': 1960})
    _, muchas, *_ = pagina.contenido({'pais': 'Finland', 'anio_inicio': 1900, 'anio_fin': 2012})
    marcas = lambda fig: next(t for t in fig.data if t.name == 'Anomalía detectada')
    assert marcas(pocas).mode == 'markers+text'
    assert marcas(muchas).mode == 'markers'
