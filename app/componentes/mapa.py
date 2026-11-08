"""Mapa mundial de temperatura (tarea 3.1): puntos de color por país y año.

El efecto «lupa» al pasar el mouse vive en assets/mapa_lupa.js (corre en el navegador).
"""
import math

import plotly.graph_objects as go
from dash import html

from componentes.formato import num

TAMANO_PUNTO = 5          # px; la lupa en mapa_lupa.js parte de este tamaño

# Clases fijas para todos los años (cerca de los terciles del dataset: 16.6 y 25.6 °C)
CORTE_BAJA, CORTE_ALTA = 15, 25
CLASES = [  # (nombre, color, texto de la leyenda)
    ('Baja', '#42934D', f'Baja (< {CORTE_BAJA} °C)'),
    ('Media', '#E2B64D', f'Media ({CORTE_BAJA}–{CORTE_ALTA} °C)'),
    ('Alta', '#E9683A', f'Alta (> {CORTE_ALTA} °C)'),
    ('Sin datos', '#C9CFD5', 'Sin datos'),
]
_COLOR = {nombre: color for nombre, color, _ in CLASES}


def clase_temperatura(temp):
    if temp is None or (isinstance(temp, float) and math.isnan(temp)):
        return 'Sin datos'
    if temp < CORTE_BAJA:
        return 'Baja'
    return 'Media' if temp <= CORTE_ALTA else 'Alta'


def _textos(df):
    clases = [clase_temperatura(t) for t in df.temp]
    colores = [_COLOR[c] for c in clases]
    custom = [[pais or 'Sin nombre', 'Sin datos' if c == 'Sin datos' else f'{num(t)} °C', c]
              for pais, t, c in zip(df.pais, df.temp, clases)]
    return colores, custom


_TOOLTIP = '<b>%{customdata[0]}</b><br>%{customdata[1]} · %{customdata[2]}<extra></extra>'


def figura_mapa(df):
    """df de datos.mapa_anio(). Con lat/lon dibuja puntos; si no, coroplético de respaldo."""
    if 'lat' not in df.columns:
        return figura_coropletica(df)
    colores, custom = _textos(df)
    fig = go.Figure(go.Scattergeo(
        lat=df.lat, lon=df.lon, mode='markers', customdata=custom, hovertemplate=_TOOLTIP,
        marker=dict(size=[TAMANO_PUNTO] * len(df), color=colores, line=dict(width=0), opacity=1),
    ))
    return _estilo(fig)


def figura_coropletica(df):
    colores, custom = _textos(df)
    indice = {nombre: i for i, (nombre, _, _) in enumerate(CLASES)}
    z = [indice[c[2]] for c in custom]
    n = len(CLASES) - 1
    escala = [[i / n, color] for i, (_, color, _) in enumerate(CLASES)]
    fig = go.Figure(go.Choropleth(
        locations=df.iso3, z=z, zmin=0, zmax=n, colorscale=escala, showscale=False,
        customdata=custom, hovertemplate=_TOOLTIP, marker_line_color='#FFFFFF', marker_line_width=0.5,
    ))
    return _estilo(fig)


def _estilo(fig):
    fig.update_geos(
        projection_type='natural earth', showframe=False, showcoastlines=False, showcountries=False,
        showland=False, showocean=False, showlakes=False, bgcolor='rgba(0,0,0,0)',
        lataxis_range=[-58, 85],
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0), autosize=True, paper_bgcolor='rgba(0,0,0,0)', dragmode=False,
        hoverlabel=dict(bgcolor='#FFFFFF', bordercolor='#E7EAED', font=dict(family='Inter, Segoe UI, sans-serif',
                                                                             size=12, color='#1F2933')),
        uirevision='mapa',   # conserva el estado de la vista al cambiar de año
    )
    return fig


def leyenda_mapa():
    return html.Div([
        html.Span('Leyenda del mapa', className='mapa-leyenda-titulo'),
        *[html.Span([html.Span(className='mapa-leyenda-punto', style={'background': color}), texto],
                    className='mapa-leyenda-item') for _, color, texto in CLASES],
    ], className='mapa-leyenda')
