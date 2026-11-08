"""Página «Acerca del proyecto». El contenido llega en las fases siguientes de PLAN.md."""
import dash
from dash import html

NOMBRE = 'Acerca del proyecto'
dash.register_page(__name__, path='/acerca', name=NOMBRE, title=f'{NOMBRE} · ClimateAI', order=4)

layout = html.Div([
    html.H1(NOMBRE),
    html.Div(id='acerca-contenido'),
])
