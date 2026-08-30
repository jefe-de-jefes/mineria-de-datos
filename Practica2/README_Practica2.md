# Práctica 2 — Estadística Descriptiva
## Minería de Datos | Dataset: NHTSA Consumer Complaints (2020–2024)

---

## 1. Objetivo de la práctica

Aplicar estadística descriptiva, identificar entidades y relaciones, trazar su diagrama y obtener métricas de datos agrupados."

---

## 2. Arquitectura del código

`Practica2/main.py` carga el CSV limpio (reconvirtiendo las columnas de fecha con `parse_dates`, ya que el formato CSV no preserva tipos de dato como `datetime64`) y genera 4 tablas mediante `pandas` + `tabulate`, sin necesidad de repetir el pipeline de limpieza de la Práctica 1.

```python
df = pd.read_csv('../data/nhtsa_clean.csv', parse_dates=['FAILDATE', 'DATEA', 'LDATE'])
```

---

## 3. Estadística descriptiva

Se aplicaron las funciones de agregación básicas (min, max, media, mediana, moda, desviación estándar, asimetría, kurtosis) sobre las 4 columnas numéricas más relevantes: `MILES`, `VEH_SPEED`, `INJURED`, `DEATHS`.

**Nota metodológica:** antes de calcular estas métricas, se detectaron y limpiaron valores centinela adicionales no identificados en la Práctica 1 (`INJURED == 99`, `DEATHS == 99`, `VEH_SPEED` por encima de 200 mph) — ver detalle en la sección 6 del README de Práctica 1. Esto se hizo retroactivamente, regenerando el CSV limpio, antes de calcular las estadísticas de esta práctica.

| Variable | Count | Media | Mediana | Máx | Moda | Asimetría | Kurtosis |
|---|---|---|---|---|---|---|---|
| MILES | 149,073 | 73,966 | 68,000 | 400,000 | 0 | 0.76 | 0.56 |
| VEH_SPEED | 237,529 | 33.4 | 35 | 200 | 0 | 0.06 | -1.28 |
| INJURED | 411,152 | 0.038 | 0 | 60 | 0 | 40.03 | 5,829.79 |
| DEATHS | 411,151 | 0.002 | 0 | 45 | 0 | 274.91 | 88,929.7 |

### Interpretación

**MILES** tiene asimetría positiva (0.76): el 75% de los vehículos reporta menos de 110,000 millas al momento de la falla, pero existe una cola de vehículos de alto kilometraje que estira la media (73,966) por encima de la mediana (68,000) — ambas métricas cuentan la misma historia desde ángulos distintos.

**VEH_SPEED** muestra kurtosis negativa (-1.28), es decir, una distribución más plana que una normal. 

**INJURED y DEATHS** tienen mediana, moda y Q75 en 0 — la gran mayoría de quejas no involucra heridos ni muertes (solo 2.73% de las quejas reportan al menos 1 herido, y 0.09% al menos 1 muerte). Esto produce asimetría y kurtosis matemáticamente extremas que **no aportan valor interpretativo** en este caso: son un efecto esperado de que casi todos los valores sean idénticos (0) con solo un puñado de casos altos (hasta 60 heridos, 45 muertes), no un error en la limpieza ni en el cálculo. Se decidió reportarlas de todos modos por transparencia metodológica, pero se advierte explícitamente que no deben interpretarse como "la distribución es muy sesgada" en el sentido útil que sí aplica a `MILES`.

---

## 4. Identificar entidades y relaciones

Se identificaron 4 entidades naturales dentro del dataset (originalmente una sola tabla plana de 44 columnas):

| Entidad | Atributos clave |
|---|---|
| **VEHÍCULO** | VIN (PK), MAKETXT, MODELTXT, YEARTXT |
| **QUEJA** | CMPLID (PK), FAILDATE, CDESCR, CMPL_TYPE, MILES, VEH_SPEED, INJURED, DEATHS |
| **COMPONENTE** | COMP_MAIN (PK), COMPDESC |
| **UBICACIÓN** | STATE (PK), CITY |


### Relaciones

Las tres relaciones son de tipo **uno a muchos (1:N)**, todas centradas en la entidad Queja:

- **Vehículo (1) → Queja (N)**: un mismo vehículo (VIN) puede tener múltiples quejas reportadas a lo largo del tiempo, pero cada queja se refiere a un solo vehículo.
- **Componente (1) → Queja (N)**: un componente (ej. "Service Brakes") puede aparecer en miles de quejas distintas, pero cada queja se asocia a un único componente principal.
- **Ubicación (1) → Queja (N)**: una ubicación (ciudad/estado) puede tener múltiples quejas de distintos consumidores, pero cada queja ocurre en una sola ubicación.

---

## 5. Diagrama entidad-relación

Diagrama construido en PlantUML (notación IE / pata de cuervo), archivo fuente en [`diagrama_er.puml`](./diagrama_er.puml), exportado como [`diagrama_er.png`](./diagrama_er.png).

```
VEHICULO ||--o{ QUEJA : "tiene"
COMPONENTE ||--o{ QUEJA : "clasifica"
UBICACION ||--o{ QUEJA : "ocurre en"
```

---

## 6. Métricas de datos agrupados

Se generaron 3 tablas usando `groupby().agg()` (patrón Map-Reduce: se agrupan los datos en subconjuntos por categoría, y se reduce cada subconjunto con una función de agregación).

### Tabla 1 — Top 10 modelos por % de quejas con muerte

Filtrado a modelos con 100+ quejas totales (para evitar porcentajes poco confiables sobre muestras chicas). Incluye velocidad promedio de las quejas con muerte de cada modelo.

F-PACE (Jaguar), A5 (Audi) y RAM 3500 encabezan con 2.5–2.7% de sus quejas asociadas a muerte, con solo 3–4 casos absolutos cada uno — **muestra demasiado pequeña para generalizar**. El caso de A5 no reporta velocidad en ninguna de sus 3 muertes (`NaN`), por lo que no se puede comparar su velocidad promedio contra los demás modelos.

### Tabla 2 — Top 10 marcas por conteo de quejas con muerte

FORD (42 casos, 10.9%), TESLA (41, 10.6%), CHEVROLET (40, 10.4%) y TOYOTA (39, 10.1%) concentran ~42% de las 386 quejas con muerte totales.

**Hallazgo:** Tesla aparece en segundo lugar, con una proporción comparable a Ford, Chevrolet y Toyota — fabricantes con décadas más de historia y volumen de ventas sustancialmente mayor. Sin datos de volumen de ventas por marca para normalizar esta comparación, no se puede concluir que Tesla sea tan riesgoso como estas marcas; la proporción amerita investigación adicional (ej. cruzando con datos externos de ventas anuales) en una práctica futura.

### Tabla 3 — Top 5 modelos por componente principal, en quejas con `MILES == 0`

De las 4,511 quejas reportadas sin ningún kilometraje registrado, el componente más común es AIR BAGS (18.6%), seguido de SERVICE BRAKES (12.1%) y ELECTRICAL SYSTEM (11.2%) — sugiere defectos de manufactura detectables antes de cualquier uso real, no desgaste por kilometraje.

**Hallazgo — Air Bags concentrado en plataforma GM:** los 3 modelos con más quejas de air bags a 0 millas son TRAVERSE (83), ENCLAVE (62) y ACADIA (53) — las tres son SUVs medianas de General Motors construidas sobre una plataforma compartida. Esto sugiere un problema específico de esa plataforma o proceso de ensamblaje, no un patrón genérico de "las SUVs fallan más en air bags".

**Hallazgo — Frenos concentrado en compactos/sedanes:** TUCSON (81), ELANTRA (40) y FUSION (34) lideran las quejas de frenos a 0 millas — dos de Hyundai y uno de Ford, sin plataforma compartida evidente, lo que sugiere que este patrón está más relacionado con el segmento de vehículo que con un fabricante único.

**Nota:** BOLT EV aparece en el top de fallas de sistema eléctrico — al ser un vehículo eléctrico, sus fallas "eléctricas" probablemente tienen una causa raíz distinta (batería/motor) a la de un vehículo de combustión, por lo que no debería agruparse conceptualmente igual que el resto sin mayor investigación.

---

## 7. Limitaciones generales

Ninguna de las comparaciones de esta práctica controla por volumen de ventas, años en el mercado, ni tipo de uso del vehículo. Son observaciones descriptivas de este dataset de quejas — no conclusiones causales sobre seguridad vehicular. Cualquier afirmación tipo "la marca X es más peligrosa" requeriría datos externos de exposición (unidades vendidas, millas totales recorridas por flota) que no están disponibles en este dataset.

---


