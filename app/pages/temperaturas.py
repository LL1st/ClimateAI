"""Página «Temperaturas». El contenido llega en las fases siguientes de PLAN.md."""
import dash
from dash import html

NOMBRE = 'Temperaturas'
dash.register_page(__name__, path='/temperaturas', name=NOMBRE, title=f'{NOMBRE} · ClimateAI', order=1)

layout = html.Div([
    html.H1(NOMBRE),
    html.Div(id='temperaturas-contenido'),
])
