"""Panel de diagnóstico del modelo (tarea 7.3): gráfica 7 con el peso de cada variable
(metricas.json) y el registro de la última inferencia (entrada, salida y tiempo_ms)."""
import json

import plotly.graph_objects as go
from dash import dcc, html

from componentes.formato import con_signo, num

NOMBRES_VARIABLES = {   # nombre completo (tooltip)
    'anio': 'Año',
    'temp_media_5a_c': 'Promedio de los 5 años anteriores',
    'cambio_anio_anterior_c': 'Año anterior frente a su promedio de 5 años',
    'tendencia_c': 'Tendencia (promedio de 5 años − de 10 años)',
}
NOMBRES_CORTOS = {'anio': 'Año', 'temp_media_5a_c': 'Promedio 5 años',
                  'cambio_anio_anterior_c': 'Año anterior', 'tendencia_c': 'Tendencia'}
COLOR_POSITIVO, COLOR_NEGATIVO = '#B8461F', '#2E75A9'
_FUENTE = dict(family='Inter, Segoe UI, sans-serif', size=12, color='#1F2933')


def figura_pesos(metricas):
    """Gráfica 7: barras horizontales con el peso de cada variable, de mayor a menor efecto."""
    pesos = metricas.get('peso_variables', {})
    orden = sorted(pesos.items(), key=lambda kv: abs(kv[1]))          # el más importante queda arriba
    valores = [v for _, v in orden]
    lineal = metricas.get('modelo_elegido') == 'regresion_lineal'
    formato = (lambda v: con_signo(v, 4)) if lineal else (lambda v: num(v, 4))
    # el valor va junto al nombre corto: así no se encima con la barra ni se corta en pantallas angostas
    etiquetas = [f'{NOMBRES_CORTOS.get(k, k)}  {formato(v)}' for k, v in orden]
    fig = go.Figure(go.Bar(
        x=valores, y=etiquetas, orientation='h', customdata=[NOMBRES_VARIABLES.get(k, k) for k, _ in orden],
        marker_color=[COLOR_POSITIVO if v >= 0 else COLOR_NEGATIVO for v in valores],
        hovertemplate='%{customdata}: %{x:.4f}<extra></extra>',
    ))
    fig.add_vline(x=0, line=dict(color='#C9CFD5', width=1))
    fig.update_layout(height=230, margin=dict(l=10, r=16, t=10, b=30), paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)', font=_FUENTE, separators=',.', showlegend=False)
    fig.update_xaxes(title_text='°C por desviación estándar' if lineal else 'importancia', gridcolor='#EEF0F2',
                     zeroline=False)
    fig.update_yaxes(automargin=True)
    return fig


def nota_pesos(metricas):
    if metricas.get('modelo_elegido') == 'regresion_lineal':
        return ('Coeficientes estandarizados de la regresión lineal: cuánto cambia la estimación (en °C) cuando la '
                'variable sube una desviación estándar. Naranja: sube la estimación · azul: la baja.')
    return 'Importancia de cada variable en el modelo elegido.'


def resumen_metricas(metricas):
    elegido = metricas['modelo_elegido']
    r = metricas['resultados']
    return (f"MAE del modelo: {num(r[elegido]['mae'], 3)} °C · línea base (promedio de 5 años): "
            f"{num(r['linea_base_promedio_5a']['mae'], 3)} °C · R²: {num(r[elegido]['r2'], 4)} · "
            f"entrenado hasta {metricas['corte'] - 1}, probado desde {metricas['corte']}")


def _fila(etiqueta, valor):
    return html.Tr([html.Th(etiqueta, scope='row', className='diag-etiqueta'), html.Td(valor)])


def registro_inferencia(registro):
    """Tabla con la última entrada y salida de predecir(), más el JSON completo."""
    if not registro:
        return html.Div('Todavía no hay inferencias: calcula una estimación.', className='nota')
    e, s = registro.get('entrada') or {}, registro.get('salida') or {}
    filas = [
        _fila('Entrada', f"país {e.get('pais')} · año base {e.get('anio_base', 'último con datos')} · "
                         f"horizonte {e.get('horizonte_anios')}"),
        _fila('Tiempo', f"{registro.get('tiempo_ms')} ms"),
    ]
    if s.get('error'):
        filas.append(_fila('Resultado', f"error: {s['error']}"))
    else:
        filas.append(_fila('Resultado', f"{num(s.get('prediccion'))} °C ± {num(s.get('mae_modelo'))} para "
                                        f"{s.get('anio_objetivo')} · {s.get('clase_etiqueta')}"))
    return html.Div([
        html.Table(html.Tbody(filas), className='diag-tabla'),
        html.Details([html.Summary('Ver la salida completa de predecir()'),
                      html.Pre(json.dumps(registro, ensure_ascii=False, indent=2), className='diag-json')]),
    ])


def panel_diagnostico(metricas):
    return html.Details([
        html.Summary([html.Span('Diagnóstico del modelo', className='titulo-seccion'),
                      html.Span(' · peso de las variables y última inferencia', className='nota')],
                     className='diag-resumen'),
        html.Div([
            html.Div(resumen_metricas(metricas), className='nota mt-2'),
            html.H3('Peso de cada variable', className='diag-subtitulo'),
            html.Div(nota_pesos(metricas), className='nota'),
            dcc.Graph(id='diag-pesos', figure=figura_pesos(metricas), config={'displayModeBar': False}),
            html.H3('Última inferencia', className='diag-subtitulo'),
            html.Div(id='diag-registro'),
        ]),
    ], className='tarjeta mt-3', id='panel-diagnostico')
