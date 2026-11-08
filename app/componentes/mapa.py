"""Mapa mundial de temperatura (tarea 3.1): puntos de color por país y año.

El efecto «lupa» al pasar el mouse vive en assets/mapa_lupa.js (corre en el navegador).
"""
import math

import plotly.graph_objects as go
from dash import html

from componentes.formato import num

TAMANO_PUNTO = 5          # px inicial; mapa_lupa.js lo ajusta al ancho real del mapa
FACTOR_CHICO = 0.55       # puntos de relleno (países pequeños): más chicos que los de la cuadrícula
PASO_GRADOS = 4           # separación de la cuadrícula (scripts/generar_puntos_mapa.py)

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


# Países A y B del modo Comparar (tarea 3.2): la letra acompaña al color (regla 5)
COLOR_AB = {'a': '#B8461F', 'b': '#2E75A9'}   # tonos oscuros: la letra blanca cumple contraste 4.5:1
SELECCION_VACIA = {'a': None, 'b': None}


def elegir_pais(seleccion, pais):
    """Regla de clics en modo Comparar: el 1.º elige A, el 2.º elige B y desde el 3.º se reemplaza B.
    Hacer clic otra vez en A no cambia nada."""
    sel = {**SELECCION_VACIA, **(seleccion or {})}
    if not pais or pais == sel['a'] or pais == sel['b']:
        return sel
    if sel['a'] is None:
        sel['a'] = pais
    else:
        sel['b'] = pais
    return sel


def _marcas_ab(seleccion, posicion):
    """Traza con un círculo y la letra de cada país elegido. posicion: pais -> (lat, lon)."""
    lat, lon, texto, color = [], [], [], []
    for clave in ('a', 'b'):
        pais = (seleccion or {}).get(clave)
        pos = posicion(pais) if pais else None
        if pos:
            lat.append(pos[0]); lon.append(pos[1]); texto.append(f'<b>{clave.upper()}</b>'); color.append(COLOR_AB[clave])
    # Insignia rellena con la letra blanca adentro (como los chips de la barra de selección)
    return go.Scattergeo(
        lat=lat, lon=lon, mode='markers+text', text=texto, textposition='middle center',
        textfont=dict(size=12, color='#FFFFFF', family='Inter, Segoe UI, sans-serif'),
        marker=dict(symbol='circle', size=22, color=color, line=dict(width=2, color='#FFFFFF')),
        hoverinfo='skip', showlegend=False, name='seleccion',
    )


def figura_mapa(df, seleccion=None, posicion=None):
    """df de datos.mapa_anio(). Con lat/lon dibuja puntos; si no, coroplético de respaldo.
    seleccion {'a', 'b'} y posicion(pais) -> (lat, lon) agregan las marcas A y B."""
    if 'lat' not in df.columns:
        return figura_coropletica(df)
    colores, custom = _textos(df)
    factores = [FACTOR_CHICO if r else 1 for r in df.get('relleno', [0] * len(df))]
    fig = go.Figure(go.Scattergeo(
        lat=df.lat, lon=df.lon, mode='markers', customdata=custom, hovertemplate=_TOOLTIP,
        marker=dict(size=[TAMANO_PUNTO * f for f in factores], color=colores, line=dict(width=0), opacity=1),
    ))
    if posicion is not None:
        fig.add_trace(_marcas_ab(seleccion, posicion))        # traza 1; la lupa solo toca la traza 0
    fig.update_layout(meta={'paso': PASO_GRADOS, 'factores': factores})   # lo lee mapa_lupa.js
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
        projection_type='equirectangular',   # filas rectas, estilo «dot matrix»
        showframe=False, showcoastlines=False, showcountries=False,
        showland=False, showocean=False, showlakes=False, bgcolor='rgba(0,0,0,0)',
        lataxis_range=[-58, 84], lonaxis_range=[-180, 180],
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0), autosize=True, paper_bgcolor='rgba(0,0,0,0)', dragmode=False,
        showlegend=False,   # la leyenda es propia (leyenda_mapa)
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
