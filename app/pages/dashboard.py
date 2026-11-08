"""Página «Dashboard»: estado de datos y modelo y mapa mundial por año (3.1).
La tarjeta de estimación (4.1) llega en las fases siguientes."""
import dash
import dash_bootstrap_components as dbc
from dash import ClientsideFunction, Input, Output, State, callback, clientside_callback, ctx, dcc, html, no_update

import datos
from componentes.formato import num
from componentes.icono import icono
from componentes.mapa import SELECCION_VACIA, elegir_pais, figura_mapa, leyenda_mapa
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


# ---------- Mapa mundial (3.1) y selección de países A y B (3.2) ----------

MODOS = [{'label': 'Explorar', 'value': 'explorar'}, {'label': 'Comparar', 'value': 'comparar'}]


def tarjeta_mapa():
    return html.Section([
        html.Div([
            html.Div(icono('globo', 22), className='tarjeta-encabezado-icono'),
            html.Div([
                html.H2('Mapa mundial de temperatura', className='titulo-seccion'),
                html.Div(['Temperatura media anual por país en ', html.Strong(str(datos.ANIO_MAX), id='mapa-anio-texto'),
                          ' · cambia a «Comparar» para elegir dos países'], className='nota'),
            ], className='flex-grow-1'),
            dbc.RadioItems(id='mapa-modo', options=MODOS, value='explorar', inline=True,
                           className='selector-modo', inputClassName='btn-check',
                           labelClassName='selector-modo-opcion', labelCheckedClassName='activo',
                           persistence=True, persistence_type='session'),
        ], className='tarjeta-encabezado'),
        html.Div([
            html.Div(id='seleccion-ab-chips', className='d-flex flex-wrap align-items-center gap-3',
                     **{'aria-live': 'polite'}),
            html.Button('Limpiar', id='limpiar-ab', className='btn btn-sm btn-outline-primary ms-auto', disabled=True),
        ], id='seleccion-ab', className='seleccion-ab', hidden=True),
        dcc.Graph(id='mapa', figure=figura_mapa(datos.mapa_anio(datos.ANIO_MAX), posicion=datos.posicion_pais),
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


@callback(Output('mapa', 'figure'), Output('mapa-anio-texto', 'children'),
          Input('mapa-anio', 'value'), Input('paises-ab', 'data'))
def actualizar_mapa(anio, seleccion):
    anio = int(anio or datos.ANIO_MAX)
    return figura_mapa(datos.mapa_anio(anio), seleccion, datos.posicion_pais), str(anio)


_PAISES_VALIDOS = set(datos.lista_paises())


def pais_del_clic(click):
    """Nombre del país del punto clicado, o None si no es un punto de un país con datos."""
    try:
        punto = click['points'][0]
        if punto.get('curveNumber', 0) != 0:          # clic sobre una marca A/B
            return None
        pais = punto['customdata'][0]
    except (TypeError, KeyError, IndexError):
        return None
    return pais if pais in _PAISES_VALIDOS else None


@callback(Output('paises-ab', 'data'), Input('mapa', 'clickData'), Input('limpiar-ab', 'n_clicks'),
          State('mapa-modo', 'value'), State('paises-ab', 'data'), prevent_initial_call=True)
def seleccionar_pais(click, _limpiar, modo, seleccion):
    return nueva_seleccion(ctx.triggered_id, click, modo, seleccion)


def nueva_seleccion(disparador, click, modo, seleccion):
    """Lógica del callback, separada para poder probarla sin Dash."""
    if disparador == 'limpiar-ab':
        return dict(SELECCION_VACIA)
    if modo != 'comparar':
        return no_update
    pais = pais_del_clic(click)
    if pais is None:
        return no_update
    nueva = elegir_pais(seleccion, pais)
    return nueva if nueva != seleccion else no_update


def _chip(clave, pais):
    return html.Span([
        html.Span(clave.upper(), className=f'chip-letra chip-{clave}'),
        html.Span(pais or 'Sin elegir', className='chip-pais' + ('' if pais else ' text-muted')),
    ], className='chip-ab')


@callback(Output('seleccion-ab-chips', 'children'), Output('seleccion-ab', 'hidden'),
          Output('limpiar-ab', 'disabled'), Input('mapa-modo', 'value'), Input('paises-ab', 'data'))
def mostrar_seleccion(modo, seleccion):
    sel = {**SELECCION_VACIA, **(seleccion or {})}
    hay = bool(sel['a'] or sel['b'])
    if modo != 'comparar' and not hay:
        return None, True, True
    if modo != 'comparar':
        ayuda = 'Cambia a «Comparar» para cambiar la selección.'
    elif sel['a'] is None:
        ayuda = 'Haz clic en un país del mapa para elegir A.'
    elif sel['b'] is None:
        ayuda = 'Ahora haz clic en otro país para elegir B.'
    else:
        ayuda = 'Un nuevo clic reemplaza a B.'
    return [_chip('a', sel['a']), _chip('b', sel['b']), html.Span(ayuda, className='nota')], False, not hay


# Efecto «lupa»: se engancha en el navegador cada vez que cambia la figura (assets/mapa_lupa.js)
clientside_callback(ClientsideFunction(namespace='climateai', function_name='activarLupa'),
                    Output('mapa-lupa', 'data'), Input('mapa', 'figure'))
