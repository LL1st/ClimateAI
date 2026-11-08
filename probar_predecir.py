import json
from modelo.inferencia import predecir
casos = [{'pais': 'Mexico', 'horizonte_anios': 5},
         {'pais': 'Canada', 'anio_base': 2000, 'horizonte_anios': 10},
         {'pais': 'India', 'anio_base': 1995, 'horizonte_anios': 5},
         {'pais': 'Atlantis', 'horizonte_anios': 5}, {'pais': 'Mexico', 'horizonte_anios': 15}, {}]
for c in casos: print(json.dumps(c, ensure_ascii=False), '->', json.dumps(predecir(c), ensure_ascii=False))
