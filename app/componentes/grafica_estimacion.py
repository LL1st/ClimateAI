"""Gráfica 3 (tarea 4.2): serie histórica del país, estimación punteada con banda ± MAE
y, si existen, los valores reales de los años estimados. Solo dibuja lo que devuelve predecir()."""
import plotly.graph_objects as go

COLOR_HISTORIA = '#1F2933'
COLOR_ESTIMACION = '#B8461F'
BANDA = 'rgba(233, 104, 58, 0.18)'
COLOR_REAL = '#2E75A9'
ANIOS_DE_CONTEXTO = 50          # años de historia visibles antes del año base

_FUENTE = dict(family='Inter, Segoe UI, sans-serif', size=12, color='#1F2933')


def _vacia(mensaje):
    fig = go.Figure()
    fig.add_annotation(text=mensaje, showarrow=False, font=dict(size=13, color='#6B7580'),
                       xref='paper', yref='paper', x=0.5, y=0.5)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return _estilo(fig)


def figura_estimacion(r, historia, reales):
    """r: salida de predecir(). historia: DataFrame anio/temp_media_anual_c hasta el año base.
    reales: DataFrame anio/temp_media_anual_c de los años estimados que ya tienen dato."""
    if r.get('error') or r.get('prediccion') is None:
        return _vacia('Sin estimación para mostrar')

    base, mae = r['anio_base'], r['mae_modelo']
    anios = list(range(base + 1, r['anio_objetivo'] + 1))
    est = r['serie_estimada']
    ultimo = float(historia.temp_media_anual_c.iloc[-1])
    # la estimación arranca en el último valor real para que la línea no quede suelta
    x_est, y_est = [base] + anios, [ultimo] + est
    arriba = [ultimo] + [v + mae for v in est]
    abajo = [ultimo] + [v - mae for v in est]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_est + x_est[::-1], y=arriba + abajo[::-1], fill='toself', fillcolor=BANDA,
                             line=dict(width=0), hoverinfo='skip', name=f'± MAE ({mae:.2f} °C)'.replace('.', ',')))
    fig.add_trace(go.Scatter(x=historia.anio, y=historia.temp_media_anual_c, mode='lines', name='Histórico',
                             line=dict(color=COLOR_HISTORIA, width=1.8),
                             hovertemplate='%{x}: %{y:.2f} °C<extra>Histórico</extra>'))
    fig.add_trace(go.Scatter(x=x_est, y=y_est, mode='lines+markers', name='Estimación',
                             line=dict(color=COLOR_ESTIMACION, width=2.2, dash='dot'), marker=dict(size=5),
                             hovertemplate='%{x}: %{y:.2f} °C<extra>Estimación</extra>'))
    if reales is not None and not reales.empty:
        fig.add_trace(go.Scatter(x=reales.anio, y=reales.temp_media_anual_c, mode='markers', name='Real',
                                 marker=dict(color=COLOR_REAL, size=7, symbol='circle-open', line=dict(width=2)),
                                 hovertemplate='%{x}: %{y:.2f} °C<extra>Real</extra>'))
    fig.update_xaxes(range=[max(int(historia.anio.min()), base - ANIOS_DE_CONTEXTO) - 0.5, r['anio_objetivo'] + 0.5])
    fig.update_yaxes(title_text='°C')
    return _estilo(fig)


def _estilo(fig):
    fig.update_layout(
        height=300, margin=dict(l=48, r=12, t=10, b=36), paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)', font=_FUENTE, hovermode='x unified', separators=',.',
        legend=dict(orientation='h', yanchor='bottom', y=1.0, xanchor='left', x=0),
    )
    fig.update_xaxes(showgrid=False, linecolor='#E7EAED', tickformat='d')
    fig.update_yaxes(gridcolor='#E7EAED', zeroline=False)
    return fig
