"""Página «Temperaturas»: explorador de temperaturas (tarea 5.2).
Todo reacciona a los filtros globales de país y rango de años de la barra lateral."""
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dash_table, dcc, html

import datos
from componentes.explorador import (PAISES_REFERENCIA, barra_referencia, figura_evolucion, filas_tabla,
                                    valor_referencia)
from componentes.formato import con_signo, num
from componentes.kpis import calcular_kpis
from componentes.sidebar import PAIS_INICIAL
from componentes.tarjeta_kpi import tarjeta_kpi

NOMBRE = 'Temperaturas'
dash.register_page(__name__, path='/temperaturas', name=NOMBRE, title=f'{NOMBRE} · ClimateAI', order=1)

COLUMNAS = [
    {'name': 'País', 'id': 'pais'}, {'name': 'Año', 'id': 'anio'}, {'name': 'Temperatura', 'id': 'temp'},
    {'name': 'Incertidumbre (°C)', 'id': 'incertidumbre'}, {'name': '¿Anomalía?', 'id': 'anomalia'},
]


def _encabezado(titulo, nota_id, nota=''):
    return html.Div([
        html.H2(titulo, className='titulo-seccion'),
        html.Div(nota, id=nota_id, className='nota'),
    ], className='mb-2')


def layout():
    return html.Div([
        html.H1('Explorador de temperaturas', className='titulo-pagina mb-1'),
        html.Div('Consulta la evolución térmica del país y el periodo elegidos en la barra lateral.',
                 className='nota subtitulo-pagina'),
        dbc.Row(id='temp-kpis', className='g-3 mt-2'),
        dbc.Row([
            dbc.Col(html.Section([
                _encabezado('Evolución histórica de temperatura', 'temp-grafica-nota'),
                html.Div([html.Span(className='leyenda-anomalia'), 'Anomalía detectada (Isolation Forest)'],
                         className='nota d-flex align-items-center gap-2 mb-1'),
                dcc.Graph(id='temp-grafica', config={'displayModeBar': False}),
            ], className='tarjeta h-100'), xl=8),
            dbc.Col(html.Section([
                _encabezado('Resumen de países de referencia', 'temp-referencia-nota'),
                html.Div(id='temp-referencia'),
            ], className='tarjeta h-100'), xl=4),
        ], className='g-3 mt-0'),
        html.Section([
            _encabezado('Registros de temperatura', 'temp-tabla-nota'),
            dash_table.DataTable(
                id='temp-tabla', columns=COLUMNAS, page_size=10, page_action='native', sort_action='native',
                style_as_list_view=True,
                style_header={'backgroundColor': '#F2F4F6', 'fontWeight': 600, 'border': 'none',
                              'color': '#636C77', 'fontSize': 12},
                style_cell={'fontFamily': 'Inter, Segoe UI, sans-serif', 'fontSize': 13, 'padding': '10px 8px',
                            'textAlign': 'left', 'color': '#1F2933', 'borderBottom': '1px solid #E7EAED'},
                style_data_conditional=[{'if': {'filter_query': '{anomalia} = "Sí"', 'column_id': 'anomalia'},
                                         'color': '#B8461F', 'fontWeight': 600}],
            ),
        ], className='tarjeta mt-3'),
    ])


def contenido(filtros):
    """Todo lo que muestra la página para unos filtros. Separado para probarlo sin Dash."""
    f = filtros or {}
    pais = f.get('pais') or PAIS_INICIAL
    inicio, fin = f.get('anio_inicio', datos.ANIO_MIN), f.get('anio_fin', datos.ANIO_MAX)
    serie = datos.serie_pais(pais, inicio, fin)
    anomalias = datos.anomalias(pais, inicio, fin)
    k = calcular_kpis(serie, anomalias)
    periodo = f'{inicio}–{fin}'

    sin = k['media'] is None
    kpis = [
        dbc.Col(tarjeta_kpi('Temperatura media', 'Sin datos' if sin else f"{num(k['media'])} °C",
                            f'{pais} · {periodo}', icono_nombre='termometro', tono='naranja'), md=4),
        dbc.Col(tarjeta_kpi('Variación del periodo', '—' if k['variacion'] is None else f"{con_signo(k['variacion'])} °C",
                            f"Últimos {k['ventana'] or 10} años frente a los primeros {k['ventana'] or 10}",
                            icono_nombre='tendencia', tono='azul'), md=4),
        dbc.Col(tarjeta_kpi('Cobertura temporal', f'{len(serie)} años',
                            f'con datos de los {fin - inicio + 1} del periodo', icono_nombre='barras', tono='verde'),
                md=4),
    ]

    referencia = PAISES_REFERENCIA + ([] if pais in PAISES_REFERENCIA else [pais])
    barras = [barra_referencia(p, *valor_referencia(datos.serie_pais(p, inicio, fin)), fin, destacado=(p == pais))
              for p in referencia]

    filas = filas_tabla(serie, set(anomalias.anio))
    return (kpis, figura_evolucion(serie, anomalias), f'Temperatura media anual · {pais} · {periodo}',
            barras, f'Último año con dato del periodo ({fin})', filas,
            f'{pais} · {periodo} · {len(filas)} registros, {len(anomalias)} con anomalía')


@callback(Output('temp-kpis', 'children'), Output('temp-grafica', 'figure'), Output('temp-grafica-nota', 'children'),
          Output('temp-referencia', 'children'), Output('temp-referencia-nota', 'children'),
          Output('temp-tabla', 'data'), Output('temp-tabla-nota', 'children'),
          Input('filtros', 'data'))
def actualizar(filtros):
    return contenido(filtros)
