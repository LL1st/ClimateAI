"""Página «Dashboard»: KPIs según los filtros (5.1), mapa mundial por año con selección A/B
(3.1 y 3.2), tarjeta de estimación (4.1), gráfica 3 con casos de ejemplo (4.2) y panel de
comparación de dos países en modo Comparar (6.1) y panel de diagnóstico (7.3)."""
import dash
import dash_bootstrap_components as dbc
from dash import ClientsideFunction, Input, Output, State, callback, clientside_callback, ctx, dcc, html, no_update

import datos
from componentes.formato import num
from componentes.comparacion import cuerpo_comparacion, panel_comparacion
from componentes.diagnostico import panel_diagnostico, registro_inferencia
from componentes.icono import icono
from componentes.kpis import calcular_kpis, fila_kpis
from componentes.mapa import SELECCION_VACIA, elegir_pais, figura_mapa, leyenda_mapa
from componentes.grafica_estimacion import figura_estimacion, figura_evolucion_promedio
from componentes.sidebar import PAIS_INICIAL
from componentes.tarjeta_estimacion import EJEMPLOS, formulario_estimacion, resultado_estimacion
from modelo.inferencia import predecir

NOMBRE = 'Dashboard'
dash.register_page(__name__, path='/', name=NOMBRE, title=f'{NOMBRE} · ClimateAI', order=0)

_NOMBRE_MODELO = {'regresion_lineal': 'regresión lineal', 'random_forest': 'Random Forest'}


def _nombre_modelo():
    elegido = datos.metricas()['modelo_elegido']
    return _NOMBRE_MODELO.get(elegido, elegido)


def subtitulo_estado():
    """Datos y modelo cargados, en una línea bajo el título."""
    m = datos.metricas()
    return html.Div(
        f"Berkeley Earth · {len(datos.lista_paises())} países · {datos.ANIO_MIN}–{datos.ANIO_MAX} · "
        f"modelo: {_nombre_modelo()} (MAE {num(m['resultados'][m['modelo_elegido']]['mae'], 3)} °C a 1 año)",
        className='nota subtitulo-pagina', id='estado-datos-modelo')


# ---------- KPIs (5.1): reaccionan a los filtros globales de país y años ----------

def _filtro(filtros):
    f = filtros or {}
    return (f.get('pais') or PAIS_INICIAL, f.get('anio_inicio', datos.ANIO_MIN), f.get('anio_fin', datos.ANIO_MAX))


def kpis_para(filtros):
    pais, inicio, fin = _filtro(filtros)
    if pais == datos.GLOBAL:
        # el promedio global no tiene anomalías propias: se cuentan las de todos los países
        valores = calcular_kpis(datos.serie_pais(pais, inicio, fin), datos.anomalias(None, inicio, fin))
        return fila_kpis(datos.NOMBRE_GLOBAL, valores, 'Años atípicos en todos los países')
    valores = calcular_kpis(datos.serie_pais(pais, inicio, fin), datos.anomalias(pais, inicio, fin))
    return fila_kpis(pais, valores)


# ---------- Evolución de la temperatura del país filtrado o del promedio global ----------

def tarjeta_evolucion():
    return html.Section([
        html.Div([
            html.Div(icono('termometro', 22), className='tarjeta-encabezado-icono'),
            html.Div([
                html.H2(['Evolución de temperatura', html.Span(id='evol-titulo')], className='titulo-seccion'),
                html.Div(id='evol-nota', className='nota'),
            ]),
        ], className='tarjeta-encabezado'),
        dcc.Graph(id='evol-grafica', config={'displayModeBar': False}),
    ], className='tarjeta mt-3', id='tarjeta-evolucion')


def evolucion(filtros):
    """Serie del país o del promedio global con su promedio móvil de 10 años y la referencia 1951–1980."""
    pais, inicio, fin = _filtro(filtros)
    nombre = datos.nombre_filtro(pais)
    serie = datos.serie_pais(pais, inicio, fin)
    nota = (f'Temperatura media anual · {inicio}–{fin} · línea gruesa: promedio de 10 años · '
            'punteada: promedio de 1951–1980')
    if pais != datos.GLOBAL:
        nota += ' · elige «Promedio global» en el filtro de país para ver el mundo'
    return figura_evolucion_promedio(serie), f' · {nombre}', nota


@callback(Output('evol-grafica', 'figure'), Output('evol-titulo', 'children'), Output('evol-nota', 'children'),
          Input('filtros', 'data'))
def actualizar_evolucion(filtros):
    return evolucion(filtros)


@callback(Output('fila-kpis', 'children'), Input('filtros', 'data'), prevent_initial_call=True)
def actualizar_kpis(filtros):
    return kpis_para(filtros)


def layout():
    return html.Div([
        html.H1(NOMBRE, className='titulo-pagina mb-1'),
        subtitulo_estado(),
        dbc.Row(kpis_para(None), className='g-3 mt-2', id='fila-kpis'),
        dbc.Row([   # como el Figma: mapa a la izquierda y estimación a la derecha (apilados en pantallas angostas)
            dbc.Col(tarjeta_mapa(), xl=8),
            dbc.Col([formulario_estimacion(datos.lista_paises(), datos.ANIO_MAX, _nombre_modelo()),
                     panel_comparacion(datos.lista_paises())], xl=4),
        ], className='g-3 mt-0'),
        tarjeta_evolucion(),
        tarjeta_grafica_estimacion(),
        dcc.Store(id='ultima-inferencia'),   # entrada, salida y tiempo_ms para el panel de diagnóstico (7.3)
        panel_diagnostico(datos.metricas()),
        html.Div(id='dashboard-contenido'),
    ])


# ---------- Tarjeta de estimación (4.1), gráfica 3 y casos de ejemplo (4.2) ----------

def tarjeta_grafica_estimacion():
    return html.Section([
        html.Div([
            html.Div(icono('tendencia', 22), className='tarjeta-encabezado-icono'),
            html.Div([
                html.H2(['Serie histórica y estimación', html.Span(id='est-grafica-pais')], className='titulo-seccion'),
                html.Div('Línea continua: datos históricos · punteada: estimación con su banda ± MAE · '
                         'círculos: valores reales de los años estimados', className='nota'),
            ]),
        ], className='tarjeta-encabezado'),
        dcc.Graph(id='est-grafica', config={'displayModeBar': False}),
    ], className='tarjeta mt-3', id='tarjeta-grafica-estimacion')


def armar_entrada(pais, anio_base, horizonte):
    entrada = {'pais': pais, 'horizonte_anios': int(horizonte) if horizonte is not None else None}
    if anio_base is not None:
        entrada['anio_base'] = int(anio_base)
    return entrada


def estimar(entrada):
    """Llama a predecir() y arma todo lo que se muestra: tarjeta, gráfica, título y registro."""
    r = predecir(entrada)
    if r.get('error') or r.get('prediccion') is None:
        figura, titulo = figura_estimacion(r, None, None), ''
    else:
        historia = datos.serie_pais(r['pais'], anio_fin=r['anio_base'])
        reales = datos.serie_pais(r['pais'], r['anio_base'] + 1, r['anio_objetivo'])
        figura, titulo = figura_estimacion(r, historia, reales), f" · {r['pais']}"
    registro = {'entrada': entrada, 'salida': r, 'tiempo_ms': r.get('tiempo_ms')}
    return resultado_estimacion(r), figura, titulo, registro


_EJEMPLO_POR_ID = {f'ejemplo-{clave}': entrada for clave, _, entrada in EJEMPLOS}


def calcular_desde(disparador, pais, anio_base, horizonte):
    """Lógica del callback, separada para probarla sin Dash. Un ejemplo llena el formulario y calcula."""
    entrada = _EJEMPLO_POR_ID.get(disparador)
    if entrada is None:
        entrada = armar_entrada(pais, anio_base, horizonte)
        formulario = (no_update, no_update, no_update)
    else:
        formulario = (entrada['pais'], entrada['anio_base'], entrada['horizonte_anios'])
    return (*estimar(entrada), *formulario)


@callback(Output('est-resultado', 'children'), Output('est-grafica', 'figure'),
          Output('est-grafica-pais', 'children'), Output('ultima-inferencia', 'data'),
          Output('est-pais', 'value'), Output('est-anio-base', 'value'), Output('est-horizonte', 'value'),
          Input('est-calcular', 'n_clicks'), *[Input(f'ejemplo-{clave}', 'n_clicks') for clave, _, _ in EJEMPLOS],
          State('est-pais', 'value'), State('est-anio-base', 'value'), State('est-horizonte', 'value'))
def calcular_estimacion(_n, *args):
    # se dispara también al abrir la página, para que la tarjeta no aparezca vacía
    pais, anio_base, horizonte = args[-3:]
    return calcular_desde(ctx.triggered_id, pais, anio_base, horizonte)


@callback(Output('est-pais', 'value', allow_duplicate=True), Input('paises-ab', 'data'), prevent_initial_call=True)
def copiar_pais_a(seleccion):
    """El país A elegido en el mapa (3.2) se copia al formulario; no calcula solo."""
    pais = (seleccion or {}).get('a')
    return pais if pais else no_update


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
    ], className='tarjeta tarjeta-mapa', id='tarjeta-mapa')


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


# ---------- Panel de comparación (6.1): sustituye a la estimación en modo Comparar ----------

@callback(Output('tarjeta-estimacion', 'hidden'), Output('tarjeta-grafica-estimacion', 'hidden'),
          Output('tarjeta-comparacion', 'hidden'),
          Output('comp-a', 'value', allow_duplicate=True), Output('comp-b', 'value', allow_duplicate=True),
          Input('mapa-modo', 'value'), State('paises-ab', 'data'), prevent_initial_call='initial_duplicate')
def alternar_panel(modo, seleccion):
    """Cambia entre estimación y comparación. Corre también al dibujarse el Dashboard, y ahí
    llena los selectores A/B con lo que ya estaba elegido (solo usa entradas de esta página)."""
    comparar = modo == 'comparar'
    sel = {**SELECCION_VACIA, **(seleccion or {})}
    return comparar, comparar, not comparar, sel['a'], sel['b']


def sincronizar(disparador, seleccion, valor_a, valor_b):
    """Mapa y selectores A/B muestran lo mismo. Lógica separada para probarla sin Dash.
    Devuelve (nueva selección para el Store, valor del selector A, valor del selector B)."""
    sel = {**SELECCION_VACIA, **(seleccion or {})}
    if disparador in ('comp-a', 'comp-b'):
        nueva = {'a': valor_a, 'b': valor_b if valor_b != valor_a else None}
        if nueva == sel:
            return no_update, no_update, no_update
        return nueva, no_update, (no_update if nueva['b'] == valor_b else nueva['b'])
    return no_update, sel['a'], sel['b']


@callback(Output('paises-ab', 'data', allow_duplicate=True), Output('comp-a', 'value'), Output('comp-b', 'value'),
          Input('paises-ab', 'data'), Input('comp-a', 'value'), Input('comp-b', 'value'),
          prevent_initial_call=True)   # no corre al arrancar: los selectores aún no existen
def sincronizar_selectores(seleccion, valor_a, valor_b):
    return sincronizar(ctx.triggered_id, seleccion, valor_a, valor_b)


def comparar(seleccion, filtros):
    sel = {**SELECCION_VACIA, **(seleccion or {})}
    f = filtros or {}
    inicio, fin = f.get('anio_inicio', datos.ANIO_MIN), f.get('anio_fin', datos.ANIO_MAX)
    serie_a = datos.serie_pais(sel['a'], inicio, fin) if sel['a'] else None
    serie_b = datos.serie_pais(sel['b'], inicio, fin) if sel['b'] else None
    return cuerpo_comparacion(sel['a'], serie_a, sel['b'], serie_b), f'Temperatura media anual · {inicio}–{fin}'


@callback(Output('comp-cuerpo', 'children'), Output('comp-nota', 'children'),
          Input('paises-ab', 'data'), Input('filtros', 'data'))
def actualizar_comparacion(seleccion, filtros):
    return comparar(seleccion, filtros)


# ---------- Panel de diagnóstico (7.3) ----------

@callback(Output('diag-registro', 'children'), Input('ultima-inferencia', 'data'))
def actualizar_diagnostico(registro):
    return registro_inferencia(registro)
