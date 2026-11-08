"""Pruebas de la opción «Promedio global (tierra firme)» del filtro de país."""
import importlib.util
import os
import sys

import pandas as pd
import pytest

import datos
from componentes.grafica_estimacion import figura_evolucion_promedio

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_GLOBAL = pd.read_csv(os.path.join(RAIZ, 'data', 'processed', 'global_anio.csv'))
CSV_ANOM = pd.read_csv(os.path.join(RAIZ, 'data', 'processed', 'anomalias.csv'))
GLOBAL_TODO = {'pais': datos.GLOBAL, 'anio_inicio': 1900, 'anio_fin': 2012}


@pytest.fixture(scope='module')
def paginas():
    nombre = 'climateai_app'
    if nombre not in sys.modules:
        spec = importlib.util.spec_from_file_location(nombre, os.path.join(RAIZ, 'app', 'app.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[nombre] = mod
        spec.loader.exec_module(mod)
    return {n: sys.modules[f'pages.{n}'] for n in ('dashboard', 'temperaturas', 'global_estaciones', 'anomalias')}


def _texto(nodo):
    if isinstance(nodo, (str, int, float)):
        return str(nodo)
    if isinstance(nodo, (list, tuple)):
        return ' '.join(_texto(n) for n in nodo)
    hijos = getattr(nodo, 'children', None)
    return '' if hijos is None else _texto(hijos)


# ---------- datos ----------

def test_opcion_global_primero_en_el_filtro():
    opciones = datos.opciones_filtro_pais()
    assert opciones[0] == {'label': 'Promedio global (tierra firme)', 'value': datos.GLOBAL}
    assert len(opciones) == 233 and len(datos.lista_paises()) == 232     # los países no cambian


def test_serie_global_con_columnas_de_pais():
    s = datos.serie_pais(datos.GLOBAL, 1950, 2000)
    assert list(s.anio) == list(range(1950, 2001))
    real = CSV_GLOBAL.set_index('anio').temp_global_tierra_c
    assert (s.set_index('anio').temp_media_anual_c == real.loc[1950:2000]).all()
    assert s.ref_1951_1980_c.iloc[0] == pytest.approx(real.loc[1951:1980].mean())
    assert datos.serie_pais(datos.GLOBAL).anio.max() == 2012          # como el resto del filtro
    assert datos.anomalias(datos.GLOBAL).empty and datos.mensual_pais(datos.GLOBAL).empty


# ---------- Dashboard ----------

def test_kpis_globales(paginas):
    texto = _texto(paginas['dashboard'].kpis_para(GLOBAL_TODO))
    t = CSV_GLOBAL[CSV_GLOBAL.anio.between(1900, 2012)].temp_global_tierra_c.tolist()
    media = sum(t) / len(t)
    variacion = sum(t[-10:]) / 10 - sum(t[:10]) / 10
    assert f'{media:.2f} °C'.replace('.', ',') in texto
    assert f'+{variacion:.2f} °C'.replace('.', ',') in texto
    assert 'Promedio global (tierra firme) · 1900–2012' in texto
    assert str(len(CSV_ANOM)) in texto and 'en todos los países' in texto


def test_grafica_de_evolucion(paginas):
    fig, titulo, nota = paginas['dashboard'].evolucion(GLOBAL_TODO)
    assert titulo == ' · Promedio global (tierra firme)'
    anual = next(t for t in fig.data if t.name == 'Temperatura anual')
    movil = next(t for t in fig.data if t.name == 'Promedio de 10 años')
    assert list(anual.x) == list(range(1900, 2013))
    ultimos = CSV_GLOBAL[CSV_GLOBAL.anio.between(2003, 2012)].temp_global_tierra_c.mean()
    assert list(movil.y)[-1] == pytest.approx(ultimos)
    _, titulo_pais, nota_pais = paginas['dashboard'].evolucion({'pais': 'Mexico', 'anio_inicio': 1900, 'anio_fin': 2012})
    assert titulo_pais == ' · Mexico' and 'Promedio global' in nota_pais   # sugiere la opción global


def test_evolucion_sin_datos():
    assert figura_evolucion_promedio(datos.serie_pais('Atlantis')).layout.annotations[0].text == \
        'Sin datos en el periodo elegido'


def test_tarjeta_en_el_dashboard(paginas):
    ids = [getattr(c, 'id', None) for c in paginas['dashboard'].layout().children]
    assert 'tarjeta-evolucion' in ids


# ---------- otras páginas ----------

def test_temperaturas_con_global(paginas):
    kpis, fig, nota, barras, _, filas, _ = paginas['temperaturas'].contenido(GLOBAL_TODO)
    assert 'Promedio global (tierra firme)' in nota and len(filas) == 113
    assert filas[0]['incertidumbre'] == '—' and filas[0]['anomalia'] == 'No'
    assert 'Promedio global (tierra firme)' in _texto(barras) and len(barras) == 5


def test_global_y_estaciones_con_global(paginas):
    kpis, fig4, nota4, fig5, nota5 = paginas['global_estaciones'].contenido(GLOBAL_TODO)
    assert [t.name for t in fig4.data] == ['Global terrestre']        # sin línea repetida
    assert 'solo tiene datos anuales' in nota5
    assert 'Anomalía global al inicio' in _texto(kpis)


def test_anomalias_con_global(paginas):
    _, _, nota, filas, _ = paginas['anomalias'].contenido(GLOBAL_TODO, paginas['anomalias'].TODOS)
    assert 'se detectan por país' in nota and len(filas) == len(CSV_ANOM)
