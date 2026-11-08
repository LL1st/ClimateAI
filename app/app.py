"""Punto de entrada de ClimateAI. Uso: python app/app.py  (abre http://127.0.0.1:8050)"""
import os
import sys

_APP = os.path.dirname(os.path.abspath(__file__))
_RAIZ = os.path.dirname(_APP)
for _ruta in (_APP, _RAIZ):           # app/ para `import datos`; raíz para `from modelo.inferencia import predecir`
    if _ruta not in sys.path:
        sys.path.insert(0, _ruta)

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dcc, html

import datos                                      # noqa: E402  carga única de los datos
from modelo.inferencia import predecir            # noqa: E402,F401  carga única del modelo (falla al arrancar si algo falta)
from componentes.aviso_transparencia import aviso_transparencia
from componentes.sidebar import sidebar

# Inter desde Google Fonts; sin internet se usa Segoe UI / system-ui (ver assets/style.css)
FUENTE_INTER = 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap'

app = dash.Dash(
    __name__,
    use_pages=True,
    pages_folder=os.path.join(_APP, 'pages'),
    assets_folder=os.path.join(_RAIZ, 'assets'),
    external_stylesheets=[dbc.themes.BOOTSTRAP, FUENTE_INTER],
    title='ClimateAI',
)

app.layout = html.Div([
    dcc.Store(id='filtros'),
    sidebar(),
    html.Main([dash.page_container, aviso_transparencia()], className='contenido'),
], className='app-contenedor')


def armar_filtros(pais, rango):
    """Filtros globales que leen todas las páginas: {"pais", "anio_inicio", "anio_fin"}."""
    inicio, fin = rango or (datos.ANIO_MIN, datos.ANIO_MAX)
    return {'pais': pais, 'anio_inicio': int(inicio), 'anio_fin': int(fin)}


callback(Output('filtros', 'data'), Input('filtro-pais', 'value'), Input('filtro-anios', 'value'))(armar_filtros)

if __name__ == '__main__':
    app.run(debug=True)
