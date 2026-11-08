"""Página «Anomalías». El contenido llega en las fases siguientes de PLAN.md."""
import dash
from dash import html

NOMBRE = 'Anomalías'
dash.register_page(__name__, path='/anomalias', name=NOMBRE, title=f'{NOMBRE} · ClimateAI', order=3)

layout = html.Div([
    html.H1(NOMBRE),
    html.Div(id='anomalias-contenido'),
])
