"""Pruebas de la tabla de países a ISO3 (tarea 2.1)."""
import importlib.util
import os

import pandas as pd

import datos

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLA = pd.read_csv(os.path.join(RAIZ, 'data', 'processed', 'paises_iso3.csv'),
                    encoding='utf-8', keep_default_na=False)   # iso3 vacío se lee como '' y no como NaN


def _script():
    spec = importlib.util.spec_from_file_location('generar_paises_iso3',
                                                  os.path.join(RAIZ, 'scripts', 'generar_paises_iso3.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_una_fila_por_cada_pais_del_dataset():
    assert list(TABLA.columns) == ['pais', 'iso3']
    assert sorted(TABLA.pais) == datos.lista_paises()


def test_codigos_validos_y_sin_repetir():
    con_codigo = TABLA[TABLA.iso3 != '']
    assert con_codigo.iso3.str.fullmatch(r'[A-Z]{3}').all()
    assert con_codigo.iso3.is_unique


def test_solo_los_territorios_listados_quedan_sin_codigo():
    sin = set(TABLA.loc[TABLA.iso3 == '', 'pais'])
    assert sin == set(_script().SIN_CODIGO)
    assert len(sin) == 4


def test_casos_no_estandar():
    codigo = dict(zip(TABLA.pais, TABLA.iso3))
    assert codigo['Burma'] == 'MMR'
    assert codigo['Congo (Democratic Republic Of The)'] == 'COD'
    assert codigo["Côte D'Ivoire"] == 'CIV'
    assert codigo['Turks And Caicas Islands'] == 'TCA'
    assert codigo['Åland'] == 'ALA'
    assert codigo['Mexico'] == 'MEX'


def test_el_script_cubre_todos_los_nombres():
    _, desconocidos = _script().construir_tabla(datos.lista_paises())
    assert desconocidos == []
