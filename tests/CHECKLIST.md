# ClimateAI · lista de verificación manual (tarea 8.2)

Para la fase 8 (lun 23 – vie 27 de noviembre). Luis la ejecuta; Juan corrige los defectos (tarea 8.3).

> **Aviso sobre los criterios.** El documento de planificación con el texto oficial de CA-01 a CA-09 no está en el repositorio. CA-01, CA-02, CA-03 y CA-08 vienen de `PLAN.md`. **CA-04 a CA-07 se dedujeron de los requisitos (RF/RNF) de `PLAN.md` y están marcados _por confirmar_**: antes de usar esta lista, compárenlos con el documento y corrijan lo que no coincida. CA-09 agrupa navegadores, usabilidad y contraste, como pide la tarea 8.2.

## Antes de empezar

1. `pip install -r requirements.txt` en un entorno limpio y `pytest -q` → todo debe pasar.
2. `python app/app.py` y abrir http://127.0.0.1:8050.
3. Usar una ventana privada (sin datos de sesiones anteriores) y la consola del navegador abierta (F12).
4. Anotar en cada criterio: fecha, quién probó y el resultado en cada navegador (✅ pasa · ❌ falla · ➖ no aplica). Cada ❌ se registra en la tabla de defectos del final.

Navegadores: **Chrome**, **Edge** y **Firefox**, en su versión más reciente, en pantalla de escritorio (1366 px de ancho o más).

---

## CA-01 · Calidad de los datos

| Paso | Resultado esperado |
| --- | --- |
| Correr `pytest -q tests/test_datos.py` | Pasa: 0 duplicados país-año, 0 nulos en la temperatura anual, 232 países |
| Abrir el filtro «País» de la barra lateral y escribir «Fin» | Aparece Finland; la lista tiene 232 países |

Respaldo automático: `tests/test_datos.py`.

| Chrome | Edge | Firefox | Fecha / quién |
| --- | --- | --- | --- |
| | | | |

## CA-02 · El mapa se actualiza en menos de 3 s

| Paso | Resultado esperado |
| --- | --- |
| En el Dashboard, mover el deslizador «Año» del mapa a 1900, 1950 y 2012 | El mapa cambia de colores en menos de 3 s cada vez (contar con cronómetro) |
| Mirar el subtítulo del mapa | Dice «… por país en 1900» (o el año elegido) |
| Pasar el mouse sobre los puntos | El punto crece y sus vecinos también (efecto lupa); vuelven a su tamaño al salir |

Respaldo automático: `tests/test_rendimiento.py` (mapa por año ≈ 0,2 s).

| Chrome | Edge | Firefox | Fecha / quién |
| --- | --- | --- | --- |
| | | | |

## CA-03 · 10 de 10 tooltips coinciden con el dataset

| Paso | Resultado esperado |
| --- | --- |
| Con el año 1990, pasar el mouse por 10 países distintos (incluir México, Canadá, India, España y uno pequeño de relleno, por ejemplo Malta) y anotar el °C | Cada valor coincide con `data/processed/clima_pais_anio.csv` (columna `temp_media_anual_c`, redondeada a 2 decimales) |
| Pasar el mouse por Sudán del Sur | Dice «Sin datos» y el punto es gris |

| # | País | °C del tooltip | °C del CSV | ¿Coincide? |
| --- | --- | --- | --- | --- |
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |
| 6 | | | | |
| 7 | | | | |
| 8 | | | | |
| 9 | | | | |
| 10 | | | | |

Respaldo automático: `tests/test_mapa.py::test_ca03_diez_tooltips_coinciden_con_el_dataset`.

## CA-04 · Estimación completa _(por confirmar · RF-01, RF-02, RF-03)_

| Paso | Resultado esperado |
| --- | --- |
| En «Estimación del modelo», abrir «Cargar ejemplo» y elegir cada caso | El formulario se llena y la tarjeta se calcula sola |
| México · desde 2012 a 5 años | 21,36 °C ± 0,33 °C · Riesgo medio · +0,62 °C frente a 1951–1980 · aviso ámbar |
| Canadá · desde 2000 a 10 años | −3,85 °C ± 0,39 °C · Riesgo alto · «Real: −1,89 °C · Error: 1,96 °C» |
| India · desde 1995 a 5 años | 24,39 °C ± 0,33 °C · Riesgo bajo · «Real: 24,50 °C · Error: 0,11 °C» |
| Revisar cada tarjeta | Nunca aparece una estimación sin su «±» ni sin el aviso |

Respaldo automático: `tests/test_estimacion.py`.

| Chrome | Edge | Firefox | Fecha / quién |
| --- | --- | --- | --- |
| | | | |

## CA-05 · Entradas inválidas no rompen la app _(por confirmar · RNF-02)_

| Paso | Resultado esperado |
| --- | --- |
| País «Heard Island And Mcdonald Islands», año base 1950, calcular | «Sin estimación para este país» + mensaje de que no hay 10 años seguidos de datos |
| México con año base 1910 y horizonte 10 | Calcula sin error |
| Cambiar varias veces de país y año base muy rápido y pulsar el botón | La app sigue respondiendo; la consola no muestra errores rojos |

Respaldo automático: `tests/test_predecir.py`, `tests/test_estimacion.py`.

| Chrome | Edge | Firefox | Fecha / quién |
| --- | --- | --- | --- |
| | | | |

## CA-06 · La gráfica de la estimación coincide con la tarjeta _(por confirmar · RF-05)_

| Paso | Resultado esperado |
| --- | --- |
| Cargar el ejemplo de Canadá y bajar a «Serie histórica y estimación · Canada» | La línea punteada termina en 2010 con el mismo valor de la tarjeta (−3,85 °C) |
| Pasar el mouse por 2010 | Muestra la estimación y el valor real (círculo azul) |
| Abrir «Diagnóstico del modelo» al final del Dashboard | «Última inferencia» muestra la entrada de Canadá, el tiempo en ms y el resultado |

Respaldo automático: `tests/test_estimacion.py`, `tests/test_diagnostico.py`.

| Chrome | Edge | Firefox | Fecha / quién |
| --- | --- | --- | --- |
| | | | |

## CA-07 · Comparación de dos países _(por confirmar · RF-07)_

| Paso | Resultado esperado |
| --- | --- |
| Cambiar el mapa a «Comparar» y hacer clic en México y luego en Canadá | Insignias A y B en el mapa; el panel «Comparación» sustituye a la estimación |
| Con el rango 1900–2012, leer las tarjetas | Diferencia A − B +25,53 °C · Cambio en A +0,93 °C · Cambio en B +1,87 °C |
| Repetir con 2 pares más y calcular la diferencia a mano (promedio de A menos promedio de B en los años comunes, desde el CSV) | Coincide con la tarjeta (redondeo a 2 decimales) |
| Cambiar B desde el selector del panel | La insignia B se mueve en el mapa |
| Hacer un tercer clic en otro país | Reemplaza a B; un clic sobre A no cambia nada |

Respaldo automático: `tests/test_comparacion.py`, `tests/test_seleccion_ab.py`.

| Par | Diferencia a mano | Diferencia en la app | ¿Coincide? |
| --- | --- | --- | --- |
| México – Canadá | | | |
| | | | |
| | | | |

## CA-08 · Detección de 5 anomalías introducidas

| Paso | Resultado esperado |
| --- | --- |
| Correr `pytest -q tests/test_anomalias.py` | Pasa: al menos 4 de 5 detectadas (resultado actual: 5 de 5) |
| Abrir la página Anomalías | 476 registros señalados, 60 países; tabla de la más atípica a la menos; recuadro «Cómo interpretar estos avisos» |
| En «País de la tabla» elegir Finland | Solo filas de Finland; el KPI cambia a sus registros |

| Chrome | Edge | Firefox | Fecha / quién |
| --- | --- | --- | --- |
| | | | |

## CA-09 · Navegadores, usabilidad y contraste

### a) Recorrido en cada navegador

Repetir en Chrome, Edge y Firefox. Marcar ✅ si funciona sin errores rojos en la consola.

| Pantalla / acción | Chrome | Edge | Firefox |
| --- | --- | --- | --- |
| Dashboard carga con KPIs, mapa y estimación | | | |
| Menú: Temperaturas, Global y estaciones, Anomalías, Acerca del proyecto | | | |
| Filtros de la barra lateral (país y años) cambian KPIs y páginas | | | |
| Mapa: deslizador, tooltips y lupa | | | |
| Modo Comparar y panel de comparación | | | |
| Tablas paginadas (Temperaturas y Anomalías) | | | |
| Aviso de transparencia visible en las 5 páginas | | | |
| Recargar la página (F5) no rompe nada | | | |

### b) Prueba de usabilidad (3 usuarios)

Personas que no conozcan la app. Sin explicación previa ni ayuda durante la prueba.

**Instrucción que se lee en voz alta:** «Compara la temperatura de México y Canadá y dime cuál de los dos se ha calentado más desde 1900.»

- Cronometrar desde que la persona toca el mouse hasta que responde.
- **Éxito:** responde correctamente (Canadá, +1,87 °C frente a +0,93 °C) en **3 minutos o menos**, sin ayuda.
- Anotar dónde dudó o qué buscó primero.

| Usuario | Tiempo | ¿Correcto? | ¿Sin ayuda? | Dónde dudó |
| --- | --- | --- | --- | --- |
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

Se cumple si los 3 lo logran (o según el umbral del documento de planificación).

### c) Contraste (WCAG 2.1 AA: 4,5:1 para texto normal)

Calculado con la fórmula de WCAG sobre los colores de `assets/style.css`. Confirmar en el navegador con una herramienta de contraste (por ejemplo, las DevTools de Chrome).

| Uso | Texto | Fondo | Contraste | ¿Cumple? |
| --- | --- | --- | --- | --- |
| Texto principal | `#1F2933` | blanco | 14,8:1 | ✅ |
| Texto secundario en tarjetas | `#636C77` | blanco | 5,3:1 | ✅ |
| Texto secundario sobre el fondo gris (subtítulos de página, barra A/B, bloque de resultado) | `#636C77` | `#F2F4F6` | 4,8:1 | ✅ (antes 4,3:1, ver DEF-01) |
| Naranja de texto | `#B8461F` | blanco | 5,3:1 | ✅ |
| Menú activo y chip «Riesgo alto» | `#B8461F` | `#FDEEE8` | 4,7:1 | ✅ |
| Botón principal | blanco | `#B8461F` | 5,3:1 | ✅ |
| Insignia B y valores azules | blanco / `#2E75A9` | `#2E75A9` / blanco | 5,0:1 | ✅ |
| Aviso ámbar y chip «Riesgo medio» | `#7A520C` | `#FFF5DD` | 6,4:1 | ✅ |
| Chip «Riesgo bajo» | `#2E6B36` | `#E9F4EA` | 5,7:1 | ✅ |
| Naranja `#E9683A` (solo en puntos y líneas, nunca en texto) | — | blanco | 3,2:1 | ➖ |

Además, revisar que el color nunca sea la única señal (regla 5 de `CLAUDE.md`): A y B llevan su letra, el riesgo lleva texto y las anomalías llevan un círculo.

---

## Defectos encontrados

Prioridad: **crítico** (rompe la app o da datos falsos) · **alto** (una función no sirve) · **medio** · **bajo**.

| ID | Criterio | Descripción | Prioridad | Estado |
| --- | --- | --- | --- | --- |
| DEF-01 | CA-09 c | El texto secundario `#6B7580` sobre el fondo `#F2F4F6` tiene 4,3:1 (< 4,5:1). Corregido: `--texto-secundario` ahora es `#636C77` (4,8:1 sobre gris, 5,3:1 sobre blanco); `tests/test_estilos.py::test_contraste_aa` lo vigila | medio | Cerrado (8/11) |
| DEF-02 | CA-07 | En el panel «Comparación», los valores de las tres tarjetas («+25,53 °C») se partían en dos líneas en pantallas de 1400 px. Corregido: el valor no se parte y su tamaño se ajusta al ancho | bajo | Cerrado (8/11) |
| | | | | |
