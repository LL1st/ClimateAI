"""Genera data/processed/puntos_mapa.csv (lat, lon, iso3, relleno): los puntos del mapa estilo «dot matrix».

Uso (una sola vez, necesita internet la primera vez):
    pip install -r requirements-scripts.txt
    python scripts/generar_puntos_mapa.py

Es el único lugar del proyecto que usa geopandas. Pasos:
1. Descarga los países Admin 0 de Natural Earth (1:110m y 1:50m) a data/raw/natural_earth/.
2. Separa los territorios de ultramar que Natural Earth junta con su país (Guayana Francesa,
   Reunión, Svalbard, Bonaire…), porque Berkeley Earth los trae como países aparte.
3. Cuadrícula cada 4° sobre el mapa 1:110m, unida por ADM0_A3 (no ISO_A3, que trae -99
   para Francia y Noruega) y traducida a ISO3.
4. Relleno: cada país de paises_iso3.csv sin punto recibe uno en su punto representativo
   del mapa 1:50m (islas y países pequeños que la cuadrícula no toca). Se marca con
   relleno=1 y el mapa lo dibuja más chico, para no romper el dibujo de la cuadrícula.
"""
import os
import urllib.request

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import box

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_NE = os.path.join(RAIZ, 'data', 'raw', 'natural_earth')
PAISES = os.path.join(RAIZ, 'data', 'processed', 'paises_iso3.csv')
SALIDA = os.path.join(RAIZ, 'data', 'processed', 'puntos_mapa.csv')
URL_NE = 'https://naciscdn.org/naturalearth/{escala}/cultural/ne_{escala}_admin_0_countries.zip'

PASO = 4                      # grados entre puntos (estilo «dot matrix»; con 2° salían ~3,900 puntos)
LAT_MIN, LAT_MAX = -60, 84    # sin la Antártida (no tiene datos)

# ADM0_A3 de Natural Earth -> ISO3 de paises_iso3.csv, cuando no coinciden
TRADUCCION = {
    'PSX': 'PSE',   # Palestina
    'SAH': 'ESH',   # Sahara Occidental
    'SOL': 'SOM',   # Somalilandia, dentro de Somalia
    'CYN': 'CYP',   # norte de Chipre
    'ALD': 'ALA',   # Åland
    'IOA': 'CXR',   # Territorios australianos del Índico (Isla de Navidad)
}

# Países del mapa que no están en Berkeley Earth: conservan su código y el mapa los pinta en gris
SIN_DATOS = {
    'BRN': 'Brunéi',
    'KOS': 'Kosovo',
    'SDS': 'Sudán del Sur (sus datos van dentro de Sudan)',
    'VUT': 'Vanuatu',
}

# Partes de ultramar que Natural Earth incluye en el país soberano: (ADM0_A3, ISO3, caja lon/lat)
ULTRAMAR = [
    ('FRA', 'GUF', (-55.0, 1.5, -51.0, 6.5)),      # Guayana Francesa
    ('FRA', 'GLP', (-62.0, 15.8, -60.9, 16.6)),    # Guadalupe
    ('FRA', 'MTQ', (-61.3, 14.3, -60.7, 15.0)),    # Martinica
    ('FRA', 'REU', (55.0, -21.5, 56.0, -20.8)),    # Reunión
    ('FRA', 'MYT', (44.9, -13.1, 45.4, -12.5)),    # Mayotte
    ('NOR', 'SJM', (-10.0, 70.5, 35.0, 81.5)),     # Svalbard y Jan Mayen
    ('NLD', 'BES', (-69.0, 11.9, -62.5, 18.0)),    # Bonaire, San Eustaquio y Saba
]


def descargar(escala):
    os.makedirs(DIR_NE, exist_ok=True)
    ruta = os.path.join(DIR_NE, f'ne_{escala}_admin_0_countries.zip')
    if not os.path.exists(ruta):
        print(f'Descargando Natural Earth {escala}…')
        urllib.request.urlretrieve(URL_NE.format(escala=escala), ruta)
    return ruta


def cargar_paises(escala):
    """Países de Natural Earth con una columna iso3 (ultramar separado y códigos traducidos)."""
    g = gpd.read_file(descargar(escala))[['ADM0_A3', 'geometry']].explode(index_parts=False)
    g['iso3'] = g.ADM0_A3.map(lambda c: TRADUCCION.get(c, c))
    for soberano, iso3, caja in ULTRAMAR:
        dentro = (g.ADM0_A3 == soberano) & g.geometry.representative_point().within(box(*caja))
        g.loc[dentro, 'iso3'] = iso3
    return g[['iso3', 'geometry']].dissolve(by='iso3').reset_index()


def cuadricula(paises):
    lons = np.arange(-180 + PASO / 2, 180, PASO)
    lats = np.arange(LAT_MIN + PASO / 2, LAT_MAX, PASO)
    lon, lat = np.meshgrid(lons, lats)
    puntos = gpd.GeoDataFrame({'lat': lat.ravel(), 'lon': lon.ravel()},
                              geometry=gpd.points_from_xy(lon.ravel(), lat.ravel()), crs=paises.crs)
    en_tierra = gpd.sjoin(puntos, paises, predicate='within', how='inner')
    return en_tierra[['lat', 'lon', 'iso3']].drop_duplicates(['lat', 'lon']).assign(relleno=0)


def relleno(puntos, paises_50m, nuestros):
    faltan = sorted(nuestros - set(puntos.iso3))
    g = paises_50m[paises_50m.iso3.isin(faltan)].copy()
    rp = g.geometry.representative_point()
    extra = pd.DataFrame({'lat': rp.y.values, 'lon': rp.x.values, 'iso3': g.iso3.values, 'relleno': 1})
    return extra, sorted(set(faltan) - set(extra.iso3))


def main():
    tabla = pd.read_csv(PAISES, encoding='utf-8', keep_default_na=False)
    nuestros = set(tabla.iso3) - {''}

    base = cuadricula(cargar_paises('110m'))
    desconocidos = sorted(set(base.iso3) - nuestros - set(SIN_DATOS))
    extra, sin_punto = relleno(base, cargar_paises('50m'), nuestros)

    puntos = pd.concat([base, extra], ignore_index=True).round({'lat': 2, 'lon': 2})
    puntos = puntos.drop_duplicates(['lat', 'lon', 'iso3']).sort_values(['lat', 'lon']).reset_index(drop=True)
    puntos.to_csv(SALIDA, index=False, encoding='utf-8')

    con_punto = len(nuestros & set(puntos.iso3))
    print(f'{len(puntos)} puntos ({len(base)} de la cuadrícula de {PASO}° + {len(extra)} chicos de relleno) '
          f'-> {os.path.relpath(SALIDA, RAIZ)}')
    print(f'Países con punto: {con_punto} de {len(nuestros)} con código')
    print(f'Sin punto: {sin_punto or "ninguno"}')
    print('Sin datos en Berkeley Earth (gris en el mapa): '
          + ', '.join(f'{c} {SIN_DATOS[c]}' for c in sorted(set(puntos.iso3) & set(SIN_DATOS))))
    if desconocidos:
        print(f'REVISAR · códigos de Natural Earth sin traducir: {desconocidos}')


if __name__ == '__main__':
    main()
