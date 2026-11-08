"""Piezas de la página «Explorador de temperaturas» (tarea 5.2)."""
import plotly.graph_objects as go
from dash import html

from componentes.formato import num
from componentes.mapa import clase_temperatura

PAISES_REFERENCIA = ['Mexico', 'Canada', 'Spain', 'India']

# color de la barra y tono de texto con contraste 4.5:1 sobre blanco, por clase
_TONOS = {'Baja': ('#42934D', '#2E6B36'), 'Media': ('#E2B64D', '#7A520C'),
          'Alta': ('#E9683A', '#B8461F'), 'Sin datos': ('#C9CFD5', '#636C77')}
ESCALA_MIN, ESCALA_MAX = -20, 30      # °C: largo de las barras (temperaturas anuales de 1900–2012)
MAX_ETIQUETAS = 8                     # anomalías con su año escrito en la gráfica

_FUENTE = dict(family='Inter, Segoe UI, sans-serif', size=12, color='#1F2933')


def figura_evolucion(serie, anomalias):
    """Línea de la temperatura anual con área suave y círculos en los años atípicos."""
    fig = go.Figure()
    if serie is None or serie.empty:
        fig.add_annotation(text='Sin datos en el periodo elegido', showarrow=False, xref='paper', yref='paper',
                           x=0.5, y=0.5, font=dict(size=13, color='#636C77'))
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        return _estilo(fig)
    base = float(serie.temp_media_anual_c.min()) - 0.5
    fig.add_trace(go.Scatter(x=serie.anio, y=[base] * len(serie), mode='lines', line=dict(width=0),
                             hoverinfo='skip', showlegend=False))
    fig.add_trace(go.Scatter(x=serie.anio, y=serie.temp_media_anual_c, mode='lines', name='Temperatura media',
                             fill='tonexty', fillcolor='rgba(233, 104, 58, 0.10)',
                             line=dict(color='#E9683A', width=2),
                             hovertemplate='%{x}: %{y:.2f} °C<extra></extra>'))
    if anomalias is not None and not anomalias.empty:
        # con muchas anomalías las etiquetas de año se encimarían: entonces solo se ven al pasar el mouse
        modo = 'markers+text' if len(anomalias) <= MAX_ETIQUETAS else 'markers'
        fig.add_trace(go.Scatter(
            x=anomalias.anio, y=anomalias.temp_media_anual_c, mode=modo, name='Anomalía detectada',
            text=[str(a) for a in anomalias.anio], textposition='top center',
            textfont=dict(size=11, color='#B8461F'),
            marker=dict(symbol='circle-open', size=11, color='#B8461F', line=dict(width=2.5)),
            hovertemplate='%{x}: %{y:.2f} °C · anomalía<extra></extra>'))
    fig.update_yaxes(title_text='°C')
    return _estilo(fig)


def _estilo(fig):
    fig.update_layout(height=320, margin=dict(l=48, r=12, t=10, b=30), paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)', font=_FUENTE, separators=',.', showlegend=False,
                      hoverlabel=dict(bgcolor='#FFFFFF', bordercolor='#E7EAED'))
    fig.update_xaxes(showgrid=True, gridcolor='#EEF0F2', linecolor='#E7EAED', tickformat='d')
    fig.update_yaxes(gridcolor='#EEF0F2', zeroline=False)
    return fig


def valor_referencia(serie):
    """(año, temperatura) del último año con dato en la serie, o (None, None)."""
    if serie is None or serie.empty:
        return None, None
    fila = serie.sort_values('anio').iloc[-1]
    return int(fila.anio), float(fila.temp_media_anual_c)


def barra_referencia(pais, anio, temp, anio_fin, destacado=False):
    clase = clase_temperatura(temp)
    color, texto = _TONOS[clase]
    ancho = 0 if temp is None else max(2, min(100, (temp - ESCALA_MIN) / (ESCALA_MAX - ESCALA_MIN) * 100))
    valor = 'Sin datos' if temp is None else f'{num(temp, 1)} °C'
    nota = f' ({anio})' if anio is not None and anio != anio_fin else ''
    return html.Div([
        html.Div([
            html.Span([pais, html.Span(' · filtro', className='nota') if destacado else None]),
            html.Span(f'{valor}{nota}', style={'color': texto}, className='fw-semibold'),
        ], className='d-flex justify-content-between'),
        html.Div(html.Div(style={'width': f'{ancho:.0f}%', 'background': color}, className='barra-relleno'),
                 className='barra-fondo', title=clase),
    ], className='barra-referencia')


def filas_tabla(serie, anios_anomalos):
    """Filas para la tabla: más recientes primero."""
    filas = []
    for fila in serie.sort_values('anio', ascending=False).itertuples():
        filas.append({
            'pais': fila.pais, 'anio': int(fila.anio),
            'temp': f'{num(fila.temp_media_anual_c)} °C',
            'incertidumbre': f'± {num(fila.incertidumbre_c)}',
            'anomalia': 'Sí' if int(fila.anio) in anios_anomalos else 'No',
        })
    return filas
