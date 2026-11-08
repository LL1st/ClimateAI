"""Anomalías frente a 1951–1980 para la página «Global y estaciones» (tarea 5.3).

- Anomalía anual del país: temperatura anual − promedio anual del país en 1951–1980.
- Anomalía global terrestre: temperatura global de tierra − su promedio de 1951–1980.
- Anomalía mensual: temperatura del mes − promedio de ese mismo mes en 1951–1980
  (la referencia se calcula siempre con 1951–1980, aunque el periodo filtrado sea otro).
"""
import pandas as pd
import plotly.graph_objects as go

REF_INICIO, REF_FIN = 1951, 1980
MESES = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
COLOR_PAIS, COLOR_GLOBAL = '#E9683A', '#2E75A9'
# de azul (más frío que lo normal) a blanco y a rojo (más cálido)
ESCALA_DIVERGENTE = [[0.0, '#1F5A85'], [0.25, '#7FB0D5'], [0.5, '#F7F7F7'], [0.75, '#F0A07C'], [1.0, '#A3341A']]

_FUENTE = dict(family='Inter, Segoe UI, sans-serif', size=12, color='#1F2933')


def anomalia_pais(serie):
    """serie: datos.serie_pais(). Devuelve anio, anomalia."""
    return pd.DataFrame({'anio': serie.anio, 'anomalia': serie.temp_media_anual_c - serie.ref_1951_1980_c})


def anomalia_global(serie_global_completa, inicio=None, fin=None):
    """Anomalía de la temperatura global terrestre; la referencia sale de la serie completa."""
    g = serie_global_completa
    ref = g[g.anio.between(REF_INICIO, REF_FIN)].temp_global_tierra_c.mean()
    d = pd.DataFrame({'anio': g.anio, 'anomalia': g.temp_global_tierra_c - ref})
    if inicio is not None:
        d = d[d.anio >= inicio]
    if fin is not None:
        d = d[d.anio <= fin]
    return d.reset_index(drop=True)


def anomalia_mensual(mensual_completo, inicio, fin):
    """Tabla mes × año con la anomalía de cada mes frente a su promedio de 1951–1980."""
    m = mensual_completo
    ref = m[m.anio.between(REF_INICIO, REF_FIN)].groupby('mes').temp_c.mean()
    d = m[m.anio.between(inicio, fin)].copy()
    d['anomalia'] = d.temp_c - d.mes.map(ref)
    tabla = d.pivot(index='mes', columns='anio', values='anomalia')
    return tabla.reindex(index=range(1, 13))


def _vacia(fig, mensaje):
    fig.add_annotation(text=mensaje, showarrow=False, xref='paper', yref='paper', x=0.5, y=0.5,
                       font=dict(size=13, color='#6B7580'))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def figura_anomalias(pais, an_pais, an_global):
    """Gráfica 4: anomalía del país y anomalía global terrestre, dos líneas."""
    fig = go.Figure()
    if an_pais.empty and an_global.empty:
        return _estilo(_vacia(fig, 'Sin datos en el periodo elegido'), 300)
    fig.add_hline(y=0, line=dict(color='#C9CFD5', width=1))
    fig.add_trace(go.Scatter(x=an_pais.anio, y=an_pais.anomalia, mode='lines', name=pais,
                             line=dict(color=COLOR_PAIS, width=2),
                             hovertemplate='%{x}: %{y:+.2f} °C<extra>' + pais + '</extra>'))
    fig.add_trace(go.Scatter(x=an_global.anio, y=an_global.anomalia, mode='lines', name='Global terrestre',
                             line=dict(color=COLOR_GLOBAL, width=2, dash='dash'),
                             hovertemplate='%{x}: %{y:+.2f} °C<extra>Global terrestre</extra>'))
    fig.update_yaxes(title_text='°C frente a 1951–1980')
    fig.update_layout(hovermode='x unified',
                      legend=dict(orientation='h', yanchor='bottom', y=1.0, xanchor='left', x=0))
    return _estilo(fig, 300)


def figura_estacional(tabla):
    """Gráfica 5: mapa de calor año × mes con la anomalía mensual."""
    fig = go.Figure()
    if tabla.empty or tabla.isna().all().all():
        return _estilo(_vacia(fig, 'Sin datos mensuales en el periodo elegido'), 340)
    limite = float(tabla.abs().stack().quantile(0.98)) or 1.0      # escala simétrica, sin que un extremo la aplaste
    fig.add_trace(go.Heatmap(
        z=tabla.values, x=list(tabla.columns), y=MESES, zmid=0, zmin=-limite, zmax=limite,
        colorscale=ESCALA_DIVERGENTE, xgap=0.5, ygap=1,
        colorbar=dict(title=dict(text='°C', side='top'), thickness=10, len=0.9),
        hovertemplate='%{y} %{x}: %{z:+.2f} °C<extra></extra>',
    ))
    fig.update_yaxes(autorange='reversed')   # enero arriba
    return _estilo(fig, 340)


def _estilo(fig, alto):
    fig.update_layout(height=alto, margin=dict(l=56, r=12, t=10, b=30), paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)', font=_FUENTE, separators=',.',
                      hoverlabel=dict(bgcolor='#FFFFFF', bordercolor='#E7EAED'))
    fig.update_xaxes(showgrid=False, linecolor='#E7EAED', tickformat='d')
    fig.update_yaxes(gridcolor='#EEF0F2', zeroline=False)
    return fig
