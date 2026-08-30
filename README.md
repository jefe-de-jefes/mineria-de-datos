# Minería de Datos

**Alumno:** Luis
**Carrera:** Licenciatura en Ciencias Computacionales
**Facultad:** Facultad de Ciencias Físico Matemáticas (FCFM), UANL
**Semestre:** 7mo semestre
**Materia:** Minería de Datos

---

## Sobre este repositorio

Este repositorio contiene las prácticas de la materia de Minería de Datos, desarrolladas de forma incremental a lo largo del semestre sobre un mismo conjunto de datos, tal como lo pide el curso.

## Dataset

**NHTSA Consumer Complaints Database (2020–2024)**
Fuente: National Highway Traffic Safety Administration (NHTSA), U.S. Department of Transportation
Descarga: [nhtsa.gov/nhtsa-datasets-and-apis](https://www.nhtsa.gov/nhtsa-datasets-and-apis)

Base de datos pública con quejas de seguridad reportadas por consumidores sobre vehículos, componentes y fallas mecánicas en Estados Unidos. Se eligió este dataset por interés genuino en mecánica automotriz, y porque cumple desde el archivo crudo los requisitos del curso: más de 5,000 filas, variables numéricas y categóricas, texto libre, y fechas con continuidad temporal adecuada para series de tiempo.

El detalle completo de la elección del dataset, la limpieza aplicada y la justificación de cada decisión está documentado en [`Practica1/README_Practica1.md`](./Practica1/README_Practica1.md).

## Estructura del repositorio

```
mineria-de-datos/
├── README.md                      ← este archivo
├── Practica1/
│   ├── main.py                    ← pipeline de carga y limpieza de datos
│   ├── mappings.py                ← diccionarios de normalización y listas de configuración
│   ├── README_Practica1.md        ← documentación detallada de la Práctica 1
│   ├── CMPL.txt                   ← diccionario de campos oficial de NHTSA
│   └── COMPLAINTS_RECEIVED_2020-2024.txt   ← dataset crudo (vía Git LFS)
├── .gitattributes                 ← configuración de Git LFS
└── .gitignore
```

Cada práctica futura se organiza en su propia carpeta (`Practica2/`, `Practica3/`, etc.), siguiendo la misma convención.

## Cómo reproducir

El dataset limpio no se versiona en este repositorio (solo el dataset crudo y el código que lo procesa, siguiendo buenas prácticas de control de versiones). Para regenerarlo:

```bash
cd Practica1
python3 main.py
```

Esto descarga las dependencias necesarias vía `pandas`, procesa el archivo crudo `COMPLAINTS_RECEIVED_2020-2024.txt`, y genera el dataset limpio en `../data/nhtsa_clean.csv`.

## Nota sobre uso de IA

En cumplimiento con la política del curso, el uso de asistentes de IA en este repositorio se limita a la modalidad de Pair Programming: apoyo en depuración de errores, sugerencias de sintaxis y librerías, y preguntas guía. Todas las decisiones de limpieza, interpretación de datos y análisis fueron tomadas por el alumno con su propio criterio.
