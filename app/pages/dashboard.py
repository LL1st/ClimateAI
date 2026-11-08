"""Página «Dashboard». Por ahora muestra el estado de datos y modelo; el mapa (3.1)
y la tarjeta de estimación (4.1) llegan en las fases siguientes."""
import dash
import dash_bootstrap_components as dbc
from dash import html

import datos
from componentes.formato import num
from componentes.tarjeta_kpi import tarjeta_kpi
from modelo.inferencia import predecir

NOMBRE = 'Dashboard'
dash.register_page(__name__, path='/', name=NOMBRE, title=f'{NOMBRE} · ClimateAI', order=0)

ENTRADA_PRUEBA = {'pais': 'Mexico', 'horizonte_anios': 5}
_NOMBRE_MODELO = {'regresion_lineal': 'regresión lineal', 'random_forest': 'Random Forest'}


def franja_estado():
    """Muestra que los datos y el modelo se cargaron, con una estimación de prueba."""
    m = datos.metricas()
    elegido = m['modelo_elegido']
    r = predecir(ENTRADA_PRUEBA)
    if r.get('error'):
        estimacion = tarjeta_kpi('Estimación de prueba', 'Sin estimación', r['error'],
                                 icono_nombre='alerta', tono='aviso')
    else:
        estimacion = tarjeta_kpi(f"Estimación de prueba · {r['pais']} {r['anio_objetivo']}",
                                 f"{num(r['prediccion'])} °C",
                                 f"± {num(r['mae_modelo'])} °C de error medio (MAE)",
                                 icono_nombre='tendencia', tono='naranja')
    return html.Div([
        dbc.Row([
            dbc.Col(tarjeta_kpi('Datos cargados', f'{len(datos.lista_paises())} países',
                                f'{datos.ANIO_MIN}–{datos.ANIO_MAX} · Berkeley Earth',
                                icono_nombre='globo', tono='azul'), md=4),
            dbc.Col(tarjeta_kpi('Modelo', _NOMBRE_MODELO.get(elegido, elegido),
                                f"MAE {num(m['resultados'][elegido]['mae'], 3)} °C a 1 año",
                                icono_nombre='barras', tono='verde'), md=4),
            dbc.Col(estimacion, md=4),
        ], className='g-3'),
        html.Div(r.get('aviso') or '', className='aviso-estimacion mt-3') if not r.get('error') else None,
    ], id='franja-estado')


def layout():
    # función: se recalcula al abrir la página (predecir tarda ~10 ms)
    return html.Div([
        html.H1(NOMBRE, className='titulo-pagina'),
        franja_estado(),
        html.Div(id='dashboard-contenido'),
    ])
