import pandas as pd
from scipy.stats import kruskal
from statsmodels.stats.multitest import multipletests
from rutas import DASHBOARD, RES_HALLAZGO

UMBRAL_EFECTO = 0.06    
comp = pd.read_csv(DASHBOARD /'componentes.csv')

no_modelados = {'COMMUNICATION', 'INTERIOR LIGHTING', 'EQUIPMENT ADAPTIVE/MOBILITY',
                'TETHER, LOWER ANCHOR (ON CAR SEAT OR VEHICLE)', 'INSERT, PADDING',
                'ROLLOVER', 'CHEST CLIP, BUCKLE, HARNESS', 'CHILD SEAT',
                'I SUSPECT THE CAR SEAT IS COUNTERFEIT', 'CARRY HANDLE, SHELL, BASE'}

ancho = comp.pivot_table(index=['MAKETXT', 'MODELTXT', 'YEARTXT'], columns='componente',
                         values='proporcion', fill_value=0)
niveles = comp[['MAKETXT', 'MODELTXT', 'YEARTXT', 'semaforo']].drop_duplicates().set_index(['MAKETXT', 'MODELTXT', 'YEARTXT'])
ancho = ancho.join(niveles)

orden = ['Verde', 'Amarillo', 'Rojo', 'Alerta de fuego']
componentes = [c for c in ancho.columns if c != 'semaforo' and c not in no_modelados]
n = len(ancho)
print('grupos:', n, '| componentes probados:', len(componentes))
print(ancho['semaforo'].value_counts())

filas = []
for c in componentes:
    listas = [ancho.loc[ancho['semaforo'] == nivel, c] for nivel in orden]
    try:
        H, p = kruskal(*listas)
    except ValueError:      # pasa si todos los valores son iguales
        H, p = 0.0, 1.0
    filas.append({'componente': c, 'H': H, 'p': p})

res = pd.DataFrame(filas)
res['epsilon2'] = res['H'] / (n - 1)
res['p_ajustado'] = multipletests(res['p'], method='holm')[1]
res['mencionar'] = (res['p_ajustado'] < 0.05) & (res['epsilon2'] >= UMBRAL_EFECTO)
res = res.sort_values('epsilon2', ascending=False)
print(res.to_string(index=False, float_format=lambda x: f'{x:.4g}'))

prop = ancho.groupby('semaforo')[componentes].mean().T[orden]
print(prop.round(3))

res.to_csv(RES_HALLAZGO /'hallazgo_componentes.csv', index=False)
prop.to_csv(RES_HALLAZGO /'proporciones_por_nivel.csv')
