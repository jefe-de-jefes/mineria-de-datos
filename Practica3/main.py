import pandas as pd
from tabulate import tabulate
import matplotlib.pyplot as plt

df = pd.read_csv('../data/nhtsa_clean.csv', parse_dates=['FAILDATE', 'DATEA', 'LDATE'])

df['MILES'].plot(kind='hist', bins=30)
plt.title('Histograma de quejas por MILES')
plt.xlabel('MILES')
plt.ylabel('Quejas')
plt.savefig('img/hist_miles.png')
plt.close()

top_modelos = df['MODELTXT'].value_counts().head(10)
top_modelos.plot(kind='bar')
plt.title('Top 10 modelos con mas quejas')
plt.xlabel('Modelo')
plt.ylabel('Numero de quejas')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig("img/top_modelos.png", bbox_inches="tight")
plt.close()


df_filtrado_speed = df[df['VEH_SPEED'] <= 140]
df_filtrado_speed.boxplot(column='VEH_SPEED', by='CRASH')
plt.suptitle('')
plt.title('Velocidad segun si hubo choque)')
plt.xlabel('Hubo choque?')
plt.ylabel('Velocidad')
plt.savefig('img/boxplot_crash.png', bbox_inches='tight')
plt.close()

reportes_anio = df['FAILDATE'].dt.year.value_counts().sort_index()
reportes_anio.plot(kind='line')
plt.title('Reportes por anio')
plt.xlabel('Anio')
plt.ylabel('Reportes')
plt.savefig('img/reportes_anio.png', bbox_inches='tight')
plt.close()

df_civic = df[df['MODELTXT'] == 'CIVIC']
componentes_civic = df_civic['COMP_MAIN'].value_counts()
top10_componentes = componentes_civic.head(10)
otros = componentes_civic.iloc[10:].sum()
pastel_civic = pd.concat([top10_componentes, pd.Series({'Otros': otros})])
plt.figure(figsize=(9, 6))
wedges, texts, autotexts = plt.pie(
    pastel_civic,
    labels=None,
    autopct='%1.1f%%',
    startangle=140,
    pctdistance=0.8,)
plt.legend(
    wedges,
    pastel_civic.index,
    title='Componentes',
    loc='center left',
    bbox_to_anchor=(1, 0, 0.5, 1),
    fontsize=9,)
plt.title('Componentes mas comunes en quejas en Civic')
plt.tight_layout()
plt.savefig('img/pastel_civic.png', bbox_inches='tight')
plt.close()

volumen = df['COMP_MAIN'].value_counts()
comp_representativos = volumen[volumen >= 5000].index
df_comp = df[df['COMP_MAIN'].isin(comp_representativos)]
tasa_choque = (
    df_comp[df_comp['CRASH'] == 'Y']['COMP_MAIN'].value_counts()
    / df_comp['COMP_MAIN'].value_counts()
    * 100).dropna()
top_riesgo = tasa_choque.sort_values(ascending=False).head(8)
plt.figure(figsize=(9, 4.5))
top_riesgo.plot(kind='bar', color='firebrick')
plt.title('Componentes con mayor porcentaje de quejas con choque')
plt.xlabel('Componente')
plt.ylabel('% de quejas con choque')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('img/tasa_choque_componente.png', bbox_inches='tight')
plt.close()
