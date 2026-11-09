import pandas as pd
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rutas import DASHBOARD

VARIABLES = ['gravedad', 'crash', 'fire']
MODELO, ANIO = 'SILVERADO', 2020          # cambia por el caso que quieras revisar

g = pd.read_csv(DASHBOARD / 'grupos.csv')
g = g[g['semaforo'] != 'Sin datos suficientes']

print('variables del K-Means:', VARIABLES)
print(g[VARIABLES].describe().round(3))

print(g.groupby('semaforo')[VARIABLES + ['quejas']].agg(['mean', 'min', 'max']).round(3))

fila = g[(g['MODELTXT'] == MODELO) & (g['YEARTXT'] == ANIO)]
print(fila[['MAKETXT', 'MODELTXT', 'YEARTXT', 'quejas', 'semaforo'] + VARIABLES])

# distancia de ese caso al centro de cada nivel, en las variables estandarizadas
z = (g[VARIABLES] - g[VARIABLES].mean()) / g[VARIABLES].std(ddof=0)
centros = z.groupby(g['semaforo']).mean()
for i in fila.index:
    print((centros - z.loc[i]).pow(2).sum(axis=1).pow(0.5).round(2))
