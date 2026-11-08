"""Página «Anomalías» (tarea 7.2, Figma AF · 5): años atípicos detectados por Isolation Forest.

- KPIs: registros señalados, países con avisos y periodo (según la tabla y el rango de años).
- Gráfica 6: serie del país de la barra lateral con círculos en sus años atípicos.
- Tabla: anomalías del rango de años, de todos los países o de uno (selector propio).
- Recuadro «Cómo interpretar estos avisos».
"""
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dash_table, dcc, html

import datos
from componentes.explorador import figura_evolucion
from componentes.formato import ETIQUETAS_DESPLEGABLE, con_signo, num
from componentes.icono import icono
from componentes.sidebar import PAIS_INICIAL
from componentes.tarjeta_kpi import tarjeta_kpi

NOMBRE = 'Anomalías'
dash.register_page(__name__, path='/anomalias', name=NOMBRE, title=f'{NOMBRE} · ClimateAI', order=3)

TODOS = '__todos__'
COLUMNAS = [
    {'name': 'País', 'id': 'pais'}, {'name': 'Año', 'id': 'anio'}, {'name': 'Variable', 'id': 'variable'},
    {'name': 'Temperatura', 'id': 'temp'}, {'name': 'Frente a su promedio de 5 años', 'id': 'desvio'},
    {'name': 'Motivo del aviso', 'id': 'motivo'}, {'name': 'Estado', 'id': 'estado'},
]
TEXTO_INTERPRETAR = ('Isolation Forest señala observaciones aisladas según los datos y parámetros utilizados. '
                     'El equipo debe revisar el contexto y la calidad de la fuente antes de atribuir significado '
                     'climático.')


def layout():
    opciones = [{'label': 'Todos los países', 'value': TODOS}] + [{'label': p, 'value': p} for p in datos.lista_paises()]
    return html.Div([
        html.H1('Anomalías detectadas', className='titulo-pagina mb-1'),
        html.Div('Revisa observaciones inusuales; una anomalía no implica un desastre.',
                 className='nota subtitulo-pagina'),
        dbc.Row(id='anom-kpis', className='g-3 mt-2'),
        html.Section([
            html.H2('Serie del país con sus años atípicos', className='titulo-seccion'),
            html.Div(id='anom-grafica-nota', className='nota'),
            html.Div([html.Span(className='leyenda-anomalia'), 'Anomalía detectada (Isolation Forest)'],
                     className='nota d-flex align-items-center gap-2 mb-1'),
            dcc.Graph(id='anom-grafica', config={'displayModeBar': False}),
        ], className='tarjeta mt-3'),
        html.Section([
            html.Div([
                html.Div([
                    html.H2('Observaciones atípicas', className='titulo-seccion'),
                    html.Div(id='anom-tabla-nota', className='nota'),
                ], className='flex-grow-1'),
                html.Div([
                    html.Label('País de la tabla', htmlFor='anom-pais', className='form-label mb-1'),
                    dcc.Dropdown(id='anom-pais', options=opciones, value=TODOS, clearable=False,
                                 labels=ETIQUETAS_DESPLEGABLE, persistence=True, persistence_type='session'),
                ], style={'minWidth': 240}),
            ], className='d-flex flex-wrap align-items-end gap-3 mb-2'),
            dash_table.DataTable(
                id='anom-tabla', columns=COLUMNAS, page_size=10, page_action='native', sort_action='native',
                style_as_list_view=True,
                style_header={'backgroundColor': '#F2F4F6', 'fontWeight': 600, 'border': 'none',
                              'color': '#636C77', 'fontSize': 12},
                style_cell={'fontFamily': 'Inter, Segoe UI, sans-serif', 'fontSize': 13, 'padding': '10px 8px',
                            'textAlign': 'left', 'color': '#1F2933', 'borderBottom': '1px solid #E7EAED',
                            'whiteSpace': 'normal', 'height': 'auto'},
                style_data_conditional=[{'if': {'column_id': 'estado'}, 'color': '#B8461F', 'fontWeight': 600}],
            ),
        ], className='tarjeta mt-3'),
        html.Section([
            html.Div([html.Span(icono('alerta', 22), className='text-naranja'),
                      html.H2('Cómo interpretar estos avisos', className='titulo-seccion')],
                     className='d-flex align-items-center gap-2 mb-2'),
            html.P(TEXTO_INTERPRETAR, className='mb-3'),
            html.Span('No predice desastres naturales', className='chip-riesgo chip-riesgo-alto'),
        ], className='tarjeta mt-3', id='anom-interpretar'),
    ])


def motivo(desvio):
    direccion = 'más cálido' if desvio > 0 else 'más frío'
    return f'Año mucho {direccion} que su promedio de los 5 años anteriores'


def filas_anomalias(tabla):
    """Filas de la tabla, de la observación más atípica a la menos atípica."""
    filas = []
    for f in tabla.sort_values('puntaje', ascending=False).itertuples():
        filas.append({
            'pais': f.pais, 'anio': int(f.anio), 'variable': 'Temperatura',
            'temp': f'{num(f.temp_media_anual_c)} °C', 'desvio': f'{con_signo(f.objetivo_cambio_c)} °C',
            'motivo': motivo(f.objetivo_cambio_c), 'estado': 'Revisar',
        })
    return filas


def contenido(filtros, pais_tabla):
    """Todo lo que muestra la página. Separado para probarlo sin Dash."""
    f = filtros or {}
    pais_filtro = f.get('pais') or PAIS_INICIAL
    inicio, fin = f.get('anio_inicio', datos.ANIO_MIN), f.get('anio_fin', datos.ANIO_MAX)
    periodo = f'{inicio}–{fin}'

    tabla = datos.anomalias(None if pais_tabla in (None, TODOS) else pais_tabla, inicio, fin)
    total_registros = int(datos.tabla_pais_anio().anio.between(inicio, fin).sum())
    alcance = 'todos los países' if pais_tabla in (None, TODOS) else pais_tabla
    porcentaje = 100 * len(tabla) / total_registros if total_registros and pais_tabla in (None, TODOS) else None
    kpis = [
        dbc.Col(tarjeta_kpi('Registros señalados', str(len(tabla)),
                            f'{alcance} · {num(porcentaje, 1)} % de los años-país' if porcentaje is not None else alcance,
                            icono_nombre='alerta', tono='naranja'), md=4),
        dbc.Col(tarjeta_kpi('Países con avisos', str(tabla.pais.nunique()), 'con al menos un año atípico',
                            icono_nombre='globo', tono='azul'), md=4),
        dbc.Col(tarjeta_kpi('Periodo', periodo, 'rango de años de la barra lateral', icono_nombre='barras',
                            tono='aviso'), md=4),
    ]
    serie = datos.serie_pais(pais_filtro, inicio, fin)
    an_pais = datos.anomalias(pais_filtro, inicio, fin)
    figura = figura_evolucion(serie, an_pais)
    nota_grafica = f'{pais_filtro} (país de la barra lateral) · {periodo} · {len(an_pais)} años atípicos'
    nota_tabla = f'{alcance} · {periodo} · de la más atípica a la menos atípica'
    return kpis, figura, nota_grafica, filas_anomalias(tabla), nota_tabla


@callback(Output('anom-kpis', 'children'), Output('anom-grafica', 'figure'), Output('anom-grafica-nota', 'children'),
          Output('anom-tabla', 'data'), Output('anom-tabla-nota', 'children'),
          Input('filtros', 'data'), Input('anom-pais', 'value'))
def actualizar(filtros, pais_tabla):
    return contenido(filtros, pais_tabla)
