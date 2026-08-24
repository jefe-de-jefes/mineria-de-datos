# Práctica 1 — Limpieza de Datos
## Minería de Datos | Dataset: NHTSA Consumer Complaints (2020–2024)

---

## 1. Elección del dataset

**Fuente:** National Highway Traffic Safety Administration (NHTSA), U.S. Department of Transportation
**URL de descarga:** https://www.nhtsa.gov/nhtsa-datasets-and-apis (sección "Complaints")
**Archivo usado:** `COMPLAINTS_RECEIVED_2020-2024.zip` (72 MB comprimido, ~312 MB descomprimido)
**Diccionario de campos:** `CMPL.txt` (51 campos documentados por NHTSA)

### Por qué este dataset

Se evaluaron tres áreas de interés personal antes de decidir: **redes/infraestructura**, **call center**, y **autos/mecánica**. Se descartó call center porque, tras investigar varias fuentes (Kaggle, data.world), no existe un dataset público de call center que cumpla simultáneamente los 5 requisitos del curso (fecha con continuidad, texto libre, numérico, categórico, 5000+ filas) — la mayoría de datasets de ese dominio son o puramente transaccionales (sin texto) o transcripciones (sin fecha/numérico). Se descartó redes por el mismo motivo: los datasets de intrusion detection casi nunca traen texto libre ni fechas con continuidad real.

Se eligió NHTSA Complaints porque:
- Cumple los 5 requisitos desde el archivo crudo, sin necesidad de combinar fuentes
- Es dato gubernamental primario, sin análisis de terceros adjunto (evita cualquier riesgo de plagio de notebooks resueltos de Kaggle)
- Conecta con interés genuino en mecánica automotriz (experiencia personal con vehículo propio de alto kilometraje)

### Características que cumple

| Requisito | Cumplimiento |
|---|---|
| Mínimo 4 variables | 51 columnas originales |
| Mínimo 2 numéricas | MILES, VEH_SPEED, INJURED, DEATHS, etc. |
| Mínimo 1 alfanumérica | MAKETXT, CDESCR, COMPDESC, etc. |
| Mínimo 1 fecha con continuidad | FAILDATE, DATEA, LDATE (2020–2024) |
| Mínimo 5,000 filas | 418,806 filas iniciales |

---

## 2. Arquitectura del código

El pipeline está organizado en funciones puras (una responsabilidad por función, con type hints), orquestadas desde `main()`. Cada función recibe un DataFrame y regresa un DataFrame transformado. Los diccionarios de mapeo (casos especiales de normalización) se separaron a un módulo aparte, `mappings.py`, para mantener `main.py` enfocado en lógica y no en datos de configuración.

```
main.py
├── load_columns(doc_path) → list
├── load_data(data_path, doc_path) → DataFrame
├── filter_by_product_type(df, product_type) → DataFrame
├── delete_invalid_states(df, codes) → DataFrame
├── delete_unused_columns(df) → DataFrame
├── refill_empty_object_columns(df, comment, percentage) → DataFrame
├── refill_middle_empty_columns(df, columns, comment) → DataFrame
├── clean_miles(df, column) → DataFrame
├── delete_empty_rows(df, columns) → DataFrame
├── convert_dates(df, columns) → DataFrame
├── delete_invalid_dates(df) → DataFrame
├── refill_year(df) → DataFrame
├── normalizar_marca(df, columna, specials=None) → DataFrame
├── create_column_comp(df) → DataFrame  (deriva COMP_MAIN desde COMPDESC)
└── revisar_columna(df, columna) → None (utilidad de inspección)

mappings.py
├── middle_empty_columns, columns_with_empty_rows, date_columns, invalid_states
├── specials_maketxt      (casos especiales para MAKETXT)
├── specials_mfr_name     (casos especiales para MFR_NAME)
├── specials_comp_main    (casos especiales para COMP_MAIN)
└── specials_modeltxt     (casos especiales para MODELTXT)
```

**Nota técnica:** `load_data()` usa `pd.read_csv(..., low_memory=False)` para evitar un `DtypeWarning` que aparecía en 8 columnas categóricas dispersas al leerlas por bloques. El warning no afectaba el resultado final (esas columnas ya quedaban 100% consistentes tras la limpieza), pero se resolvió de raíz por prolijidad.

---

## 3. Paso a paso del pipeline (orden de ejecución en `main()`)

### Paso 1 — Carga de datos
`load_columns()` parsea `CMPL.txt` línea por línea, detecta las líneas que definen campos (empiezan con un número seguido del nombre) y extrae los 51 nombres de columna automáticamente — evita transcripción manual y reduce error humano.

`load_data()` carga el archivo con `pd.read_csv()`, indicando `sep='\t'` (confirmado con `cat -A` que el separador real es tab, no espacio), `header=None` (el archivo no trae encabezados), y los nombres obtenidos en el paso anterior.

**Resultado:** 418,806 filas × 51 columnas.

### Paso 2 — Filtrar por tipo de producto
El dataset de NHTSA no es exclusivamente de vehículos: incluye llantas (`T`), equipo (`E`) y sillas infantiles (`C`) bajo el campo `PROD_TYPE`. Como el interés del análisis es específicamente fallas automotrices, se filtra a `PROD_TYPE == 'V'`.

**Justificación:** 412,729 de 418,806 filas (98.6%) son de vehículos — perder el 1.4% restante es una pérdida mínima y alinea el dataset con la pregunta de investigación real. Como beneficio adicional, este filtro elimina de raíz decenas de "marcas" que en realidad eran fabricantes de llantas/accesorios (Michelin, Garmin, Britax) mezcladas en la columna `MAKETXT`.

### Paso 3 — Eliminar estados inválidos
Se detectaron códigos en la columna `STATE` que no corresponden a los 50 estados + DC: territorios de EE.UU. (`PR`, `GU`, `VI`, `AS`, `MP`), direcciones militares (`AE`, `AA`, `AP`), y códigos claramente corruptos (`NN`, `CD`, `UN`, `??`, `00`). Se decidió eliminar todos estos (1,570 filas, 0.4% del dataset) para quedarse estrictamente con jurisdicción estadounidense propiamente dicha. Se conservaron intencionalmente los códigos de países asociados (`MH`, `FM`, `PW` — Islas Marshall, Micronesia, Palau) por ser jurídicamente válidos.

### Paso 4 — Eliminar columnas sin dato útil
Se eliminaron 8 columnas:
- `STATE_OF_INCIDENT`, `VEHICLE_OPERATOR`: 0% de completitud. Motivo verificado en `CMPL.txt`: estos campos se agregaron al formulario de NHTSA el 30 de abril de 2026, **después** del rango de fechas del dataset (2020–2024) — no es que falte el dato, es que el campo no existía cuando se capturaron estos registros.
- `OCCURENCES`, `PURCH_DT`, `NUM_CYLS`, `MANUF_DT`: más del 90% de nulos cada una (96.6%, 99.4%, 93.6%, 99.9% respectivamente) — se consideró que el valor informativo restante no justificaba mantenerlas.
- `DEALER_TEL`, `DEALER_ZIP`: datos de contacto del distribuidor sin relevancia para el análisis de fallas mecánicas.

### Paso 5 — Rellenar columnas categóricas dispersas (detección automática)
Se detectan automáticamente (sin lista manual) las columnas de tipo `object` con más del 50% de nulos, y se rellenan con el texto `"No aplica"`. Afectó a: `DRIVE_TRAIN`, `FUEL_SYS`, `FUEL_TYPE`, `TRANS_TYPE`, `TIRE_SIZE`, `LOC_OF_TIRE`, `TIRE_FAIL_TYPE`, `SEAT_TYPE`, `RESTRAINT_TYPE`, `ORIG_EQUIP_YN`.

**Justificación:** estas columnas no son nulas por error de captura, sino por diseño del formulario — solo aplican a un tipo específico de queja (ej. `TIRE_SIZE` únicamente si la queja es sobre llantas). El vacío en sí es información ("este campo no correspondía a este tipo de queja").

### Paso 6 — Rellenar columnas con nulos moderados (lista explícita)
Columnas con proporción baja de nulos (~1.3%): `VIN`, `ORIG_OWNER_YN`, `ANTI_BRAKES_YN`, `CRUISE_CONT_YN`, `VEHICLES_TOWED_YN`. Se rellenan con `"Desconocido"` en vez de `"No aplica"`, porque aquí la ausencia probablemente se debe a que el consumidor no proporcionó el dato, no a que el campo no aplicara.

**Nota de diseño:** se usó lista explícita en vez de detección automática por umbral, porque un umbral bajo (~1%) podría capturar columnas no deseadas junto con las 5 columnas objetivo — se prefirió control manual consciente sobre automatización en este caso específico.

### Paso 7 — Limpieza de outliers en millaje (`MILES`)
Se calculó el rango intercuartílico (IQR): Q1 = 27,000, Q3 = 110,000, IQR = 83,000, límite estadístico puro = Q3 + 1.5×IQR = **234,500 millas**.

**Decisión:** se usó un límite ajustado de **400,000 millas** en vez del límite estadístico puro, porque el límite de 234,500 descartaría vehículos reales de alto kilometraje en circulación. Se eliminaron 393 filas con MILES > 400,000 (0.26% de los registros con dato de millaje).

Los 268,754 registros sin dato de millaje (64% del total) se dejaron como `NaN` — no se rellenaron con media/mediana porque distorsionaría significativamente el análisis dado el volumen, y no se eliminaron las filas porque conservan información valiosa en otras columnas (marca, descripción, componente).

### Paso 8 — Eliminar filas con nulos mínimos
Columnas con nulos casi insignificantes (2 a 25 filas de +400,000): `MFR_NAME`, `MAKETXT`, `MODELTXT`, `YEARTXT`, `COMPDESC`, `CITY`, `CDESCR`, `PROD_TYPE`. Se eliminaron las filas afectadas (50 filas totales, considerando solapamiento entre columnas) en vez de rellenar, porque el costo de perder esas filas es despreciable frente al beneficio de mantener columnas centrales del análisis 100% completas.

### Paso 9 — Conversión de fechas
`FAILDATE`, `DATEA`, `LDATE` vienen como enteros en formato `YYYYMMDD` (ej. `20230415`). Se convirtieron a `datetime64` con `pd.to_datetime(..., format='%Y%m%d', errors='coerce')`. No se generó ningún `NaT` nuevo — todas las fechas originales estaban bien formadas.

### Paso 10 — Eliminación de fechas lógicamente inválidas
Se detectaron y eliminaron dos tipos de inconsistencia:
- 6 filas donde `FAILDATE > LDATE` (el incidente se reportó *antes* de que ocurriera — imposible).
- 78 filas donde `FAILDATE < 1995-01-01` (el propio diccionario de NHTSA indica que el sistema de captura de quejas inicia el 1 de enero de 1995; fechas anteriores son sospechosas de error de captura).

### Paso 11 — Año de modelo desconocido (`YEARTXT`)
NHTSA usa el código `9999` como placeholder para "año desconocido" (documentado en `CMPL.txt`). Se detectaron 5,920 filas con ese valor. Se decidió **convertirlo a `NaN`** (no eliminar la fila) — mismo criterio que `MILES`: preservar el resto de la información de la fila.

### Paso 12 — Normalización de marcas (`MAKETXT` y `MFR_NAME`)
**Normalización automática:** mayúsculas, guiones convertidos a espacios, espacios múltiples colapsados a uno solo. Redujo `MAKETXT` de 358 a 356 marcas únicas (ej. `MERCEDES-BENZ`/`MERCEDES BENZ`/`MERCEDES-BENz` → una sola entrada; `CAN-AM` → `CAN AM`; `HARLEY-DAVIDSON` → `HARLEY DAVIDSON`).

**Diccionario manual de casos investigados** (no capturados por normalización automática, por ser sinónimos con texto distinto):
- `UNKNOWN MANUFACTURER` → `UNKNOWN`
- `4-STAR TRAILER` → `4 STAR` (verificado: ambos nombres corresponden a la misma empresa, 4-Star Trailers Inc., Oklahoma City, fundada 1984)
- `LIVIN' LITE` → `LIVIN LITE`

Para `MFR_NAME`, además:
- `REDUNDANT POLARIS INDUSTRIES, INC.` → `POLARIS` (error de captura evidente: la palabra "redundant" quedó pegada al nombre)
- Variantes DBA, sufijos corporativos (INC./LTD.) y aclaraciones entre paréntesis de la misma entidad legal (Mercedes-Benz, Bentley, Chrysler, Mazda) — unificadas.

**Decisión explícita de NO fusionar:** subdivisiones de producto que podrían representar líneas de manufactura o plataformas distintas dentro de la misma marca (ej. `JAYCO FIFTH WHEEL` vs `JAYCO TRAVEL TRAILER`, `THOR` vs `THOR MOTOR COACH`, `STARCRAFT` vs sus variantes, `MERCEDES-BENZ` vs `MERCEDES MAYBACH`). Razón: en datos de seguridad vehicular, un defecto puede estar aislado a una planta o plataforma específica; fusionar subdivisiones sin evidencia haría perder esa capacidad de detección de patrones.

### Paso 13 — Normalización de `COMPDESC` (componente de la falla) y creación de `COMP_MAIN`
`COMPDESC` viene estructurada jerárquicamente por NHTSA usando `:` como separador (ej. `"SERVICE BRAKES:HYDRAULIC:MASTER CYLINDER"`). Se creó una columna derivada, `COMP_MAIN`, que extrae únicamente la categoría principal (la parte antes del primer `:`), para facilitar análisis agregados por tipo general de falla sin perder el detalle completo, que permanece intacto en `COMPDESC`.

Sobre `COMP_MAIN` se aplicó normalización con diccionario manual (`specials_comp_main`), agrupando subtipos que se consideró aportan más como categoría única que separados (ej. `SERVICE BRAKES, HYDRAULIC/ELECTRIC/AIR` → `SERVICE BRAKES`), y unificando variantes de "desconocido" (`UNKNOWN OR OTHER`, `OTHER/I AM NOT SURE`, `NONE` → `UNKNOWN`). El detalle de subtipo de sistema de frenos sigue disponible íntegro en `COMPDESC` para quien lo necesite.

### Paso 14 — Normalización de `MODELTXT`
Se aplicó normalización automática (mismo mecanismo que `MAKETXT`/`MFR_NAME`) más un diccionario extenso de casos especiales (`specials_modeltxt`), que cubre:
- **Errores de captura con prefijo "REDUNDANT"/"DUPLICATE"** (mismo patrón detectado en `MFR_NAME`): ej. `REDUNDANT ALTIMA` → `ALTIMA`.
- **Typos y caracteres parásitos**: ej. `DURANGO1` → `DURANGO`, `!MX 5` → `MX 5`.
- **Marca registrada por error en el campo de modelo, sin modelo real capturado**: mapeadas a `UNKNOWN` (ej. una fila donde `MODELTXT` solo dice `"FORD"` sin especificar cuál modelo).
- **Categorías genéricas de tipo de vehículo sin modelo específico** (ej. `TRAILER`, `BUS`, `PICKUP` sueltos): mapeadas a `UNKNOWN`.

**Decisión explícita de NO tocar:** códigos de generación/plataforma entre paréntesis (ej. `911 (997)`, `BOXSTER (987)`) se dejaron intactos — representan información real de generación del modelo, no ruido de captura.

Resultado: 2,329 modelos únicos sobre 411,156 filas. Los modelos más frecuentes (`ESCAPE`, `F 150`, `1500`, `FUSION`, `EXPLORER`) son coherentes con los de mayor volumen de venta en EE.UU. en el periodo.

### Nota sobre el alcance de "vehículo" (`PROD_TYPE == 'V'`)
Se confirmó que la categoría "Vehículo" de NHTSA es más amplia que "automóvil de pasajeros": incluye motocicletas, casas rodantes (RVs), remolques, buses escolares y equipo montado sobre chasís (grúas, plataformas aéreas). Se decidió conservar el dataset así, sin acotar más, ya que el interés del análisis (fallas mecánicas y de seguridad) aplica igualmente a estas categorías, y NHTSA no ofrece una columna directa para distinguir "auto de pasajeros" de otros vehículos motorizados sin inferencia adicional.

---

## 4. Verificaciones adicionales realizadas

- **Duplicados:** 0 filas duplicadas en el dataset completo (verificado con `df.duplicated().sum()`).
- **Valores negativos:** se confirmó que `MILES`, `VEH_SPEED`, `INJURED`, `DEATHS` no contienen valores negativos (mínimo = 0 en las cuatro).
- **Ceros:** se evaluó que los ceros en `INJURED`/`DEATHS` (la gran mayoría de registros) y en `VEH_SPEED` tienen sentido lógico — la mayoría de quejas no involucran heridos/muertes, y muchas ocurren con el vehículo detenido o en componentes no relacionados con movimiento (ej. sillas infantiles, sistemas eléctricos).
- **Catálogo de `CMPL_TYPE`:** se verificó contra la lista oficial de 15 códigos documentados en `CMPL.txt`; los 8 valores presentes en el dataset son todos válidos.

---

## 5. Resultado final del pipeline

| Etapa | Filas | Columnas |
|---|---|---|
| Carga inicial | 418,806 | 51 |
| Filtro por tipo de producto (solo vehículos) | 412,729 | 51 |
| Filtro de estados válidos | ~411,159 | 51 |
| Eliminación de columnas inútiles | ~411,159 | 45 |
| Eliminación filas nulos mínimos | ~411,109 | 45 |
| Filtro outliers de millaje | ~410,716 | 45 |
| Eliminación fechas inválidas (6 + 78) | **411,156*** | 45 |

*El orden exacto de aplicación de filtros hace que el número final observado en ejecución sea 411,156 filas × 45 columnas — muy por encima del mínimo de 5,000 filas exigido por el curso.

---

## 6. Nota sobre uso de IA

Este código fue desarrollado bajo la modalidad de Pair Programming (Conductor/Navegante) permitida por el curso: toda la lógica y decisiones fueron escritas y tomadas por el estudiante; la asistencia de IA se limitó a depuración conceptual de errores, sugerencias de sintaxis/librerías, y preguntas guía para que el estudiante llegara a sus propias conclusiones e interpretaciones. Ningún hallazgo, conclusión de negocio, ni interpretación de resultados fue generado por la IA — cada decisión (umbral de outliers, qué fusionar y qué no, qué eliminar vs. rellenar) fue evaluada y decidida por el estudiante con su propio criterio, incluyendo instancias donde se cuestionaron y rechazaron sugerencias automáticas por falta de justificación suficiente.
