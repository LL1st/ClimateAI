"""Panel de comparación de dos países (tarea 6.1, Figma AF · 2).

- Diferencia A − B: promedio de A menos promedio de B en los años del periodo que ambos tienen.
- Cambio en A / en B: igual que el KPI «Variación del periodo» (últimos 10 años frente a los
  primeros 10 del periodo), para que las cifras coincidan en todo el Dashboard.
"""
import plotly.graph_objects as go
from dash import dcc, html

from componentes.formato import ETIQUETAS_DESPLEGABLE, con_signo, num
from componentes.kpis import calcular_kpis
from componentes.mapa import COLOR_AB

_FUENTE = dict(family='Inter, Segoe UI, sans-serif', size=12, color='#1F2933')


def panel_comparacion(paises):
    def selector(clave):
        return html.Div([
            html.Span(clave.upper(), className=f'chip-letra chip-{clave}', **{'aria-hidden': 'true'}),
            dcc.Dropdown(id=f'comp-{clave}', options=paises, placeholder=f'País {clave.upper()}',
                         labels=ETIQUETAS_DESPLEGABLE, className='flex-grow-1'),
        ], className='d-flex align-items-center gap-2 flex-grow-1', title=f'País {clave.upper()}')

    return html.Section([
        html.Div([
            html.H2('Comparación', className='titulo-seccion'),
            html.Div(id='comp-nota', className='nota'),
        ], className='mb-2'),
        html.Div([selector('a'), selector('b')], className='d-flex gap-2'),
        html.Div(id='comp-cuerpo', className='mt-3'),
    ], className='tarjeta tarjeta-comparacion', id='tarjeta-comparacion', hidden=True)


def resumen_comparacion(serie_a, serie_b):
    """Diferencia A − B (años comunes) y cambio de cada país en el periodo."""
    comunes = serie_a.merge(serie_b, on='anio', suffixes=('_a', '_b'))
    diferencia = None
    if not comunes.empty:
        diferencia = float(comunes.temp_media_anual_c_a.mean() - comunes.temp_media_anual_c_b.mean())
    return {
        'diferencia': diferencia,
        'anios_comunes': len(comunes),
        'cambio_a': calcular_kpis(serie_a, serie_a.iloc[0:0])['variacion'],
        'cambio_b': calcular_kpis(serie_b, serie_b.iloc[0:0])['variacion'],
    }


def figura_comparacion(pais_a, serie_a, pais_b, serie_b):
    """Gráfica 2: A naranja continua y B azul punteada, con el último valor de cada una."""
    fig = go.Figure()
    for clave, pais, serie, trazo in (('a', pais_a, serie_a, 'solid'), ('b', pais_b, serie_b, 'dash')):
        if serie.empty:
            continue
        color = COLOR_AB[clave]
        fig.add_trace(go.Scatter(x=serie.anio, y=serie.temp_media_anual_c, mode='lines',
                                 name=f'{clave.upper()} · {pais}', line=dict(color=color, width=2, dash=trazo),
                                 hovertemplate='%{x}: %{y:.2f} °C<extra>' + f'{clave.upper()} · {pais}</extra>'))
        ultimo = serie.sort_values('anio').iloc[-1]
        fig.add_annotation(x=ultimo.anio, y=ultimo.temp_media_anual_c, text=f'{num(ultimo.temp_media_anual_c, 1)} °C',
                           showarrow=False, xanchor='left', xshift=4, font=dict(size=11, color=color))
    fig.update_layout(height=230, margin=dict(l=40, r=48, t=8, b=28), paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)', font=_FUENTE, separators=',.', hovermode='x unified',
                      legend=dict(orientation='h', yanchor='bottom', y=1.0, xanchor='left', x=0, font=dict(size=11)))
    fig.update_xaxes(showgrid=False, linecolor='#E7EAED', tickformat='d')
    fig.update_yaxes(gridcolor='#EEF0F2', zeroline=False, title_text='°C')
    return fig


def tarjetas_comparacion(r):
    def mini(titulo, valor, clase=''):
        return html.Div([html.Div(titulo, className='kpi-titulo'), html.Div(valor, className=f'comp-valor {clase}')],
                        className='comp-mini')
    return html.Div([
        mini('Diferencia A − B', '—' if r['diferencia'] is None else f"{con_signo(r['diferencia'])} °C"),
        mini('Cambio en A', '—' if r['cambio_a'] is None else f"{con_signo(r['cambio_a'])} °C", 'comp-a'),
        mini('Cambio en B', '—' if r['cambio_b'] is None else f"{con_signo(r['cambio_b'])} °C", 'comp-b'),
    ], className='comp-tarjetas')


def cuerpo_comparacion(pais_a, serie_a, pais_b, serie_b):
    """Gráfica y tarjetas, o un mensaje si falta un país o no hay datos en el periodo."""
    if not pais_a or not pais_b:
        falta = 'dos países' if not pais_a and not pais_b else 'un segundo país'
        return html.Div(f'Elige {falta} en el mapa (modo Comparar) o en los selectores para comparar.',
                        className='estimacion-sin', role='status')
    if serie_a.empty or serie_b.empty:
        sin = pais_a if serie_a.empty else pais_b
        return html.Div(f'{sin} no tiene datos en el periodo elegido. Cambia el rango de años en la barra lateral.',
                        className='estimacion-sin', role='status')
    r = resumen_comparacion(serie_a, serie_b)
    return html.Div([
        dcc.Graph(figure=figura_comparacion(pais_a, serie_a, pais_b, serie_b), config={'displayModeBar': False},
                  id='comp-grafica'),
        tarjetas_comparacion(r),
        html.Div(f"Diferencia sobre {r['anios_comunes']} años con datos de ambos · cambio: últimos 10 años "
                 'frente a los primeros 10 del periodo', className='nota mt-2'),
    ])
