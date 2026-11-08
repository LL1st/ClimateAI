"""Pruebas de la fila de KPIs del Dashboard (tarea 5.1)."""
import importlib.util
import os
import sys

import pytest

import datos
from componentes.kpis import calcular_kpis, fila_kpis

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = datos.tabla_pais_anio()


@pytest.fixture(scope='module')
def dashboard():
    nombre = 'climateai_app'
    if nombre not in sys.modules:
        spec = importlib.util.spec_from_file_location(nombre, os.path.join(RAIZ, 'app', 'app.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[nombre] = mod
        spec.loader.exec_module(mod)
    return sys.modules['pages.dashboard']


def _kpis(pais, inicio, fin):
    return calcular_kpis(datos.serie_pais(pais, inicio, fin), datos.anomalias(pais, inicio, fin))


@pytest.mark.parametrize('pais, inicio, fin', [('Mexico', 1900, 2012), ('Canada', 1950, 2000), ('India', 1990, 2012)])
def test_valores_coinciden_con_un_calculo_a_mano(pais, inicio, fin):
    d = CSV[(CSV.pais == pais) & CSV.anio.between(inicio, fin)].sort_values('anio')
    k = _kpis(pais, inicio, fin)
    assert k['media'] == pytest.approx(d.temp_media_anual_c.mean())
    t = d.temp_media_anual_c.tolist()
    assert k['variacion'] == pytest.approx(sum(t[-10:]) / 10 - sum(t[:10]) / 10)
    assert k['cambio_ref'] == pytest.approx(d.temp_media_anual_c.mean() - d.ref_1951_1980_c.iloc[0])
    an = datos.anomalias()
    assert k['anomalias'] == len(an[(an.pais == pais) & an.anio.between(inicio, fin)])


def test_periodo_corto_usa_mitades():
    k = _kpis('Mexico', 2000, 2005)          # 6 años: compara los últimos 3 con los primeros 3
    assert k['ventana'] == 3


def test_periodo_sin_datos_no_rompe():
    # Heard Island empieza en 1948
    k = _kpis('Heard Island And Mcdonald Islands', 1900, 1940)
    assert k['media'] is None and k['anomalias'] == 0
    columnas = fila_kpis('Heard Island And Mcdonald Islands', k)
    assert len(columnas) == 4
    assert columnas[0].children.children[-1].children[1].children == 'Sin datos'


def test_fila_tiene_cuatro_kpis_con_formato():
    columnas = fila_kpis('Mexico', _kpis('Mexico', 1900, 2012))
    ids = [c.children.id for c in columnas]
    assert ids == ['kpi-media', 'kpi-variacion', 'kpi-cambio', 'kpi-anomalias']
    valor_media = columnas[0].children.children[-1].children[1].children
    assert valor_media.endswith(' °C') and ',' in valor_media
    assert columnas[1].children.children[-1].children[1].children[0] in '+−'


def test_kpis_reaccionan_a_los_filtros(dashboard):
    a = dashboard.actualizar_kpis({'pais': 'Mexico', 'anio_inicio': 1900, 'anio_fin': 2012})
    b = dashboard.actualizar_kpis({'pais': 'Canada', 'anio_inicio': 1950, 'anio_fin': 2000})
    nota = lambda fila: fila[0].children.children[-1].children[2].children
    assert nota(a) == 'Mexico · 1900–2012' and nota(b) == 'Canada · 1950–2000'
