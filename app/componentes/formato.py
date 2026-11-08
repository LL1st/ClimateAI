"""Formato de números para la interfaz en español (coma decimal)."""


def num(valor, decimales=2):
    """1234.5 -> '1234,50'. Devuelve '—' si no hay valor."""
    if valor is None:
        return '—'
    return f'{valor:.{decimales}f}'.replace('.', ',')


def con_signo(valor, decimales=2):
    """0.62 -> '+0,62', -0.4 -> '−0,40'. Devuelve '—' si no hay valor."""
    if valor is None:
        return '—'
    texto = num(abs(valor), decimales)
    return f'+{texto}' if valor >= 0 else f'−{texto}'


# Textos en español para los desplegables de Dash 4 (por omisión vienen en inglés: «Search»…)
ETIQUETAS_DESPLEGABLE = {
    'search': 'Buscar',
    'clear_search': 'Borrar búsqueda',
    'no_options_found': 'Sin resultados',
    'clear_selection': 'Quitar selección',
    'select_all': 'Seleccionar todo',
    'deselect_all': 'Quitar todo',
}
