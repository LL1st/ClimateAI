"""Prepara los datos de ClimateAI a partir de los CSV de Berkeley Earth.
Uso: python preparar_datos.py <carpeta con los CSV> <carpeta de salida>
"""
import sys, os, pandas as pd
src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
c = pd.read_csv(os.path.join(src, 'GlobalLandTemperaturesByCountry.csv'), parse_dates=['dt'])
CONTINENTES = ['Africa', 'Asia', 'Europe', 'North America', 'Oceania', 'South America', 'Antarctica']
EUROPA = {'Denmark': 'Denmark (Europe)', 'France': 'France (Europe)', 'Netherlands': 'Netherlands (Europe)', 'United Kingdom': 'United Kingdom (Europe)'}
c = c[~c.Country.isin(CONTINENTES + list(EUROPA))].copy()          # quita continentes y versiones con territorios lejanos
c['Country'] = c.Country.replace({v: k for k, v in EUROPA.items()})
c['anio'] = c.dt.dt.year; c['mes'] = c.dt.dt.month
# mensual limpio (para la gráfica estacional)
men = c.dropna(subset=['AverageTemperature']).query('1900 <= anio <= 2012')
men[['Country', 'anio', 'mes', 'AverageTemperature']].rename(columns={'Country': 'pais', 'AverageTemperature': 'temp_c'}).round(3).to_csv(os.path.join(out, 'temperatura_pais_mes.csv'), index=False)
# anual por país: solo años con al menos 10 meses
a = (men.groupby(['Country', 'anio']).agg(meses=('AverageTemperature', 'size'), temp_media_anual_c=('AverageTemperature', 'mean'),
     incertidumbre_c=('AverageTemperatureUncertainty', 'mean')).reset_index().query('meses >= 10').drop(columns='meses').rename(columns={'Country': 'pais'}))
partes = []
for pais, d in a.groupby('pais'):
    d = d.set_index('anio').reindex(range(d.anio.min(), d.anio.max() + 1))
    prev = d.temp_media_anual_c.shift(1)                              # solo años anteriores: sin fuga
    d['temp_anio_anterior_c'] = prev
    d['temp_media_5a_c'] = prev.rolling(5, min_periods=5).mean()
    d['temp_media_10a_c'] = prev.rolling(10, min_periods=10).mean()
    d['ref_1951_1980_c'] = d.loc[1951:1980, 'temp_media_anual_c'].mean()
    partes.append(d.dropna(subset=['temp_media_anual_c']).reset_index().assign(pais=pais))
p = pd.concat(partes, ignore_index=True)
p['cambio_anio_anterior_c'] = p.temp_anio_anterior_c - p.temp_media_5a_c
p['tendencia_c'] = p.temp_media_5a_c - p.temp_media_10a_c
cols = ['pais', 'anio', 'temp_media_anual_c', 'incertidumbre_c', 'temp_anio_anterior_c', 'temp_media_5a_c', 'temp_media_10a_c', 'cambio_anio_anterior_c', 'tendencia_c', 'ref_1951_1980_c']
p[cols].round(3).to_csv(os.path.join(out, 'clima_pais_anio.csv'), index=False)
# serie global terrestre anual (años completos)
g = pd.read_csv(os.path.join(src, 'GlobalTemperatures.csv'), parse_dates=['dt']); g['anio'] = g.dt.dt.year
g = g.groupby('anio').agg(n=('LandAverageTemperature', 'count'), temp_global_tierra_c=('LandAverageTemperature', 'mean'),
                          temp_global_tierra_oceano_c=('LandAndOceanAverageTemperature', 'mean')).query('n == 12 and anio >= 1900').drop(columns='n')
g.round(3).to_csv(os.path.join(out, 'global_anio.csv'))
print('pais-año', p.shape, 'países', p.pais.nunique(), 'años', p.anio.min(), p.anio.max(), '| mensual', men.shape, '| global', g.shape)
