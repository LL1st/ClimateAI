# ClimateAI · contexto para Claude Code

Dashboard web académico (UT Cancún, LITIID 73) que muestra la temperatura histórica de 232 países, compara dos países y estima la temperatura futura con un modelo de ML. **Entrega final: 1 de diciembre de 2026. Congelamiento de funciones: 20 de noviembre.**

Equipo: Luis López Chi (requerimientos, UI y pruebas), José Cocom Ucan (datos y modelo), Juan Barajas Quetzal (mapa y desarrollo).

## Alcance (no lo amplíes sin que te lo pidan)

- **Solo datos de temperatura** de Berkeley Earth. **No hay datos de CO₂**: no agregues nada de emisiones (cambio CC-02).
- Páginas: Dashboard (mapa + estimación), Temperaturas, Global y estaciones, Anomalías y Acerca del proyecto.
- Fuera de alcance: exportar PNG/CSV, comparar dos periodos, pantallas «Modelo de IA» y «Fuentes y calidad de datos», ciudades/estados, cuentas de usuario y despliegue en producción.

## Stack

- Python 3.11 o superior. Interfaz: **Dash** + Plotly + dash-bootstrap-components. Datos: pandas. Modelo: scikit-learn + joblib. Pruebas: pytest.
- geopandas **solo** en `scripts/generar_puntos_mapa.py` (se corre una vez, no en la app).
- Toda la interfaz va en español.

## Estructura

```
climateai_modelo/
├── app/
│   ├── app.py                 # punto de entrada: Dash(use_pages=True)
│   ├── datos.py               # carga única de data/processed (caché en memoria)
│   ├── componentes/           # sidebar, tarjeta_kpi, tarjeta_estimacion, chip_riesgo, aviso_transparencia
│   └── pages/                 # dashboard.py, temperaturas.py, global_estaciones.py, anomalias.py, acerca.py
├── assets/style.css           # tokens de diseño (Dash lo carga solo)
├── data/raw/                  # CSV originales del zip (no se versionan)
├── data/processed/            # salidas de preparar_datos.py y entrenar.py
├── modelo/                    # entrenar.py, inferencia.py (predecir), evaluar_horizonte.py, modelo_clima.joblib
├── scripts/                   # generar_puntos_mapa.py, generar_paises_iso3.py
├── tests/
├── preparar_datos.py
└── requirements.txt
```

## Reglas del código

1. **La app solo usa el modelo a través de `from modelo.inferencia import predecir`.** No reentrenes, no cargues el `.joblib` desde `app/` y no copies lógica del modelo en los callbacks. No modifiques `modelo/` salvo que la tarea lo pida.
2. Los datos se leen **una vez** en `app/datos.py`; las páginas importan de ahí. Nada de leer CSV dentro de callbacks.
3. **Nunca muestres una estimación sin su margen (± MAE) y el aviso de limitaciones.** El aviso de transparencia va en todas las páginas.
4. Si `predecir()` devuelve `error`, la tarjeta muestra ese mensaje; la app no debe romperse.
5. El color nunca es la única señal: los países A y B llevan su letra, el riesgo lleva texto y las anomalías, un círculo.
6. Cada callback que tarde más de 3 s es un defecto (RNF-01).
7. Después de cada tarea: `pytest -q` debe pasar y `python app/app.py` debe arrancar sin errores.

## Datos disponibles (`data/processed/`)

| Archivo | Contenido |
| --- | --- |
| `clima_pais_anio.csv` | Una fila por país y año (1900–2012): `pais, anio, temp_media_anual_c, incertidumbre_c, temp_anio_anterior_c, temp_media_5a_c, temp_media_10a_c, cambio_anio_anterior_c, tendencia_c, ref_1951_1980_c` |
| `temperatura_pais_mes.csv` | `pais, anio, mes, temp_c` (para el mapa de calor) |
| `global_anio.csv` | `anio, temp_global_tierra_c, temp_global_tierra_oceano_c` (1900–2015) |
| `anomalias.csv` | `pais, anio, temp_media_anual_c, temp_media_5a_c, objetivo_cambio_c, puntaje` (476 filas) |
| `metricas.json`, `mae_por_horizonte.json` | Resultados de la evaluación (MAE 0.307 °C a 1 año; línea base 0.318 °C) |

Los nombres de país son los de Berkeley Earth en inglés (`Mexico`, `Canada`…). Para el mapa hace falta `paises_iso3.csv` (tarea 2.1).

## Contrato de `predecir()` (no lo cambies)

```python
predecir({"pais": "Mexico", "anio_base": 2012, "horizonte_anios": 5})
# -> {"pais", "anio_base", "anio_objetivo", "prediccion", "serie_estimada", "mae_modelo",
#     "clase_etiqueta", "cambio_vs_1951_1980", "confianza_o_score", "valor_real", "aviso", "error", "tiempo_ms"}
# Entrada inválida -> {"prediccion": None, "error": "<mensaje para el usuario>", "tiempo_ms": n}
```

`anio_base` es opcional (por omisión, el último año con datos). `horizonte_anios` es un entero de 1 a 10. `valor_real` viene lleno si el año objetivo es 2012 o anterior.

## Diseño

Archivo de Figma: https://www.figma.com/design/BIDaDhn8rTEK3tbpKJlHPQ/ClimateAI-%E2%80%94-Dashboard-clim%C3%A1tico

La referencia es la página **«Wireframes · Alta fidelidad»**. Si tienes el servidor MCP de Figma conectado, consulta cada frame con su `node-id` (en la URL va con guion: `?node-id=96-30`). Si no lo tienes, pídele al usuario una captura del frame.

| Pantalla | node-id | Notas |
| --- | --- | --- |
| AF · 1 Dashboard | `96:30` | Mapa, tarjeta de estimación, KPIs y aviso de transparencia |
| AF · 2 Dashboard en modo comparación | `96:313` | Panel de comparación A/B |
| AF · 3 Explorador de temperaturas | `96:637` | Página Temperaturas |
| AF · 5 Anomalías | `96:994` | Página Anomalías |
| Guía visual | `96:1183` | Paleta, tipografía y componentes |
| Estados de la tarjeta de estimación | `96:1225` | Cargando, resultado, sin estimación y error |
| Baja fidelidad (página completa) | `93:30` | Anotaciones de comportamiento y flujo de navegación |

Hay tres diferencias que ganan sobre el Figma:
- **AF · 4 Explorador de emisiones (`96:807`) ya no aplica**, porque no hay datos de CO₂. Esa página se reemplaza por «Global y estaciones», que no tiene diseño en Figma: usa el mismo estilo que `96:637`.
- **Textos de prueba:** ignora los que dicen «Mockup», «Datos de ejemplo» o valores inventados; los valores reales salen de los datos.
- **Colores:** donde el Figma use texto gris `#87919B` o naranja sobre fondo naranja claro, usa los tonos corregidos de abajo.

- Tipografía Inter: títulos Bold 25, secciones Semi Bold 18, navegación Medium 13 y notas Regular 11 o más.
- Colores: naranja `#E9683A` (acción, país A, temperatura alta), azul `#2E75A9` (país B), verde `#42934D` (temperatura baja), amarillo `#E2B64D` (temperatura media), texto `#1F2933`, texto secundario `#636C77` (corregido en DEF-01: cumple 4,5:1 también sobre el fondo gris), fondo `#F2F4F6`, borde `#E7EAED` y aviso `#7A520C` sobre `#FFF5DD`.
- Para texto sobre fondos claros usa `#B8461F` en lugar del naranja. Estos tonos ya cumplen el contraste 4.5:1.
- Tarjetas blancas con radio de 16 px y borde de 1 px; controles con radio de 8 a 10 px; barra lateral blanca de 244 px.

## Comandos

```
python preparar_datos.py "data/raw/Global Land Temperatures" data/processed
python modelo/entrenar.py data/processed
python app/app.py          # abre http://127.0.0.1:8050
pytest -q
```

El plan de trabajo por tareas está en `PLAN.md`.
