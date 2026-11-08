"""Barra lateral: logo, menú de páginas y filtros globales de país y años."""
import dash_bootstrap_components as dbc
from dash import dcc, html

import datos

PAIS_INICIAL = 'Mexico'

MENU = [('Dashboard', '/'), ('Temperaturas', '/temperaturas'),
        ('Global y estaciones', '/global-y-estaciones'), ('Anomalías', '/anomalias')]


def sidebar():
    return html.Aside([
        html.Div('ClimateAI', className='sidebar-logo', style={'fontWeight': 700, 'fontSize': 22, 'marginBottom': 24}),
        dbc.Nav([dbc.NavLink(nombre, href=ruta, active='exact') for nombre, ruta in MENU],
                vertical=True, pills=True, id='menu'),
        html.Hr(),
        html.Div([
            html.Label('País', htmlFor='filtro-pais', className='form-label'),
            dcc.Dropdown(id='filtro-pais', options=datos.lista_paises(), value=PAIS_INICIAL,
                         clearable=False, persistence=True, persistence_type='session'),
            html.Label('Rango de años', htmlFor='filtro-anios', className='form-label mt-3'),
            dcc.RangeSlider(id='filtro-anios', min=datos.ANIO_MIN, max=datos.ANIO_MAX, step=1,
                            value=[datos.ANIO_MIN, datos.ANIO_MAX],
                            marks={a: str(a) for a in (datos.ANIO_MIN, 1950, datos.ANIO_MAX)},
                            tooltip={'placement': 'bottom'}, persistence=True, persistence_type='session'),
        ], id='filtros-globales'),
        html.Div(dbc.Nav([dbc.NavLink('Acerca del proyecto', href='/acerca', active='exact')],
                         vertical=True, pills=True), style={'marginTop': 'auto'}),
    ], id='sidebar', className='sidebar',
        style={'width': 244, 'minWidth': 244, 'minHeight': '100vh', 'background': '#FFFFFF',
               'borderRight': '1px solid #E7EAED', 'padding': 20, 'display': 'flex', 'flexDirection': 'column'})
