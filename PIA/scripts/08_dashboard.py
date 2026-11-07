import pandas as pd
from rutas import DASHBOARD

claves = ['MAKETXT', 'MODELTXT', 'YEARTXT']
grupos = pd.read_csv(DASHBOARD /'grupos.csv')
componentes = pd.read_csv(DASHBOARD /'componentes.csv')
historial = pd.read_csv(DASHBOARD /'historial.csv')

sem = grupos[claves + ['cluster']]
componentes = componentes.merge(sem, on=claves, how='left')
historial = historial.rename(columns={'quejas': 'quejas_mes'}).merge(
    grupos[claves + ['semaforo', 'cluster']], on=claves, how='left')
chk = componentes.merge(grupos[claves + ['quejas']], on=claves)
assert ((chk['proporcion'] * chk['quejas']).round() == chk['quejas_comp']).all()
print('conteo por componente: ok')
todo = pd.concat([grupos.assign(tipo='grupo'),
                  componentes.assign(tipo='componente'),
                  historial.assign(tipo='mes')], ignore_index=True)
todo.to_csv(DASHBOARD /'dashboard.csv', index=False)
print(todo.shape)
print(todo['tipo'].value_counts())
