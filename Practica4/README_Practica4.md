# Práctica 4 — Pruebas Estadísticas
## Minería de Datos | Dataset: NHTSA Consumer Complaints (2020–2024)

## 1. Objetivo

Comprobar si existen diferencias reales entre grupos usando ANOVA/prueba t o Kruskal-Wallis, revisando primero si los supuestos de cada prueba se cumplen. La decisión de qué prueba reportar no se asume de entrada: depende de lo que arroje la prueba de Levene y de lo que ya sabíamos de la forma de los datos desde la Práctica 2.

## 2. Qué se comparó y por qué

Se eligieron dos comparaciones, ambas conectadas con hallazgos de prácticas anteriores en vez de variables elegidas al azar:

| Comparación | Variable numérica | Grupos | Viene de |
|---|---|---|---|
| 1 | VEH_SPEED | CRASH (Y/N) | El boxplot de la Práctica 3 |
| 2 | MILES | COMP_MAIN (11 componentes) | El hallazgo de air bags a 0 millas en la Práctica 2 |

Para la Comparación 2 se usó el mismo filtro de la Práctica 3 (componentes con 5,000 quejas o más), así los grupos pequeños no meten ruido a la comparación.

## 3. Cómo se hizo

Primero se contó cuántos datos servibles había por grupo (quitando los `NaN`), para no correr una prueba sobre una muestra insuficiente. Luego se aplicó Levene para ver si las varianzas eran parecidas entre grupos. Con el tamaño de muestra que maneja este dataset, un test de normalidad tipo Shapiro-Wilk casi siempre va a rechazar la normalidad sin decir mucho útil, así que para eso se usó lo que ya se había calculado en la Práctica 2 (asimetría y kurtosis).

Se corrieron las dos versiones de cada prueba — paramétrica y no paramétrica — y al final se reportó cuál de las dos es la que realmente aplica según lo que dijo Levene. También se calculó tamaño de efecto (Cohen's d y eta cuadrado), porque con cientos de miles de filas hasta una diferencia mínima sale "significativa" y eso por sí solo no dice si importa en la práctica.

## 4. Cuántos datos había por grupo

**VEH_SPEED según CRASH**

| CRASH | n |
|---|---|
| N | 223,182 |
| Y | 14,347 |

**MILES según COMP_MAIN**

| Componente | n |
|---|---|
| ENGINE | 22,071 |
| ELECTRICAL SYSTEM | 17,371 |
| POWER TRAIN | 16,914 |
| STEERING | 12,284 |
| SERVICE BRAKES | 10,730 |
| UNKNOWN | 9,627 |
| FUEL SYSTEM | 8,716 |
| AIR BAGS | 7,304 |
| STRUCTURE | 6,555 |
| VISIBILITY | 5,445 |
| ENGINE AND ENGINE COOLING | 5,304 |

Todos los grupos están muy por arriba del mínimo de 30 casos que se suele pedir para confiar en este tipo de prueba.

## 5. VEH_SPEED según CRASH

Levene dio p<0.0001, así que las varianzas no son iguales entre los dos grupos. En términos prácticos, eso quiere decir que la velocidad no se comporta parejo entre quejas con choque y sin choque: en un grupo hay más variación que en el otro, y por eso no se puede usar directamente el t-test como si ambos grupos fueran igual de "dispersos".

Las medias: 33.67 mph sin choque, 28.92 mph con choque. Ambas pruebas (t de Welch y Mann-Whitney) salieron con p prácticamente cero, o sea que la diferencia entre esos dos números no es casualidad ni ruido de la muestra. Pero el Cohen's d de -0.183 pone las cosas en perspectiva: es un efecto pequeño. Estadísticamente hay diferencia, pero en la calle esos 5 mph de diferencia entre un grupo y otro no son gran cosa — no es que un grupo vaya a 80 y el otro a 20.

Como `VEH_SPEED` ya mostraba una distribución no normal en la Práctica 2, y aquí Levene confirma que las varianzas tampoco son homogéneas, la prueba que vale reportar es Mann-Whitney, no el t-test clásico.

Lo curioso del resultado es que va al revés de lo que uno esperaría: las quejas con choque reportan menos velocidad, no más. Si alguien pensaba que "a mayor velocidad, mayor riesgo de choque" iba a salir clarísimo en los números, aquí no fue así. No hay que leer esto como que manejar rápido es más seguro — el dataset son quejas que la gente decidió reportar a NHTSA, no un registro completo de todos los accidentes que ocurren, y puede haber sesgo en qué tipo de eventos termina reportándose. Una explicación posible es que los choques capturados aquí sean más de maniobras a baja velocidad, como tráfico o estacionamiento, mientras que las quejas sin choque incluyen fallas detectadas en carretera yendo a velocidad de crucero, donde el auto falla pero no llega a impactar nada. Es una hipótesis, no una conclusión cerrada.

## 6. MILES según COMP_MAIN

Levene también dio p<0.0001 aquí, varianzas distintas entre los 11 componentes.

Mediana de MILES por componente, de menor a mayor:

| Componente | Mediana MILES |
|---|---|
| VISIBILITY | 31,000 |
| UNKNOWN | 54,000 |
| ELECTRICAL SYSTEM | 58,000 |
| SERVICE BRAKES | 63,000 |
| STRUCTURE | 65,000 |
| FUEL SYSTEM | 70,000 |
| POWER TRAIN | 75,000 |
| AIR BAGS | 75,000 |
| STEERING | 80,500 |
| ENGINE | 81,000 |
| ENGINE AND ENGINE COOLING | 86,141 |

ANOVA y Kruskal-Wallis salieron con p prácticamente cero, eta cuadrado de 0.0276. Como `MILES` ya tenía asimetría de 0.76 desde la Práctica 2, y Levene rechaza homocedasticidad, la prueba que corresponde reportar es Kruskal-Wallis.

El eta cuadrado tan bajo dice algo importante en términos simples: saber en qué componente falló el auto casi no ayuda a predecir a cuántas millas va a fallar. El componente explica menos del 3% de esa variación. Dentro de cada categoría hay autos que fallan rapidísimo y otros que aguantan muchísimo, y esa mezcla es tan grande que opaca cualquier patrón general entre componentes.

Dicho eso, con las medianas sí se ve algo consistente con lo que cualquiera esperaría de un auto. Visibilidad, o sea limpiaparabrisas, luces, espejos, es lo que falla más pronto, con mediana de 31,000 millas — tiene sentido, son piezas expuestas todos los días al sol, la lluvia y el uso constante. En el otro extremo está motor y sistema de enfriamiento, con mediana de 86,141 millas, y eso también coincide con la fama que tiene el motor de ser de las partes más resistentes del auto si se le da mantenimiento.

Lo que no cuadra tan fácil es air bags. En la Práctica 2 había salido como el componente más frecuente en quejas a 0 millas, es decir, fallas que aparecen antes de que el auto siquiera se use. Pero aquí su mediana de 75,000 millas lo deja en un rango medio-alto, casi igual que power train, como si fuera una pieza que dura bastante. La explicación más probable es que air bags no tiene un solo tipo de falla sino dos comportamientos mezclados: unos son defectos de fábrica que se detectan desde el primer día, y otros son fallas normales que aparecen años después por desgaste del componente. Al calcular una sola mediana, esas dos historias se combinan en un número que no representa bien a ninguna de las dos, y por eso el patrón que se veía clarísimo en la Práctica 2 aquí prácticamente desaparece.

## 7. Qué le sirve a un conductor de esto

Alguien buscando comprar un auto usado puede sacar algo concreto de la Comparación 2: conviene revisar con más cuidado visibilidad, sistema eléctrico y frenos aunque el kilometraje sea relativamente bajo, porque son los componentes que estadísticamente fallan más temprano en este dataset. Motor y enfriamiento parecen aguantar más, así que ahí el riesgo de una falla temprana es menor.

Con air bags conviene un paso extra: dado que parte de esas fallas ocurren desde el primer día y no por desgaste, vale la pena meter la marca y modelo del auto a la base de recalls de NHTSA en nhtsa.gov/recalls antes de comprarlo, porque puede que ya exista una campaña de recall abierta para ese defecto específico. El caso más conocido de la industria es el de Takata, aunque este dataset no permite confirmar si es esa la causa de lo que aparece aquí.

Lo de la velocidad y los choques no es un dato para cambiar la forma de manejar. El efecto es chico y el dataset no aguanta una lectura de causa y efecto, así que se queda como un hallazgo documentado, no como una recomendación.

## 8. Limitaciones

Los tamaños de efecto (d=-0.183, eta²=0.0276) son chicos: hay diferencia estadística, pero ninguna de las dos variables predice gran cosa por sí sola, queda mucha variación individual sin explicar.

Kruskal-Wallis dice que hay diferencia entre al menos algunos de los 11 componentes, pero no dice cuáles pares. Para confirmar, por ejemplo, que visibilidad realmente difiere de motor y enfriamiento, haría falta una prueba post-hoc como Dunn's test, que no se corrió en esta práctica.

El dataset son quejas que la gente decidió reportar, no todos los eventos reales de falla o choque que existen. Los patrones que aparecen aquí describen lo que llegó a NHTSA, no necesariamente a todos los autos en circulación.

## 9. Nota sobre uso de IA

Este código se desarrolló bajo la modalidad de Pair Programming (Conductor/Navegante) permitida por el curso: la lógica y las decisiones fueron mías; la IA se usó para depurar errores puntuales, sugerir sintaxis o librerías, y hacer preguntas guía. Ningún hallazgo ni interpretación salió de la IA — qué prueba reportar como válida, qué comparaciones elegir, y qué tan relevante es cada efecto lo decidí yo con mi propio criterio.
