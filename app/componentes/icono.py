"""Ícono de línea (SVG en assets/iconos) que toma el color del texto que lo rodea."""
from dash import html


def icono(nombre, tamano=20):
    """nombre: globo, inicio, termometro, barras, alerta, info o tendencia."""
    return html.Span(className=f'icono icono-{nombre}', style={'width': tamano, 'height': tamano},
                     **{'aria-hidden': 'true'})
