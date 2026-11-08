"""Tarjeta de estimación (tarea 4.1): formulario y resultado de predecir().

Aquí no hay lógica del modelo: solo se muestra lo que devuelve predecir() (regla 1).
Toda estimación lleva su ± MAE y el aviso (regla 3); si hay error, solo el mensaje (regla 4).
"""
import dash_bootstrap_components as dbc
from dash import dcc, html

from componentes.chip_riesgo import chip_riesgo
from componentes.formato import ETIQUETAS_DESPLEGABLE, num
from componentes.icono import icono

PAIS_INICIAL = 'Mexico'
HORIZONTE_INICIAL = 5
ANIO_BASE_MIN = 1910

# Casos de ejemplo de la tarea 4.2: (clave del id, texto del menú, entrada de predecir())
EJEMPLOS = [
    ('mexico', 'México · desde 2012 a 5 años', {'pais': 'Mexico', 'anio_base': 2012, 'horizonte_anios': 5}),
    ('canada', 'Canadá · desde 2000 a 10 años', {'pais': 'Canada', 'anio_base': 2000, 'horizonte_anios': 10}),
    ('india', 'India · desde 1995 a 5 años', {'pais': 'India', 'anio_base': 1995, 'horizonte_anios': 5}),
]


def _signo(valor, decimales=2):
    texto = num(abs(valor), decimales)
    return f'+{texto}' if valor >= 0 else f'−{texto}'


def formulario_estimacion(paises, anio_max, nombre_modelo):
    anios = [{'label': str(a), 'value': a} for a in range(anio_max, ANIO_BASE_MIN - 1, -1)]
    return html.Section([
        html.Div([
            html.Div(icono('tendencia', 22), className='tarjeta-encabezado-icono'),
            html.Div([
                html.H2('Estimación del modelo', className='titulo-seccion'),
                html.Div(f'Temperatura media anual · {nombre_modelo}', className='nota'),
            ], className='flex-grow-1'),
            dbc.DropdownMenu(
                [dbc.DropdownMenuItem(texto, id=f'ejemplo-{clave}') for clave, texto, _ in EJEMPLOS],
                label='Cargar ejemplo', size='sm', color='light', align_end=True, id='menu-ejemplos',
                toggle_class_name='boton-ejemplo'),
        ], className='tarjeta-encabezado'),
        dbc.Row([
            dbc.Col([
                html.Label('País', htmlFor='est-pais', className='form-label'),
                dcc.Dropdown(id='est-pais', options=paises, value=PAIS_INICIAL, clearable=False,
                             labels=ETIQUETAS_DESPLEGABLE),
            ], xs=7),
            dbc.Col([
                html.Label('Año base', htmlFor='est-anio-base', className='form-label'),
                dcc.Dropdown(id='est-anio-base', options=anios, value=anio_max, clearable=False,
                             labels=ETIQUETAS_DESPLEGABLE),
            ], xs=5),
        ], className='g-2'),
        html.Label('Horizonte (años)', htmlFor='est-horizonte', className='form-label mt-3'),
        dcc.Slider(id='est-horizonte', min=1, max=10, step=1, value=HORIZONTE_INICIAL,
                   marks={h: str(h) for h in (1, 5, 10)}, tooltip={'placement': 'bottom'}),
        html.Button('Calcular estimación', id='est-calcular', className='btn btn-primary w-100 mt-3'),
        dcc.Loading(html.Div(id='est-resultado', className='mt-3'), type='dot', color='#B8461F'),
    ], className='tarjeta tarjeta-estimacion', id='tarjeta-estimacion')


def resultado_estimacion(r):
    """Estado «resultado» o «sin estimación» a partir de la salida de predecir()."""
    if r.get('error') or r.get('prediccion') is None:
        return html.Div([
            html.Div('Sin estimación para este país', className='estimacion-sin-titulo'),
            html.P(r.get('error') or 'No se pudo calcular la estimación.', className='mb-0'),
        ], className='estimacion-sin', role='alert')

    partes = [
        html.Div(f"Estimado para {r['anio_objetivo']} · {r['pais']}", className='estimacion-etiqueta'),
        html.Div(f"{num(r['prediccion'])} °C", className='estimacion-valor'),
        html.Div(f"± {num(r['mae_modelo'])} °C de error medio (MAE)", className='estimacion-margen'),
        html.Div([
            chip_riesgo(r.get('clase_etiqueta')),
            html.Span(f"{_signo(r['cambio_vs_1951_1980'])} °C frente a 1951–1980", className='estimacion-cambio'),
        ], className='estimacion-riesgo'),
    ]
    if r.get('valor_real') is not None:
        error = abs(r['prediccion'] - r['valor_real'])
        partes.append(html.Div(f"Real: {num(r['valor_real'])} °C · Error: {num(error)} °C",
                               className='estimacion-real'))
    return html.Div([
        html.Div(partes, className='estimacion-resultado'),
        html.Div(r.get('aviso'), className='aviso-estimacion mt-3'),
    ])
