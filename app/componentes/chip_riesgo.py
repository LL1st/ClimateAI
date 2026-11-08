"""Chip de riesgo: el color siempre va con su texto (regla 5 de CLAUDE.md)."""
from dash import html

# etiqueta de predecir() -> clase CSS
NIVELES = {'Riesgo bajo': 'bajo', 'Riesgo medio': 'medio', 'Riesgo alto': 'alto'}


def chip_riesgo(etiqueta):
    nivel = NIVELES.get(etiqueta, 'medio')
    return html.Span(etiqueta or 'Riesgo sin calcular', className=f'chip-riesgo chip-riesgo-{nivel}')
