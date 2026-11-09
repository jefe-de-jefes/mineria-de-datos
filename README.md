# Minería de Datos

**Alumno:** Luis Fernando Segobia Torres 2177528
**Carrera:** Licenciatura en Ciencias Computacionales
**Facultad:** Facultad de Ciencias Físico Matemáticas (FCFM), UANL
**Semestre:** 7mo semestre
**Materia:** Minería de Datos

---

## Sobre este repositorio

Este repositorio contiene las prácticas y el proyecto integrador (PIA) de la materia de Minería de Datos, desarrollados de forma incremental a lo largo del semestre sobre un mismo conjunto de datos, tal como lo pide el curso.

## Dataset

**NHTSA Consumer Complaints Database (2020–2024)**
Fuente: National Highway Traffic Safety Administration (NHTSA), U.S. Department of Transportation
Descarga: [nhtsa.gov/nhtsa-datasets-and-apis](https://www.nhtsa.gov/nhtsa-datasets-and-apis)

Base de datos pública con quejas de seguridad reportadas por consumidores sobre vehículos, componentes y fallas mecánicas en Estados Unidos. Se eligió este dataset por interés genuino en mecánica automotriz, y porque cumple desde el archivo crudo los requisitos del curso: más de 5,000 filas, variables numéricas y categóricas, texto libre, y fechas con continuidad temporal adecuada para series de tiempo.

El detalle completo de la elección del dataset, la limpieza aplicada y la justificación de cada decisión está documentado en [`Practica1/README_Practica1.md`](./Practica1/README_Practica1.md).

## Contenido

| Carpeta | Tema |
|---|---|
| `Practica1/` | Limpieza de datos |
| `Practica2/` | Estadística descriptiva |
| `Practica3/` | Visualización de datos |
| `Practica4/` | Pruebas estadísticas |
| `Practica5/` | Modelos lineales y correlación |
| `Practica6/` | Clasificación de datos (KNN) |
| `Practica7/` | Agrupamiento de datos (K-Means) |
| `Practica8/` | Pronóstico (Forecasting) |
| `Practica9/` | Análisis de texto |
| `PIA/` | Proyecto integrador: riesgo de quejas por marca, modelo y año |

## PIA

Clasificador de texto para rellenar el componente faltante de las quejas, K-Means para agrupar las combinaciones marca-modelo-año en un semáforo de riesgo (Verde, Amarillo, Rojo y Alerta de fuego), prueba de Kruskal-Wallis entre niveles y un dashboard en Data Studio pensado para quien va a comprar un auto usado.

Dashboard: [Data Studio](https://datastudio.google.com/reporting/226addaa-9c08-432d-88c9-bb28a82a7a86)

## Estructura del repositorio

```
mineria-de-datos/
├── README.md
├── data/
│   └── nhtsa_clean.csv
├── Practica1/ ... Practica9/
├── PIA/
│   ├── main.py
│   ├── scripts/
│   ├── resultados/
│   ├── dashboard/
│   └── img/
├── .gitattributes
└── .gitignore
```

Cada práctica tiene su propia carpeta con su código y, cuando aplica, su `README_PracticaN.md` y una carpeta `img/` con las gráficas.

## Cómo reproducir

El dataset limpio se versiona con Git LFS en `data/nhtsa_clean.csv`. Para regenerarlo desde el archivo crudo:

```bash
cd Practica1
python3 main.py
```

Esto procesa el archivo crudo `COMPLAINTS_RECEIVED_2020-2024.txt` con `pandas` y genera el dataset limpio en `../data/nhtsa_clean.csv`.

Cada práctica posterior lee `../data/nhtsa_clean.csv`. El PIA se corre desde su carpeta con `python3 main.py`; las instrucciones están en [`PIA/README_PIA.md`](./PIA/README_PIA.md).

Los archivos `.csv` y `.txt` se guardan con Git LFS, así que hay que tener `git lfs` instalado antes de clonar.

## Nota sobre uso de IA

En cumplimiento con la política del curso, el uso de asistentes de IA en este repositorio se limita a la modalidad de Pair Programming: apoyo en depuración de errores, sugerencias de sintaxis y librerías, y preguntas guía. Todas las decisiones de limpieza, interpretación de datos y análisis fueron tomadas por el alumno con su propio criterio.
