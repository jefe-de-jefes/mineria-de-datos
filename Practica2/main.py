import pandas as pd
from tabulate import tabulate

df = pd.read_csv('../data/nhtsa_clean.csv', parse_dates=['FAILDATE', 'DATEA', 'LDATE'])

def print_tabulate(df):
    print(tabulate(df, headers=df.columns, tablefmt='grid'))

columnas = ['MILES', 'VEH_SPEED', 'INJURED', 'DEATHS']

resumen = df[columnas].describe().T
resumen['moda'] = [df[col].mode()[0] for col in columnas]
resumen['asimetria'] = [df[col].skew() for col in columnas]
resumen['kurtosis'] = [df[col].kurt() for col in columnas]
print_tabulate(resumen)

conteo_por_modelo = df['MODELTXT'].value_counts()
modelos_con_volumen = conteo_por_modelo[conteo_por_modelo >= 100].index
df_filtrado = df[df['MODELTXT'].isin(modelos_con_volumen)]
con_muertes_modelo = df_filtrado[df_filtrado['DEATHS'] > 0]

con_heridos = df[df['INJURED'] > 0]
con_muertes = df[df['DEATHS'] > 0]

ceros = df[df['MILES'] == 0]

resumen_muertes = con_muertes_modelo.groupby('MODELTXT').agg(
    conteo_muertes=('DEATHS', 'count'),
    velocidad_promedio=('VEH_SPEED', 'mean')
)
resumen_muertes['pct_quejas_con_muerte'] = (
    resumen_muertes['conteo_muertes'] / df_filtrado.groupby('MODELTXT').size() * 100
)
resumen_muertes = resumen_muertes.sort_values('pct_quejas_con_muerte', ascending=False).head(10)
print("\nTop 10 modelos por % de quejas con muerte:")
print_tabulate(resumen_muertes.round(2))

resumen_marcas = con_muertes.groupby('MAKETXT').size().to_frame('conteo_muertes')
resumen_marcas['pct_del_total_muertes'] = (resumen_marcas['conteo_muertes'] / len(con_muertes) * 100).round(2)
resumen_marcas = resumen_marcas.sort_values('conteo_muertes', ascending=False).head(10)
print("\nTop 10 marcas por conteo de quejas con muerte:")
print_tabulate(resumen_marcas)

top_componentes = ceros['COMP_MAIN'].value_counts().head(5).index

conteo_comp_modelo = ceros.groupby(['COMP_MAIN', 'MODELTXT']).size()
top5_por_componente = conteo_comp_modelo.groupby(level='COMP_MAIN', group_keys=False).nlargest(5)
top5_por_componente = top5_por_componente[
    top5_por_componente.index.get_level_values('COMP_MAIN').isin(top_componentes)
]
tabla3 = top5_por_componente.reset_index(name='conteo')
print("\nTop 5 modelos por componente (en quejas con MILES == 0):")
print_tabulate(tabla3.fillna('-'))

