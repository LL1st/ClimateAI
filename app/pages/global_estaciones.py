"""Página «Global y estaciones» (tarea 5.3): anomalía del país frente a la global terrestre
(gráfica 4) y mapa de calor de anomalías mensuales (gráfica 5). Sin diseño propio en el Figma:
usa el estilo del explorador de temperaturas. Reacciona a los filtros globales."""
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dcc, html

import datos
from componentes.anomalias_clima import (MESES, anomalia_global, anomalia_mensual, anomalia_pais,
                                         figura_anomalias, figura_estacional)
from componentes.formato import con_signo
from componentes.sidebar import PAIS_INICIAL
from componentes.tarjeta_kpi import tarjeta_kpi

NOMBRE = 'Global y estaciones'
dash.register_page(__name__, path='/global-y-estaciones', name=NOMBRE, title=f'{NOMBRE} · ClimateAI', order=2)

_GLOBAL = datos.serie_global()   # serie completa (1900–2015); la referencia 1951–1980 sale de aquí


def _tarjeta(titulo, nota_id, grafica_id, nota_fija):
    return html.Section([
        html.H2(titulo, className='titulo-seccion'),
        html.Div(id=nota_id, className='nota'),
        html.Div(nota_fija, className='nota mb-1'),
        dcc.Graph(id=grafica_id, config={'displayModeBar': False}),
    ], className='tarjeta mt-3')


def layout():
    return html.Div([
        html.H1(NOMBRE, className='titulo-pagina mb-1'),
        html.Div('Compara el calentamiento del país con el de toda la tierra firme y mira en qué meses ocurre. '
                 'Todas las anomalías son frente al promedio de 1951–1980.', className='nota subtitulo-pagina'),
        dbc.Row(id='global-kpis', className='g-3 mt-2'),
        _tarjeta('Anomalía del país frente a la global terrestre', 'global-nota-4', 'global-grafica-4',
                 'Línea continua: el país · punteada: promedio de toda la tierra firme'),
        _tarjeta('Anomalías por mes y año', 'global-nota-5', 'global-grafica-5',
                 'Azul: más frío que su promedio de 1951–1980 · rojo: más cálido'),
    ])


def _ultimos(df, n=10):
    d = df.dropna(subset=['anomalia']).sort_values('anio').tail(n)
    return (None, 0) if d.empty else (float(d.anomalia.mean()), len(d))


def contenido(filtros):
    """Todo lo que muestra la página para unos filtros. Separado para probarlo sin Dash."""
    f = filtros or {}
    pais = f.get('pais') or PAIS_INICIAL
    inicio, fin = f.get('anio_inicio', datos.ANIO_MIN), f.get('anio_fin', datos.ANIO_MAX)

    es_global = pais == datos.GLOBAL
    nombre = datos.nombre_filtro(pais)
    # con «Promedio global» la línea del país sería la misma que la global: solo se dibuja la global
    serie = datos.serie_pais(pais, inicio, fin)
    an_pais = anomalia_pais(serie.iloc[0:0] if es_global else serie)
    an_global = anomalia_global(_GLOBAL, inicio, fin)
    tabla = anomalia_mensual(datos.mensual_pais(pais), inicio, fin)

    media_global, n_global = _ultimos(an_global)
    por_mes = tabla.mean(axis=1).dropna()
    if por_mes.empty:
        mes_valor = '—'
        mes_nota = 'El promedio global solo tiene datos anuales' if es_global else 'Sin datos mensuales'
    else:
        mes_valor = MESES[int(por_mes.idxmax()) - 1]
        mes_nota = f'{con_signo(float(por_mes.max()))} °C en promedio · {pais}'
    if es_global:   # primera tarjeta: cómo empezó el periodo, para ver el cambio frente a la segunda
        d = an_global.dropna(subset=['anomalia']).sort_values('anio').head(10)
        media_1, n_1 = (float(d.anomalia.mean()), len(d)) if not d.empty else (None, 0)
        kpi_1 = tarjeta_kpi('Anomalía global al inicio', '—' if media_1 is None else f'{con_signo(media_1)} °C',
                            f'Promedio de los primeros {n_1} años del periodo', icono_nombre='termometro', tono='naranja')
    else:
        media_pais, n_pais = _ultimos(an_pais)
        kpi_1 = tarjeta_kpi(f'Anomalía de {pais}', '—' if media_pais is None else f'{con_signo(media_pais)} °C',
                            f'Promedio de los últimos {n_pais} años del periodo', icono_nombre='termometro',
                            tono='naranja')
    kpis = [
        dbc.Col(kpi_1, md=4),
        dbc.Col(tarjeta_kpi('Anomalía global terrestre', '—' if media_global is None else f'{con_signo(media_global)} °C',
                            f'Promedio de los últimos {n_global} años del periodo', icono_nombre='globo',
                            tono='azul'), md=4),
        dbc.Col(tarjeta_kpi('Mes más cálido frente a lo normal', mes_valor, mes_nota, icono_nombre='barras',
                            tono='aviso'), md=4),
    ]
    periodo = f'{inicio}–{fin}'
    nota_5 = ('El promedio global solo tiene datos anuales: elige un país para ver los meses'
              if es_global else f'{pais} · {periodo} · cada celda es un mes')
    return (kpis, figura_anomalias(nombre, an_pais, an_global), f'{nombre} · {periodo}',
            figura_estacional(tabla), nota_5)


@callback(Output('global-kpis', 'children'), Output('global-grafica-4', 'figure'), Output('global-nota-4', 'children'),
          Output('global-grafica-5', 'figure'), Output('global-nota-5', 'children'), Input('filtros', 'data'))
def actualizar(filtros):
    return contenido(filtros)
