"""Formato de números para la interfaz en español (coma decimal)."""


def num(valor, decimales=2):
    """1234.5 -> '1234,50'. Devuelve '—' si no hay valor."""
    if valor is None:
        return '—'
    return f'{valor:.{decimales}f}'.replace('.', ',')
