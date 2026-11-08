"""Aviso de transparencia: va en todas las páginas (regla 3 de CLAUDE.md)."""
from dash import html

TEXTO_AVISO = ('Las estimaciones se basan en patrones históricos de Berkeley Earth (1900–2012) '
               'y no son pronósticos oficiales.')


def aviso_transparencia():
    return html.Div(
        [html.Strong('ClimateAI es un proyecto académico. '), TEXTO_AVISO],
        id='aviso-transparencia', className='aviso-transparencia', role='note',
        style={'background': '#FFF5DD', 'color': '#7A520C', 'borderRadius': 10, 'padding': '10px 14px',
               'fontSize': 13, 'marginTop': 24},
    )
