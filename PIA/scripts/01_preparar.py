import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
from rutas import DATOS_NHTSA, INTERMEDIOS

columnas = ['ODINO', 'MAKETXT', 'MODELTXT', 'YEARTXT', 'FAILDATE', 'COMP_MAIN', 'CDESCR',
            'CRASH', 'FIRE', 'INJURED', 'DEATHS', 'VEH_SPEED', 'MILES']
df = pd.read_csv(DATOS_NHTSA, usecols=columnas, parse_dates=['FAILDATE'])
df['COMP_MAIN'] = df['COMP_MAIN'].replace('COMMUNICATIONS', 'COMMUNICATION')

# CRASH y FIRE a 0 y 1 
df['CRASH'] = (df['CRASH'] == 'Y').astype(int)
df['FIRE'] = (df['FIRE'] == 'Y').astype(int)

# Comprobación, una sola vez: que estas columnas no cambien dentro de una queja
# print((df.groupby('ODINO')[['CRASH', 'FIRE', 'INJURED', 'DEATHS', 'VEH_SPEED', 'MILES']].nunique() > 1).sum())

# Una fila por queja, con el conjunto de sus componentes
quejas = df.groupby('ODINO').agg({
    'CDESCR': 'first', 'MAKETXT': 'first', 'MODELTXT': 'first',
    'YEARTXT': 'first', 'FAILDATE': 'first',
    'MILES': 'first', 'VEH_SPEED': 'first',
    'CRASH': 'max', 'FIRE': 'max', 'INJURED': 'max', 'DEATHS': 'max',
    'COMP_MAIN': set})
quejas['COMP_MAIN'] = quejas['COMP_MAIN'].apply(lambda s: s - {'UNKNOWN'})
vacias = quejas[quejas['COMP_MAIN'].apply(len) == 0].copy()
con_comp = quejas[quejas['COMP_MAIN'].apply(len) > 0].copy()

# Quitar componentes con 100 o menos quejas
mlb = MultiLabelBinarizer()
Y = mlb.fit_transform(con_comp['COMP_MAIN'])
conteo = pd.Series(Y.sum(axis=0), index=mlb.classes_)
chicos = set(conteo[conteo <= 100].index)
con_comp['COMP_MAIN'] = con_comp['COMP_MAIN'].apply(lambda s: s - chicos)
con_comp = con_comp[con_comp['COMP_MAIN'].apply(len) > 0]

print('quejas:', quejas.shape, '| vacias:', vacias.shape, '| con_comp:', con_comp.shape)
print('componentes quitados:', chicos)

quejas.to_pickle(INTERMEDIOS / 'quejas.pkl')
vacias.to_pickle(INTERMEDIOS / 'vacias.pkl')
con_comp.to_pickle(INTERMEDIOS / 'con_comp.pkl')
