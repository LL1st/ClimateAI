"""Página «Dashboard». Por ahora muestra el estado de datos y modelo; el mapa (3.1)
y la tarjeta de estimación (4.1) llegan en las fases siguientes."""
import dash
import dash_bootstrap_components as dbc
from dash import html

import datos
from componentes.formato import num
from modelo.inferencia import predecir

NOMBRE = 'Dashboard'
dash.register_page(__name__, path='/', name=NOMBRE, title=f'{NOMBRE} · ClimateAI', order=0)

ENTRADA_PRUEBA = {'pais': 'Mexico', 'horizonte_anios': 5}
_NOMBRE_MODELO = {'regresion_lineal': 'regresión lineal', 'random_forest': 'Random Forest'}


def _tarjeta(titulo, valor, nota):
    return dbc.Col(dbc.Card(dbc.CardBody([
        html.Div(titulo, className='text-muted small'),
        html.Div(valor, className='fs-4 fw-bold'),
        html.Div(nota, className='small'),
    ])), md=4)


def franja_estado():
    """Muestra que los datos y el modelo se cargaron, con una estimación de prueba."""
    m = datos.metricas()
    elegido = m['modelo_elegido']
    r = predecir(ENTRADA_PRUEBA)
    if r.get('error'):
        estimacion = _tarjeta('Estimación de prueba', 'Sin estimación', r['error'])
    else:
        estimacion = _tarjeta(
            f"Estimación de prueba · {r['pais']} {r['anio_objetivo']}",
            f"{num(r['prediccion'])} °C ± {num(r['mae_modelo'])} °C",
            r['aviso'])
    return dbc.Row([
        _tarjeta('Datos cargados', f'{len(datos.lista_paises())} países',
                 f'{datos.ANIO_MIN}–{datos.ANIO_MAX} · Berkeley Earth'),
        _tarjeta('Modelo', _NOMBRE_MODELO.get(elegido, elegido),
                 f"MAE {num(m['resultados'][elegido]['mae'], 3)} °C a 1 año"),
        estimacion,
    ], className='g-3', id='franja-estado')


def layout():
    # función: se recalcula al abrir la página (predecir tarda ~10 ms)
    return html.Div([
        html.H1(NOMBRE),
        franja_estado(),
        html.Div(id='dashboard-contenido'),
    ])
