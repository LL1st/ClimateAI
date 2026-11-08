"""Pruebas de los estilos y la tarjeta KPI (tarea 1.3)."""
import os
import re

import pytest

from componentes.tarjeta_kpi import tarjeta_kpi

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS = open(os.path.join(RAIZ, 'assets', 'style.css'), encoding='utf-8').read()


@pytest.mark.parametrize('color', ['#E9683A', '#B8461F', '#2E75A9', '#42934D', '#E2B64D', '#1F2933',
                                   '#6B7580', '#F2F4F6', '#E7EAED', '#7A520C', '#FFF5DD'])
def test_tokens_de_claude_md_en_el_css(color):
    assert color.lower() in CSS.lower()


def test_no_se_usa_el_gris_sin_contraste():
    assert '#87919b' not in re.sub(r'/\*.*?\*/', '', CSS, flags=re.S).lower()


def test_los_iconos_del_css_existen():
    for nombre in re.findall(r"url\('iconos/([a-z]+\.svg)'\)", CSS):
        assert os.path.exists(os.path.join(RAIZ, 'assets', 'iconos', nombre)), nombre


def test_tarjeta_kpi_tiene_titulo_valor_y_nota():
    t = tarjeta_kpi('Temperatura media', '14,2 °C', 'Promedio del periodo', icono_nombre='termometro', id='kpi-1')
    assert t.id == 'kpi-1' and 'tarjeta-kpi' in t.className
    texto = t.children[-1].children
    assert [c.children for c in texto] == ['Temperatura media', '14,2 °C', 'Promedio del periodo']


def test_tarjeta_kpi_sin_nota_ni_icono():
    t = tarjeta_kpi('Anomalías', '18')
    assert len(t.children) == 1 and len(t.children[0].children) == 2


def test_tarjeta_kpi_rechaza_tono_desconocido():
    with pytest.raises(ValueError):
        tarjeta_kpi('X', '1', tono='morado')
