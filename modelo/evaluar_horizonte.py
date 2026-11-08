"""MAE por horizonte (1 a 10 años) en el periodo de prueba, frente a la línea base."""
import json, sys, numpy as np, pandas as pd
sys.path.insert(0, '.')
from modelo.inferencia import predecir, _DATOS
res = {}
for h in range(1, 11):
    em, eb = [], []
    for pais, d in _DATOS.groupby('pais'):
        s = d.set_index('anio').temp_media_anual_c
        for base in range(1992, 2013 - h):
            if base + h not in s.index: continue
            r = predecir({'pais': pais, 'anio_base': base, 'horizonte_anios': h})
            if r.get('error'): continue
            em.append(abs(r['prediccion'] - s[base + h]))
            eb.append(abs(s.loc[base - 4:base].mean() - s[base + h]))
    res[h] = {'mae_modelo': round(float(np.mean(em)), 3), 'mae_linea_base': round(float(np.mean(eb)), 3), 'casos': len(em)}
print(json.dumps(res, indent=1)); json.dump(res, open('data/processed/mae_por_horizonte.json', 'w'), indent=1)
