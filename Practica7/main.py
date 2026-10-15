import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns

columnas = ['FAILDATE','MAKETXT', 'YEARTXT', 'MILES', 'VEH_SPEED', 'CRASH', 'FIRE', 'INJURED', 'DEATHS']
df = pd.read_csv('../data/nhtsa_clean.csv', usecols=columnas, parse_dates=['FAILDATE'])

#reportes entre 2020 y 2025
df = df[(df['FAILDATE'].dt.year >= 2020) & (df['FAILDATE'].dt.year <= 2025)]

#hacer binario crash y fire
df['CRASH'] = (df['CRASH'] == 'Y').astype(int)
df['FIRE'] = (df['FIRE'] == 'Y').astype(int)

df['GRAVEDAD']= df['INJURED'] + df['DEATHS']

#agrupar por marca y anio
df_riesgo = df.groupby(['MAKETXT', 'YEARTXT']).agg({
    'GRAVEDAD': 'mean',
    'MILES': 'mean',
    'VEH_SPEED': 'mean',
    'CRASH': ['mean', 'count'],
    'FIRE': 'mean'
})

df_riesgo.columns = ['_'.join(col).strip('_') for col in df_riesgo.columns]
df_riesgo = df_riesgo[df_riesgo['CRASH_count'] >= 50]

#eliminar crash counts
df_riesgo = df_riesgo.drop(columns='CRASH_count')

#Escalar
scaler = StandardScaler()
df_riesgo_scaled = scaler.fit_transform(df_riesgo)

#inercias = []
# #kmeans con for de k desde 2 a 10
# for k in range(2, 11):
#     kmeans = KMeans(n_clusters=k, random_state=42)
#     kmeans.fit(df_riesgo_scaled)
#     inercias.append(kmeans.inertia_)
#     labels = kmeans.labels_
#     # df_riesgo['cluster'] = labels
#
# plt.plot(range(2, 11), inercias, marker='o')
# plt.xlabel('Número de clusters (k)')
# plt.ylabel('Inercia')
# plt.title('Método del codo')
# plt.savefig('img/metodo_codo.png', dpi=300)
# plt.close()

kmeans_final = KMeans(n_clusters=5, random_state=42)
kmeans_final.fit(df_riesgo_scaled)

df_risk_scaled_df = pd.DataFrame(df_riesgo_scaled, columns=df_riesgo.columns)
df_risk_scaled_df['cluster'] = kmeans_final.labels_

df_riesgo['cluster'] = kmeans_final.labels_

#modelos en cada cluster

total = df_riesgo.index.get_level_values('MAKETXT').value_counts()
for c in [0, 3]:
    grupo = df_riesgo[df_riesgo['cluster'] == c]
    en_cluster = grupo.index.get_level_values('MAKETXT').value_counts()
    tabla_marcas = pd.DataFrame({'en_cluster': en_cluster, 'total': total.loc[en_cluster.index]})
    tabla_marcas['proporcion_%'] = (tabla_marcas['en_cluster'] / tabla_marcas['total'] * 100).round(0)
    print(c, len(grupo))
    print(tabla_marcas.head(10))

#grafica de clusters

#grafica de miles vs gravedad
scatter_plot = plt.scatter(df_riesgo['MILES_mean'], df_riesgo['GRAVEDAD_mean'], c=df_riesgo['cluster'], cmap='viridis')
plt.xlabel('Millaje')
plt.ylabel('Gravedad')
plt.title('Millaje vs Gravedad')
plt.legend(*scatter_plot.legend_elements(), title='Cluster')
plt.savefig('img/miles_gravedad.png', dpi=300)
plt.close()

#grafica de crash vs gravedad
scatter_plot = plt.scatter(df_riesgo['CRASH_mean'], df_riesgo['GRAVEDAD_mean'], c=df_riesgo['cluster'], cmap='viridis')
plt.xlabel('Crash')
plt.ylabel('Gravedad')
plt.title('Crash vs Gravedad')
plt.legend(*scatter_plot.legend_elements(), title='Cluster')
plt.savefig('img/crash_gravedad.png', dpi=300)
plt.close()

#grafica de mapa de calor de df_riesgo.groupby('cluster').mean()
sns.heatmap(df_risk_scaled_df.groupby('cluster').mean(), annot=True, fmt='.2f', cmap='Blues')
plt.title('Promedios por cluster')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('img/promedios_cluster.png', dpi=300)
plt.close()

#promedio de clusters por categoria
print(df_riesgo.groupby('cluster').mean())

