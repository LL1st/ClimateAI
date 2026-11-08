"""Página «Acerca del proyecto» (tarea 7.4): datos, modelo, métricas, limitaciones y licencia.
Las cifras salen de metricas.json y mae_por_horizonte.json (vía app/datos.py), no están escritas a mano."""
import dash
import dash_bootstrap_components as dbc
from dash import html

import datos
from componentes.formato import num

NOMBRE = 'Acerca del proyecto'
dash.register_page(__name__, path='/acerca', name=NOMBRE, title=f'{NOMBRE} · ClimateAI', order=4)

_NOMBRES_MODELOS = {'linea_base_promedio_5a': 'Línea base (promedio de los 5 años anteriores)',
                    'regresion_lineal': 'Regresión lineal', 'random_forest': 'Random Forest'}


def _miles(n):
    """18899 -> '18.899' (separador de miles en español)."""
    return f'{n:,}'.replace(',', '.')


def _seccion(titulo, *contenido, id=None):
    props = {'id': id} if id else {}
    return html.Section([html.H2(titulo, className='titulo-seccion mb-2'), *contenido],
                        className='tarjeta mt-3 acerca-seccion', **props)


def _tabla(encabezados, filas, resaltar=None):
    return html.Table([
        html.Thead(html.Tr([html.Th(e, scope='col') for e in encabezados])),
        html.Tbody([html.Tr([html.Td(c) for c in f], className='fila-resaltada' if i == resaltar else None)
                    for i, f in enumerate(filas)]),
    ], className='acerca-tabla')


def tabla_modelos(m):
    claves = ['linea_base_promedio_5a', 'regresion_lineal', 'random_forest']
    filas = [[_NOMBRES_MODELOS[k], f"{num(m['resultados'][k]['mae'], 3)} °C", f"{num(m['resultados'][k]['rmse'], 3)} °C",
              num(m['resultados'][k]['r2'], 4)] for k in claves]
    return _tabla(['Modelo', 'MAE', 'RMSE', 'R²'], filas, resaltar=claves.index(m['modelo_elegido']))


def tabla_horizontes(h):
    filas = [[f'{a} año' if a == 1 else f'{a} años', f"{num(v['mae_modelo'], 3)} °C",
              f"{num(v['mae_linea_base'], 3)} °C", _miles(v['casos'])] for a, v in sorted(h.items())]
    return _tabla(['Horizonte', 'Error del modelo (MAE)', 'Error de la línea base', 'Casos evaluados'], filas)


def layout():
    m, h = datos.metricas(), datos.mae_por_horizonte()
    n_paises = len(datos.lista_paises())
    elegido = _NOMBRES_MODELOS.get(m['modelo_elegido'], m['modelo_elegido']).lower()
    return html.Div([
        html.H1(NOMBRE, className='titulo-pagina mb-1'),
        html.Div('Qué datos usa ClimateAI, cómo estima y qué no puede hacer.', className='nota subtitulo-pagina'),

        _seccion('Qué es ClimateAI',
                 html.P('Dashboard académico de la UT Cancún (LITIID 73) que muestra la temperatura histórica de '
                        f'{n_paises} países, permite comparar dos de ellos y estima la temperatura de los próximos '
                        'años con un modelo de aprendizaje automático.'),
                 html.P('Equipo: Luis López Chi (requerimientos, interfaz y pruebas), José Cocom Ucan (datos y modelo) '
                        'y Juan Barajas Quetzal (mapa y desarrollo).', className='mb-0')),

        _seccion('Datos',
                 html.Ul([
                     html.Li(['Fuente: ', html.Strong('Berkeley Earth'), ', temperatura media mensual de la superficie '
                              'terrestre por país (archivo GlobalLandTemperaturesByCountry).']),
                     html.Li(f'{n_paises} países y territorios, de {datos.ANIO_MIN} a {datos.ANIO_MAX}. Un año cuenta solo '
                             'si tiene al menos 10 meses con dato; de cada año se usa el promedio y su incertidumbre.'),
                     html.Li('Serie global de la tierra firme de 1900 a 2015, para comparar cada país con el promedio '
                             'mundial.'),
                     html.Li('Referencia climática: el promedio de cada país entre 1951 y 1980.'),
                     html.Li('Solo hay datos de temperatura: el proyecto no incluye emisiones de CO₂.'),
                 ], className='mb-0')),

        _seccion('Modelo',
                 html.P(['El modelo elegido es una ', html.Strong(elegido), '. No predice la temperatura directamente, '
                         'sino cuánto se aleja un año del promedio de los 5 años anteriores. Usa cuatro variables, '
                         'todas calculadas solo con años pasados: el año, el promedio de los 5 años anteriores, cuánto '
                         'se alejó el año anterior de ese promedio y la tendencia (promedio de 5 años menos el de 10).']),
                 html.P('Para estimar varios años, el modelo encadena sus propias estimaciones año por año. Por eso el '
                        'error crece con el horizonte.'),
                 html.P(f"Se entrenó con los años anteriores a {m['corte']} ({_miles(m['train'])} registros país-año) y "
                        f"se probó con los de {m['corte']} en adelante ({_miles(m['test'])}). Se comparó con Random "
                        'Forest y con una línea base que solo repite el promedio de los 5 años anteriores.'),
                 html.P(['Los años atípicos de la página Anomalías los detecta un ', html.Strong('Isolation Forest'),
                         f" que marca el {num(m['anomalias_pct'], 1)} % de los registros más inusuales "
                         f"({m['anomalias']} años-país)."], className='mb-0')),

        _seccion('Métricas',
                 html.P('Error en el periodo de prueba para estimar el año siguiente (MAE: error medio absoluto; '
                        'RMSE: penaliza más los errores grandes). La fila resaltada es el modelo elegido.',
                        className='nota'),
                 tabla_modelos(m),
                 html.P('Error según cuántos años hacia adelante se estima:', className='nota mt-3'),
                 tabla_horizontes(h), id='acerca-metricas'),

        _seccion('Limitaciones',
                 html.Ul([
                     html.Li('Son estimaciones académicas basadas en patrones históricos, no pronósticos oficiales.'),
                     html.Li(f"El error medio va de {num(h[1]['mae_modelo'], 2)} °C a un año a "
                             f"{num(h[10]['mae_modelo'], 2)} °C a diez años, pero un año inusual puede fallar mucho "
                             'más (Canadá 2010: error de casi 2 °C).'),
                     html.Li(f'Los datos terminan en {datos.ANIO_MAX}: todo lo posterior es una extrapolación.'),
                     html.Li('El modelo solo conoce la temperatura pasada; no considera emisiones, eventos como El Niño '
                             'ni cambios de uso del suelo.'),
                     html.Li('Una anomalía es un aviso para revisar, no una conclusión: puede deberse a la calidad '
                             'del dato. No predice desastres naturales.'),
                     html.Li('Los nombres de país aparecen en inglés, como vienen en Berkeley Earth. En el mapa, los '
                             'países muy pequeños se representan con un solo punto.'),
                 ], className='mb-0')),

        _seccion('Licencia y créditos',
                 html.Ul([
                     html.Li(['Datos de temperatura: © Berkeley Earth, con licencia ',
                              html.A('Creative Commons BY-NC 4.0', href='https://creativecommons.org/licenses/by-nc/4.0/',
                                     target='_blank', rel='noopener'),
                              ' (atribución, uso no comercial). Más información en ',
                              html.A('berkeleyearth.org', href='https://berkeleyearth.org/data/', target='_blank',
                                     rel='noopener'), '.']),
                     html.Li(['Contornos para generar los puntos del mapa: ',
                              html.A('Natural Earth', href='https://www.naturalearthdata.com/', target='_blank',
                                     rel='noopener'), ' (dominio público).']),
                     html.Li('Hecho con Python, Dash, Plotly, pandas y scikit-learn.'),
                 ], className='mb-0'), id='acerca-licencia'),
    ])
