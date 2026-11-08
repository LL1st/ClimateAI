# ClimateAI · prueba de datos y modelo (solo temperatura)

Fuente: `Global_Land_Temperatures.zip` (Berkeley Earth), entregado por el profesor.

```
python preparar_datos.py "<carpeta con los CSV>" data/processed   # limpia y genera los datasets
python modelo/entrenar.py data/processed                          # compara modelos, guarda el elegido y las anomalías
python modelo/evaluar_horizonte.py                                # MAE por horizonte (1 a 10 años)
python probar_predecir.py                                         # prueba el contrato predecir()
```

Archivos generados en `data/processed/`:
- `clima_pais_anio.csv`: una fila por país y año (232 países, 1900-2012).
- `temperatura_pais_mes.csv`: datos mensuales limpios, para la gráfica estacional.
- `global_anio.csv`: temperatura global terrestre anual (1900-2015).
- `anomalias.csv`: años atípicos detectados con Isolation Forest (2 %).
- `metricas.json` y `mae_por_horizonte.json`: resultados de la evaluación.

Requisitos: Python 3.11 o superior. Instala las dependencias con `pip install -r requirements.txt` (pandas, scikit-learn, joblib, Dash, Plotly, dash-bootstrap-components y pytest).
