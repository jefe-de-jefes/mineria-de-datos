import pandas as pd
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rutas import DASHBOARD
t = pd.read_csv(DASHBOARD / 'dashboard.csv', low_memory=False)
c = t[(t['MODELTXT'] == 'CR V') & (t['tipo'] == 'componente')]
s = c.groupby('componente')['quejas_comp'].sum().sort_values(ascending=False)
print((s / s.sum() * 100).round(1).head(10))

g = pd.read_csv(DASHBOARD / 'grupos.csv')
g = g[g['semaforo'] != 'Sin datos suficientes']
for c in ['gravedad', 'crash', 'fire']:
    print(c, round((g[c] * g['quejas']).sum() / g['quejas'].sum(), 4))
