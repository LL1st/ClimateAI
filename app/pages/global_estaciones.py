"""Página «Global y estaciones». El contenido llega en las fases siguientes de PLAN.md."""
import dash
from dash import html

NOMBRE = 'Global y estaciones'
dash.register_page(__name__, path='/global-y-estaciones', name=NOMBRE, title=f'{NOMBRE} · ClimateAI', order=2)

layout = html.Div([
    html.H1(NOMBRE),
    html.Div(id='global-contenido'),
])
