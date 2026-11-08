"""Tarjeta KPI del Figma (AF · 1): ícono en cuadro de color, título, valor grande y nota."""
from dash import html

from componentes.icono import icono

TONOS = {'naranja', 'azul', 'verde', 'aviso'}


def tarjeta_kpi(titulo, valor, nota=None, icono_nombre=None, tono='naranja', id=None):
    if tono not in TONOS:
        raise ValueError(f'tono debe ser uno de {sorted(TONOS)}')
    partes = []
    if icono_nombre:
        partes.append(html.Div(icono(icono_nombre), className=f'kpi-icono tono-{tono}'))
    texto = [html.Div(titulo, className='kpi-titulo'), html.Div(valor, className='kpi-valor')]
    if nota:
        texto.append(html.Div(nota, className='kpi-nota'))
    partes.append(html.Div(texto, style={'minWidth': 0}))
    props = {'id': id} if id else {}
    return html.Div(partes, className='tarjeta tarjeta-kpi', **props)
