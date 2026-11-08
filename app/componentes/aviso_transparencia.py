"""Aviso de transparencia: va en todas las páginas (regla 3 de CLAUDE.md)."""
from dash import html

from componentes.icono import icono

TITULO_AVISO = 'ClimateAI es un proyecto académico.'
TEXTO_AVISO = ('Las estimaciones se basan en patrones históricos de Berkeley Earth (1900–2012) '
               'y no son pronósticos oficiales.')


def aviso_transparencia():
    return html.Div([
        html.Div(icono('info', 18), className='aviso-transparencia-icono'),
        html.Div([
            html.Div(TITULO_AVISO, className='aviso-transparencia-titulo'),
            html.Div(TEXTO_AVISO, className='aviso-transparencia-texto'),
        ]),
    ], id='aviso-transparencia', className='tarjeta aviso-transparencia', role='note')
