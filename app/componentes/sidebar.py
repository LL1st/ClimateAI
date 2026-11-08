"""Barra lateral: logo, menú de páginas, filtros globales y pie con "Acerca del proyecto"."""
import dash_bootstrap_components as dbc
from dash import dcc, html

import datos
from componentes.formato import ETIQUETAS_DESPLEGABLE
from componentes.icono import icono

PAIS_INICIAL = 'Mexico'

MENU = [('Dashboard', '/', 'inicio'), ('Temperaturas', '/temperaturas', 'termometro'),
        ('Global y estaciones', '/global-y-estaciones', 'barras'), ('Anomalías', '/anomalias', 'alerta')]


def _enlace(nombre, ruta, nombre_icono):
    return dbc.NavLink([icono(nombre_icono), html.Span(nombre)], href=ruta, active='exact')


def sidebar():
    return html.Aside([
        html.Div([
            html.Div(icono('globo', 22), className='sidebar-logo-icono'),
            html.Div([html.Div('ClimateAI', className='sidebar-logo-nombre'),
                      html.Div('Análisis climático con IA', className='sidebar-logo-sub')]),
        ], className='sidebar-logo'),

        html.Div('Análisis', className='sidebar-etiqueta'),
        dbc.Nav([_enlace(*m) for m in MENU], vertical=True, pills=True, id='menu'),
        html.Hr(className='sidebar-separador'),

        html.Div('Filtros', className='sidebar-etiqueta'),
        html.Div([
            html.Label('País', htmlFor='filtro-pais', className='form-label'),
            dcc.Dropdown(id='filtro-pais', options=datos.lista_paises(), value=PAIS_INICIAL,
                         clearable=False, persistence=True, persistence_type='session',
                         labels=ETIQUETAS_DESPLEGABLE),
            html.Label('Rango de años', htmlFor='filtro-anios', className='form-label mt-3'),
            dcc.RangeSlider(id='filtro-anios', min=datos.ANIO_MIN, max=datos.ANIO_MAX, step=1,
                            value=[datos.ANIO_MIN, datos.ANIO_MAX],
                            marks={a: str(a) for a in (datos.ANIO_MIN, 1950, datos.ANIO_MAX)},
                            tooltip={'placement': 'bottom'}, persistence=True, persistence_type='session'),
        ], id='filtros-globales', className='sidebar-filtros'),

        html.Div([
            dbc.Nav([_enlace('Acerca del proyecto', '/acerca', 'info')], vertical=True, pills=True),
            html.Hr(className='sidebar-separador'),
            html.Div([
                html.Div('CA', className='sidebar-equipo-avatar', **{'aria-hidden': 'true'}),
                html.Div([html.Div('Equipo ClimateAI', className='sidebar-equipo-nombre'),
                          html.Div('Proyecto académico · UT Cancún', className='nota')]),
            ], className='sidebar-equipo'),
        ], className='sidebar-pie'),
    ], id='sidebar', className='sidebar')
