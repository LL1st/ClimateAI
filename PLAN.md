# ClimateAI · plan de trabajo con Claude Code

Plan para construir el dashboard del 9 al 27 de noviembre de 2026 siguiendo el cronograma (con la recuperación del atraso del 8/11). Los datos, el modelo y `predecir()` ya están listos. Lo que falta es la aplicación.

## Cómo usar este plan

1. Abre Claude Code en la carpeta `climateai_modelo`. Claude lee `CLAUDE.md` solo.
2. Pide una tarea a la vez, por ejemplo: **«Lee PLAN.md y haz la tarea 1.2»**. Para las tareas marcadas con 🧭, pídele primero que entre en modo plan y revisa su propuesta antes de que escriba código.
3. Al terminar cada tarea: revisa el diff, corre `pytest -q` y `python app/app.py`, revisa la pantalla en el navegador y haz commit con el número de tarea (`git commit -m "1.2 barra lateral y páginas"`).
4. Si Claude propone algo fuera de alcance (CO₂, exportar, ciudades), dile que no: está en la lista de exclusiones de `CLAUDE.md`.
5. Marca la casilla de cada tarea terminada en este archivo.

## Calendario

| Fechas | Fase | Hito |
| --- | --- | --- |
| Lun 9 – mar 10 | 0, 1 y 2: repositorio, app base y datos del mapa | — |
| Mié 11 – vie 13 | 3, 4 y 5: mapa, estimación y exploradores | — |
| Lun 16 | Festivo | — |
| Mar 17 – vie 20 | 6 y 7: comparación, anomalías y diagnóstico | **H6** (comparación) y **H7** (congelamiento), vie 20 |
| Lun 23 – vie 27 | 8: pruebas y corrección de defectos | **H8**, vie 27 |
| Lun 30 – mar 1 | 9: ensayo y entrega | **H9**, mar 1/12 |

---

## Fase 0 · Repositorio (lun 9 · Juan · A11)

- [x] **0.1 Inicializar el repositorio**
  - Prompt: «Inicializa git en esta carpeta. Crea un `.gitignore` para Python que excluya `.venv/`, `__pycache__/`, `data/raw/` y `.DS_Store`. Actualiza `requirements.txt` agregando dash, dash-bootstrap-components, plotly y pytest con versiones fijas compatibles con las que ya están, y corrige el README para que pida Python 3.11 o superior.»
  - Terminado cuando: `pip install -r requirements.txt` funciona en un entorno nuevo y el primer commit está hecho.
- [x] **0.2 Pruebas del modelo existente**
  - Prompt: «Crea `tests/test_predecir.py` con pytest. Debe probar que `predecir()` devuelve todas las llaves del contrato en `CLAUDE.md` para México a 5 años; que devuelve `error` sin lanzar excepción con país inexistente, horizonte 0, horizonte 11, entrada vacía y un año base sin datos; que `valor_real` viene lleno para Canadá desde 2000 a 10 años; y que cada llamada tarda menos de 3 s.»
  - Terminado cuando: `pytest -q` pasa.

## Fase 1 · Aplicación base (lun 9 – mar 10 · Juan y Luis · A12)

- [x] **1.1 Carga de datos** (Juan)
  - Prompt: «Crea `app/datos.py`, que lea una sola vez los archivos de `data/processed` y exponga funciones para obtener la serie de un país, la lista de países, los valores de un año para el mapa, la serie global, los datos mensuales de un país y las anomalías. Agrega `tests/test_datos.py` que verifique 0 duplicados por país y año, 0 nulos en `temp_media_anual_c` y 232 países (criterio CA-01).»
  - Terminado cuando: las pruebas pasan y ninguna función lee archivos más de una vez.
- [x] **1.2 Esqueleto de la app** 🧭 (Juan)
  - Nota (8/11): el enlace «Reportar un error» queda fuera por decisión del equipo. El Dashboard muestra por ahora una franja de estado (datos, modelo y una estimación de prueba) que la tarea 4.1 reemplaza.
  - Prompt: «Crea `app/app.py` con Dash, `use_pages=True` y dash-bootstrap-components. Crea las cinco páginas de `CLAUDE.md` con su título y un contenedor vacío. Agrega en `app/componentes/` la barra lateral (logo ClimateAI, menú con la página activa resaltada y "Acerca del proyecto" al pie) y el aviso de transparencia con el enlace "Reportar un error", que se muestra en todas las páginas. Los filtros globales de país y rango de años van en la barra lateral y se guardan en un `dcc.Store`.»
  - Terminado cuando: `python app/app.py` abre las 5 páginas y el menú navega entre ellas.
- [x] **1.3 Estilos del diseño** (Luis)
  - Prompt: «Crea `assets/style.css` con los tokens de diseño de `CLAUDE.md` como variables CSS y aplícalos a la barra lateral, las tarjetas, los botones y los textos. Crea `app/componentes/tarjeta_kpi.py` con título, valor grande y nota, igual que los KPI del Figma.»
  - Terminado cuando: la app se parece a la pantalla «AF · 1 Dashboard» del Figma, sin contar el contenido.

## Fase 2 · Datos para el mapa (lun 9 – mar 10 · José y Juan)

- [x] **2.1 Tabla de países a ISO3** (José)
  - Resultado: 228 de 232 con ISO3. Sin código: Baker Island, Kingman Reef y Palmyra Atoll (deshabitados) y Gaza Strip (comparte PSE con Palestina). Para la 2.2: Natural Earth usa `ADM0_A3` distintos de ISO3 en algunos casos (p. ej. Palestina `PSX`, Sudán del Sur `SDS`); hay que traducirlos al unir. Sudán del Sur no está en Berkeley Earth (sus datos van dentro de Sudan).
  - Prompt: «Crea `scripts/generar_paises_iso3.py`, que produzca `data/processed/paises_iso3.csv` con las columnas `pais` e `iso3` para los 232 países de `clima_pais_anio.csv`. Usa una tabla de equivalencias escrita en el script para los nombres que no son estándar. Imprime al final la lista de países sin código. Los territorios deshabitados sin código pueden quedar fuera del mapa, pero deben listarse.»
  - Terminado cuando: todos los países con población tienen ISO3 y la lista de excluidos está revisada.
- [x] **2.2 Puntos del mapa** 🧭 (Juan; se corre en la computadora del equipo, porque necesita internet)
  - Prompt: «Crea `scripts/generar_puntos_mapa.py` con geopandas. Debe descargar el mapa de países Admin 0 de Natural Earth a escala 1:110m, crear una cuadrícula de puntos cada 2 grados y conservar solo los que caen sobre un país. Guarda `data/processed/puntos_mapa.csv` con `lat, lon, iso3`. Usa la columna `ADM0_A3` de Natural Earth, no `ISO_A3`, porque esta trae -99 para Francia y Noruega. Imprime cuántos puntos quedaron.»
  - Terminado cuando: hay entre 3,000 y 10,000 puntos y casi todos los países de `paises_iso3.csv` tienen al menos un punto.
  - **Plan B:** si geopandas da problemas, usa un mapa coroplético de Plotly con los códigos ISO3 (ver tarea 3.1).
  - Resultado (8/11): 3,956 puntos (3,879 de la cuadrícula 1:110m + 77 de relleno con el mapa 1:50m para islas y países pequeños) y los 228 países con código tienen punto. Los territorios de ultramar (Guayana Francesa, Reunión, Svalbard, Bonaire…) se separan de su país. Brunéi, Kosovo, Sudán del Sur y Vanuatu no están en Berkeley Earth: sus puntos conservan su código y en la 3.1 van en gris. Dependencias en `requirements-scripts.txt`.

## Fase 3 · Mapa interactivo (mié 11 – vie 13 · Juan · A14) — ruta crítica

- [x] **3.1 Mapa por año** 🧭
  - Extra (8/11): efecto «lupa» al pasar el mouse (`assets/mapa_lupa.js`): el punto crece a 13 px y los vecinos a menos de 7° crecen según la distancia. Clases fijas Baja < 15 °C, Media 15–25 °C, Alta > 25 °C y gris «Sin datos».
  - Prompt: «En la página Dashboard, dibuja el mapa con `go.Scattergeo` usando `puntos_mapa.csv`. Cada punto toma el color de la temperatura de su país en el año elegido, con una escala de verde (baja) a amarillo (media) y a naranja (alta). Agrega el deslizador de año (1900–2012), un tooltip con el nombre del país y su °C, y la leyenda Baja/Media/Alta. Si `puntos_mapa.csv` no existe, usa `go.Choropleth` con los ISO3 como respaldo.»
  - Terminado cuando: al mover el año, el mapa se actualiza en menos de 3 s, y 10 de 10 tooltips revisados coinciden con el dataset (CA-02 y CA-03).
- [ ] **3.2 Selección de países A y B**
  - Prompt: «Agrega el interruptor Explorar | Comparar en el encabezado del mapa. En modo Comparar, el primer clic en un país lo guarda como A y el segundo como B en un `dcc.Store`; un tercer clic reemplaza al B. Marca A y B en el mapa con un círculo y su letra. El país A también se copia al formulario de estimación.»
  - Terminado cuando: el Store guarda A y B correctos en 5 pruebas a mano.
- **Recorte si el lunes 16 no está la 3.2:** quitar el deslizador de año y dejar el mapa en el último año (2012).

## Fase 4 · Estimación con el modelo (mié 11 – vie 13 · José · A21)

- [ ] **4.1 Tarjeta de estimación** 🧭
  - Prompt: «En la página Dashboard, crea la tarjeta de estimación del Figma con el selector de país, el selector de año base (1910–2012, por omisión 2012), el deslizador de horizonte (1–10) y el botón "Calcular estimación". El botón llama a `predecir()` dentro de un callback envuelto en `dcc.Loading`. Muestra la predicción ± `mae_modelo`, el chip de riesgo (verde, ámbar o rojo, con texto), `cambio_vs_1951_1980` y el aviso. Si viene `valor_real`, muestra también "Real: X °C · Error: Y °C". Si viene `error`, muestra solo el mensaje.»
  - Terminado cuando: México, Canadá e India dan tarjetas completas, y una entrada inválida muestra el mensaje sin romper la app (RF-01, RF-02, RF-03 y RNF-02).
- [ ] **4.2 Gráfica 3 y casos de ejemplo**
  - Prompt: «Debajo de la tarjeta, agrega la gráfica 3: la serie histórica del país en línea continua y la `serie_estimada` punteada con una banda de ± MAE; si hay `valor_real`, dibuja también los valores reales de esos años. Agrega el botón "Cargar ejemplo" con 3 casos: México desde 2012 a 5 años, Canadá desde 2000 a 10 años e India desde 1995 a 5 años. El botón llena el formulario y calcula solo. Guarda la última entrada, la salida y `tiempo_ms` en un Store para el panel de diagnóstico.»
  - Terminado cuando: los 3 casos se cargan y la gráfica coincide con la tarjeta (RF-05).

## Fase 5 · Exploradores y KPIs (mié 11 – vie 13 · Luis · A16)

- [ ] **5.1 KPIs del dashboard**
  - Prompt: «Agrega la fila de 4 KPIs al Dashboard: temperatura media del periodo, variación del periodo, cambio frente a 1951–1980 y número de anomalías. Todos reaccionan a los filtros globales de país y rango de años.»
- [ ] **5.2 Página Temperaturas**
  - Prompt: «En `pages/temperaturas.py`, muestra la evolución histórica del país filtrado (línea), un resumen de 4 países de referencia en barras y una tabla paginada con `pais, anio, temp_media_anual_c, incertidumbre_c` y una columna "¿Anomalía?". Todo reacciona a los filtros globales.»
- [ ] **5.3 Página Global y estaciones**
  - Prompt: «En `pages/global_estaciones.py`, agrega la gráfica 4, con la anomalía del país y la anomalía global terrestre frente a 1951–1980 en dos líneas, y la gráfica 5, un heatmap con año en X, mes en Y y color de la anomalía de cada mes frente a su promedio de 1951–1980, en escala de azul a rojo.»
  - Terminado cuando: 5 de 5 valores revisados coinciden con los CSV (RF-09) y los filtros actualizan todo en menos de 3 s.

## Fase 6 · Comparación de dos países (mar 17 – jue 19 · Juan · A15) → H6

- [ ] **6.1 Panel de comparación**
  - Prompt: «Cuando el interruptor está en Comparar, sustituye la tarjeta de estimación por el panel de comparación del Figma: selectores A y B (sincronizados con el mapa), la gráfica 2 con dos líneas (A naranja continua, B azul punteada) y 3 tarjetas: diferencia A − B, cambio de A y cambio de B en el periodo filtrado. Si solo hay un país elegido, muestra "Elige un segundo país en el mapa para comparar".»
  - Terminado cuando: la diferencia coincide con un cálculo a mano en 3 casos (RF-07).

## Fase 7 · Anomalías y diagnóstico (mar 17 – vie 20 · José · A20 y A22)

- [ ] **7.1 Prueba de las 5 anomalías introducidas** (CA-08)
  - Prompt: «Crea `tests/test_anomalias.py`. Debe tomar una copia de `clima_pais_anio.csv`, alterar 5 pares país-año conocidos sumando +3 °C, volver a correr el Isolation Forest con la misma configuración de `modelo/entrenar.py` y verificar que al menos 4 de los 5 queden marcados. No modifiques los archivos originales.»
- [ ] **7.2 Página Anomalías**
  - Prompt: «En `pages/anomalias.py`, muestra 3 KPIs (registros señalados, países con avisos y periodo), la gráfica 6 (serie del país con círculos en los años de `anomalias.csv`), la tabla de anomalías filtrable por país y años, y el recuadro "Cómo interpretar estos avisos" con el texto del Figma.»
- [ ] **7.3 Panel de diagnóstico**
  - Prompt: «Agrega al final del Dashboard un panel plegable con la gráfica 7 (barras horizontales con `peso_variables` de `metricas.json`) y el registro de la última inferencia (entrada, salida y `tiempo_ms`).»
- [ ] **7.4 Página Acerca del proyecto**
  - Prompt: «En `pages/acerca.py`, explica en texto breve los datos (Berkeley Earth, 1900–2012), el modelo (regresión lineal sobre el cambio frente al promedio de 5 años), sus métricas (de `metricas.json` y `mae_por_horizonte.json`), las limitaciones y la licencia de los datos.»

### Vie 20 · Congelamiento de funciones (H7)

- [ ] Todas las tareas de las fases 0 a 7 están terminadas y con commit.
- [ ] `pytest -q` pasa y la app arranca sin errores en la consola.
- [ ] Desde aquí solo se corrigen defectos; no se agregan funciones.

## Fase 8 · Pruebas y corrección (lun 23 – vie 27 · Luis prueba, Juan corrige)

- [ ] **8.1 Pruebas automáticas de rendimiento**
  - Prompt: «Agrega pruebas que midan el tiempo de los callbacks principales (mapa por año, estimación, filtros y comparación) llamando a sus funciones directamente. Deben fallar si alguno pasa de 3 s.»
- [ ] **8.2 Lista de verificación manual**
  - Prompt: «Crea `tests/CHECKLIST.md` con los criterios CA-01 a CA-09 del documento de planificación, convertidos en pasos de prueba manual: navegadores (Chrome, Edge y Firefox), prueba de usabilidad (3 usuarios comparan dos países en 3 min o menos, sin ayuda) y revisión de contraste.»
- [ ] **8.3 Corrección de defectos:** un commit por defecto, primero los críticos y altos.

## Fase 9 · Entrega (lun 30 – mar 1/12)

- [ ] **9.1 README final**
  - Prompt: «Actualiza el README con la instalación paso a paso en Windows, los comandos para preparar los datos, entrenar y correr la app, y una captura de cada página.»
- [ ] **9.2 Ensayo de la demostración** con los 3 casos de ejemplo y la comparación de dos países.

## Orden de recorte si algo se atrasa

1. Deslizador de año del mapa (queda fijo en 2012).
2. Mapa de calor estacional (gráfica 5).
3. Chip de riesgo.

No se recortan: el mapa con selección A/B, la comparación, la estimación con su margen y aviso, ni las anomalías.
