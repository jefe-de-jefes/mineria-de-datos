import pandas as pd
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rutas import DASHBOARD

g = pd.read_csv(DASHBOARD / 'grupos.csv')
total = g['quejas'].sum()
sub = g[g['semaforo'] != 'Sin datos suficientes']

filas = [{'indicador': 'grupos usados', 'valor': len(sub)},
         {'indicador': 'quejas cubiertas', 'valor': sub['quejas'].sum()},
         {'indicador': '% de las quejas totales', 'valor': round(sub['quejas'].sum() / total * 100, 1)}]
for c in ['gravedad', 'crash', 'fire']:
    filas.append({'indicador': c, 'valor': round((sub[c] * sub['quejas']).sum() / sub['quejas'].sum(), 4)})

ref = pd.DataFrame(filas)
print(ref.to_string(index=False))
ref.to_csv(DASHBOARD / 'referencias.csv', index=False)
