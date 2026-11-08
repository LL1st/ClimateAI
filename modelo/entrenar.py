"""Entrena y compara modelos de ClimateAI. Uso: python modelo/entrenar.py data/processed"""
import sys, os, json, joblib, pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
d = sys.argv[1]
df = pd.read_csv(os.path.join(d, 'clima_pais_anio.csv'))
X = ['anio', 'temp_media_5a_c', 'cambio_anio_anterior_c', 'tendencia_c']
m = df.dropna(subset=X).sort_values('anio').reset_index(drop=True)
m['objetivo_cambio_c'] = m.temp_media_anual_c - m.temp_media_5a_c        # el modelo predice el cambio sobre el promedio de 5 años
corte = int(m.anio.iloc[int(len(m) * 0.8)])
tr, te = m[m.anio < corte], m[m.anio >= corte]
y = te.temp_media_anual_c
def met(p): return dict(mae=round(mean_absolute_error(y, p), 3), rmse=round(mean_squared_error(y, p) ** .5, 3), r2=round(r2_score(y, p), 4))
res = {'linea_base_promedio_5a': met(te.temp_media_5a_c)}
modelos = {'regresion_lineal': LinearRegression(), 'random_forest': RandomForestRegressor(n_estimators=200, min_samples_leaf=20, random_state=42, n_jobs=-1)}
for k, mdl in modelos.items():
    mdl.fit(tr[X], tr.objetivo_cambio_c); res[k] = met(te.temp_media_5a_c + mdl.predict(te[X]))
mejor = min(modelos, key=lambda k: res[k]['mae'])
info = dict(corte=corte, filas=len(m), train=len(tr), test=len(te), variables=X, resultados=res, modelo_elegido=mejor,
            supera_linea_base=res[mejor]['mae'] < res['linea_base_promedio_5a']['mae'])
if mejor == 'regresion_lineal':
    sd = tr[X].std(); info['peso_variables'] = {v: round(float(c * sd[v]), 4) for v, c in zip(X, modelos[mejor].coef_)}
else:
    info['peso_variables'] = dict(zip(X, modelos[mejor].feature_importances_.round(4).tolist()))
joblib.dump({'modelo': modelos[mejor], 'variables': X, 'mae': res[mejor]['mae']}, os.path.join(os.path.dirname(__file__), 'modelo_clima.joblib'))
# anomalías: Isolation Forest sobre el cambio de cada año frente a su promedio de 5 años
iso = IsolationForest(contamination=0.02, random_state=42).fit(m[['objetivo_cambio_c', 'cambio_anio_anterior_c']])
m['puntaje'] = -iso.score_samples(m[['objetivo_cambio_c', 'cambio_anio_anterior_c']]); m['es_anomalia'] = (iso.predict(m[['objetivo_cambio_c', 'cambio_anio_anterior_c']]) == -1).astype(int)
m[m.es_anomalia == 1][['pais', 'anio', 'temp_media_anual_c', 'temp_media_5a_c', 'objetivo_cambio_c', 'puntaje']].round(3).to_csv(os.path.join(d, 'anomalias.csv'), index=False)
info['anomalias'] = int(m.es_anomalia.sum()); info['anomalias_pct'] = round(100 * m.es_anomalia.mean(), 1)
json.dump(info, open(os.path.join(d, 'metricas.json'), 'w'), ensure_ascii=False, indent=2)
print(json.dumps(info, ensure_ascii=False, indent=1))
