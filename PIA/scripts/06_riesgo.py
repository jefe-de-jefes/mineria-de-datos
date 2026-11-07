import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, MultiLabelBinarizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, adjusted_rand_score
from rutas import INTERMEDIOS, DASHBOARD, IMG

MIN_QUEJAS = 50
VARIABLES = ['gravedad', 'crash', 'fire']     # solo variables de riesgo
DESCRIPTIVAS = ['miles', 'veh_speed']         # se muestran, no entran al clustering
K = 4
MODO = 'final'    # 'probar': codo, silueta y tablas por K, y se detiene | 'final': clustering con K y exporta

q = pd.read_pickle(INTERMEDIOS /'quejas_completas.pkl')

# 1. Filtros y variable de gravedad
q = q[(q['FAILDATE'].dt.year >= 2020) & (q['FAILDATE'].dt.year <= 2025)]
q = q.dropna(subset=['MAKETXT', 'MODELTXT', 'YEARTXT']).copy()
q['YEARTXT'] = q['YEARTXT'].astype(int)
q['GRAVEDAD'] = q['INJURED'] + q['DEATHS']

# 2. Una fila por marca, modelo y año
claves = ['MAKETXT', 'MODELTXT', 'YEARTXT']
riesgo = q.groupby(claves).agg(
    quejas=('GRAVEDAD', 'size'),
    gravedad=('GRAVEDAD', 'mean'),
    miles=('MILES', 'mean'),
    veh_speed=('VEH_SPEED', 'mean'),
    crash=('CRASH', 'mean'),
    fire=('FIRE', 'mean'))
riesgo_total = riesgo.copy()

print('combinaciones totales:', len(riesgo))
riesgo = riesgo[riesgo['quejas'] >= MIN_QUEJAS]
print('con al menos', MIN_QUEJAS, 'quejas:', len(riesgo))
riesgo = riesgo.dropna(subset=VARIABLES)
print('para el clustering:', len(riesgo))

# 3. Escalar
X = StandardScaler().fit_transform(riesgo[VARIABLES])

# 4. Modo probar: codo, silueta y tablas para varios K
if MODO == 'probar':
    rango = range(2, 9)
    inercias, siluetas = [], []
    for k in rango:
        km = KMeans(n_clusters=k, random_state=42, n_init=10).fit(X)
        inercias.append(km.inertia_)
        siluetas.append(silhouette_score(X, km.labels_))
    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    ax[0].plot(rango, inercias, marker='o')
    ax[0].set_title('Método del codo')
    ax[0].set_xlabel('Número de clusters (k)')
    ax[0].set_ylabel('Inercia')
    ax[1].plot(rango, siluetas, marker='o')
    ax[1].set_title('Silueta')
    ax[1].set_xlabel('Número de clusters (k)')
    ax[1].set_ylabel('Silueta promedio')
    plt.tight_layout()
    plt.savefig(IMG / 'codo_silueta_riesgo.png', dpi=200)
    plt.close()
    print({k: round(s, 3) for k, s in zip(rango, siluetas)})

    r = riesgo.reset_index()
    for k in [2, 3, 4]:
        r['cluster'] = KMeans(n_clusters=k, random_state=42, n_init=10).fit(X).labels_
        print('K =', k)
        print(r['cluster'].value_counts().sort_index())
        print(r.groupby('cluster')[VARIABLES + DESCRIPTIVAS + ['quejas', 'YEARTXT']].mean().round(3))
    raise SystemExit

# 5. Modo final: clustering con K
km = KMeans(n_clusters=K, random_state=42, n_init=10).fit(X)
riesgo['cluster'] = km.labels_
print('silueta:', round(silhouette_score(X, km.labels_), 3))
otro = KMeans(n_clusters=K, random_state=7, n_init=10).fit(X).labels_
print('estabilidad (ARI, 1 = iguales):', round(adjusted_rand_score(km.labels_, otro), 3))

# Semáforo: escala de gravedad más una alerta de fuego (cluster de la tabla de K = 4)
mapa = {1: 'Verde', 0: 'Amarillo', 3: 'Rojo', 2: 'Alerta de fuego'}
riesgo['semaforo'] = riesgo['cluster'].map(mapa)
assert riesgo['semaforo'].notna().all()
print(riesgo['semaforo'].value_counts())
print(riesgo.groupby('semaforo')[VARIABLES + DESCRIPTIVAS + ['quejas']].mean().round(3))

# 6. Componentes de cada grupo (para describir los niveles, no para formarlos)
q = q.join(riesgo[['cluster', 'semaforo']], on=claves, how='inner')
mlb = MultiLabelBinarizer()
M = pd.DataFrame(mlb.fit_transform(q['COMP_FINAL']), columns=mlb.classes_, index=q.index)
llave = [q['MAKETXT'], q['MODELTXT'], q['YEARTXT']]
prop = M.groupby(llave).mean()
conteo_comp = M.groupby(llave).sum()
prop.columns.name = 'componente'
conteo_comp.columns.name = 'componente'
componentes = prop.stack().rename('proporcion').to_frame()
componentes['quejas_comp'] = conteo_comp.stack()
componentes = componentes.reset_index()
componentes = componentes[componentes['quejas_comp'] > 0]
componentes = componentes.merge(riesgo[['semaforo']].reset_index(), on=claves)

# 7. Confiabilidad del relleno por grupo
riesgo['prop_forzado'] = (q['ORIGEN'] == 'forzado').groupby(llave).mean()

# 8. Historial por mes de falla
q['mes'] = q['FAILDATE'].dt.to_period('M').dt.to_timestamp()
historial = q.groupby(claves + ['mes']).size().rename('quejas').reset_index()

# 9. Exportar para Looker Studio (incluye los modelos sin quejas suficientes)
sin = riesgo_total[riesgo_total['quejas'] < MIN_QUEJAS].copy()
sin['semaforo'] = 'Sin datos suficientes'
grupos = pd.concat([riesgo, sin]).reset_index()
grupos.to_csv(DASHBOARD /'grupos.csv', index=False)
componentes.to_csv(DASHBOARD /'componentes.csv', index=False)
historial.to_csv(DASHBOARD /'historial.csv', index=False)
