"""Pruebas de app/datos.py (tarea 1.1, criterio CA-01)."""
import builtins
import json

import pandas as pd
import pytest

import datos


# --- CA-01: calidad del dataset país-año ---

def test_cero_duplicados_por_pais_y_anio():
    t = datos.tabla_pais_anio()
    assert t.duplicated(['pais', 'anio']).sum() == 0


def test_cero_nulos_en_temperatura_anual():
    assert datos.tabla_pais_anio().temp_media_anual_c.isna().sum() == 0


def test_232_paises():
    assert len(datos.lista_paises()) == 232
    assert datos.lista_paises() == sorted(datos.lista_paises())


# --- funciones de consulta ---

def test_serie_pais_y_rango():
    s = datos.serie_pais('Mexico', 1950, 1960)
    assert list(s.anio) == list(range(1950, 1961))
    assert (s.pais == 'Mexico').all()
    assert datos.serie_pais('Atlantis').empty


def test_valores_anio_para_el_mapa():
    v = datos.valores_anio(2012)
    assert list(v.columns) == ['pais', 'temp_media_anual_c']
    assert v.pais.is_unique and len(v) > 200


def test_serie_global():
    g = datos.serie_global(2000, 2010)
    assert list(g.anio) == list(range(2000, 2011))


def test_mensual_pais():
    m = datos.mensual_pais('Mexico', 2000, 2000)
    assert list(m.mes) == list(range(1, 13))


def test_anomalias():
    assert len(datos.anomalias()) == 476
    a = datos.anomalias('Finland')
    assert not a.empty and (a.pais == 'Finland').all()


def test_metricas_y_mae():
    assert datos.metricas()['modelo_elegido'] == 'regresion_lineal'
    assert set(datos.mae_por_horizonte()) == set(range(1, 11))


def test_las_copias_no_alteran_la_cache():
    s = datos.serie_pais('Mexico')
    s['temp_media_anual_c'] = 999
    assert (datos.serie_pais('Mexico').temp_media_anual_c != 999).all()


# --- los archivos se leen una sola vez (al importar) ---

def test_ninguna_funcion_vuelve_a_leer_archivos(monkeypatch):
    def prohibido(*a, **k):
        raise AssertionError('una función de datos intentó leer un archivo')
    monkeypatch.setattr(pd, 'read_csv', prohibido)
    monkeypatch.setattr(json, 'load', prohibido)
    monkeypatch.setattr(builtins, 'open', prohibido)
    datos.lista_paises(); datos.serie_pais('Mexico', 1950, 2000); datos.valores_anio(1990)
    datos.serie_global(); datos.mensual_pais('Mexico'); datos.anomalias('Mexico')
    datos.metricas(); datos.mae_por_horizonte(); datos.tabla_pais_anio()
