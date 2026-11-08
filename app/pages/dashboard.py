"""Página «Dashboard»: estado de datos y modelo y mapa mundial por año (3.1).
La tarjeta de estimación (4.1) llega en las fases siguientes."""
import dash
import dash_bootstrap_components as dbc
from dash import ClientsideFunction, Input, Output, callback, clientside_callback, dcc, html

import datos
from componentes.formato import num
from componentes.icono import icono
from componentes.mapa import figura_mapa, leyenda_mapa
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
        tarjeta_mapa(),
        html.Div(id='dashboard-contenido'),
    ])


# ---------- Mapa mundial (3.1) ----------

def tarjeta_mapa():
    return html.Section([
        html.Div([
            html.Div(icono('globo', 22), className='tarjeta-encabezado-icono'),
            html.Div([
                html.H2('Mapa mundial de temperatura', className='titulo-seccion'),
                html.Div(['Temperatura media anual por país en ', html.Strong(str(datos.ANIO_MAX), id='mapa-anio-texto'),
                          ' · pasa el mouse sobre los puntos para ver el detalle'], className='nota'),
            ]),
        ], className='tarjeta-encabezado'),
        dcc.Graph(id='mapa', figure=figura_mapa(datos.mapa_anio(datos.ANIO_MAX)),
                  config={'displayModeBar': False, 'scrollZoom': False, 'responsive': True},
                  className='mapa-grafica'),
        dcc.Store(id='mapa-lupa'),
        html.Div([
            html.Label('Año', htmlFor='mapa-anio', className='form-label mb-0'),
            dcc.Slider(id='mapa-anio', min=datos.ANIO_MIN, max=datos.ANIO_MAX, step=1, value=datos.ANIO_MAX,
                       marks={a: str(a) for a in (*range(datos.ANIO_MIN, 1990, 20), datos.ANIO_MAX)},
                       tooltip={'placement': 'bottom'}, className='mapa-deslizador'),
        ], className='mapa-control-anio'),
        leyenda_mapa(),
    ], className='tarjeta tarjeta-mapa mt-3', id='tarjeta-mapa')


@callback(Output('mapa', 'figure'), Output('mapa-anio-texto', 'children'), Input('mapa-anio', 'value'),
          prevent_initial_call=True)   # la figura inicial (2012) ya viene en el layout
def actualizar_mapa(anio):
    anio = int(anio or datos.ANIO_MAX)
    return figura_mapa(datos.mapa_anio(anio)), str(anio)


# Efecto «lupa»: se engancha en el navegador cada vez que cambia la figura (assets/mapa_lupa.js)
clientside_callback(ClientsideFunction(namespace='climateai', function_name='activarLupa'),
                    Output('mapa-lupa', 'data'), Input('mapa', 'figure'))
