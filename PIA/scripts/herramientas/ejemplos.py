import pandas as pd
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rutas import DASHBOARD
pd.set_option('display.width', 200)

MARCA = None    # por ejemplo 'MAZDA' para ver solo una marca; None = todas

g = pd.read_csv(DASHBOARD / 'grupos.csv')
if MARCA:
    g = g[g['MAKETXT'] == MARCA]

cols = ['MAKETXT', 'MODELTXT', 'YEARTXT', 'quejas', 'gravedad', 'crash', 'fire']

for nivel in ['Verde', 'Amarillo', 'Rojo', 'Alerta de fuego', 'Sin datos suficientes']:
    sub = g[g['semaforo'] == nivel]
    print(f'\n=== {nivel} | {len(sub)} grupos')
    if sub.empty:
        continue
    print('con más quejas:')
    print(sub.sort_values('quejas', ascending=False)[cols].head(5).round(3).to_string(index=False))
    print('al azar:')
    print(sub.sample(min(3, len(sub)), random_state=1)[cols].round(3).to_string(index=False))
