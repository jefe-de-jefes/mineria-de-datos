import pandas as pd
from tabulate import tabulate
import matplotlib.pyplot as plt
import statsmodels.api as sm

df = pd.read_csv('../data/nhtsa_clean.csv', parse_dates=['FAILDATE', 'DATEA', 'LDATE'])

diferencia = (df['LDATE'] - df['FAILDATE']).dt.days

def ajustar_regresion(df, x_col, y_col):
    x = sm.add_constant(df[x_col])
    modelo = sm.OLS(df[y_col], x).fit()
    return modelo

#modelo de regresion de gravedad vs diferencia
gravedad = df['INJURED'] + df['DEATHS']
df_reporte1 = pd.DataFrame({'dias_reporte': diferencia, 'gravedad': gravedad})
df_reporte1 = df_reporte1[df_reporte1['gravedad'] > 0]
modelo1 = ajustar_regresion(df_reporte1, 'gravedad', 'dias_reporte')
print(modelo1.summary())

#modelo de regresion de millaje vs tiempo en que se reporta la falla
millaje = df['MILES']
df_reporte2 = pd.DataFrame({'dias_reporte': diferencia, 'millaje': millaje})
df_reporte2 = df_reporte2[df_reporte2['millaje'].notna()]
modelo2 = ajustar_regresion(df_reporte2, 'millaje', 'dias_reporte')
print(modelo2.summary())

#modelo de regresion de numero de reportes vs mes/anio que se reportan

meses = df['FAILDATE'].dt.to_period('M')
conteo = meses.value_counts().sort_index()
conteo = conteo[conteo.index >= '2018-01']
x_secuencia = list(range(len(conteo)))
df_reporte3 = pd.DataFrame({'x': x_secuencia, 'y': conteo.values})
modelo3 = ajustar_regresion(df_reporte3, 'x', 'y')
print(modelo3.summary())

# Graficas

# dias vs gravedad
df_reporte1.plot(x='gravedad', y='dias_reporte', kind='scatter', figsize=(8, 5))
intercepto, pendiente = modelo1.params
x_vals = df_reporte1['gravedad']
y_pred = intercepto + pendiente * x_vals
plt.plot(x_vals, y_pred, color='red')
plt.title('Días para reportar según gravedad del incidente')
plt.xlabel('Nivel de Gravedad')
plt.ylabel('Dias transcurridos para reportar')
plt.tight_layout() # <-- Evita que los títulos/ejes se corten o empalmen
plt.savefig('img/regresion_gravedad.png', dpi=300)
plt.close()

# dias vs millaje
df_reporte2.plot(x='millaje', y='dias_reporte', kind='scatter', figsize=(12, 8))
intercepto, pendiente = modelo2.params
x_vals = df_reporte2['millaje']
y_pred = intercepto + pendiente * x_vals
plt.plot(x_vals, y_pred, color='red')
plt.title('Días para reportar según millaje')
plt.xlabel('Millaje del vehículo')
plt.ylabel('Días transcurridos para reportar')
plt.tight_layout() 
plt.savefig('img/regresion_millaje.png', dpi=300)
plt.close()

# no de reportes vs mes/anio que se reportan
df_reporte3.plot(x='x', y='y', kind='scatter', alpha=0.6, figsize=(10, 6), label='Datos reales')
intercepto, pendiente = modelo3.params
x_vals = df_reporte3['x']
y_pred = intercepto + pendiente * x_vals
prediccion = modelo3.get_prediction(sm.add_constant(df_reporte3['x']))
intervalo = prediccion.conf_int()
plt.plot(x_vals, y_pred, color='red', label = 'Regresion lineal')
plt.title('No de reportes por mes')
plt.xticks(ticks=df_reporte3['x'][::6], labels=conteo.index[::6], rotation=90)
plt.fill_between(x_vals, intervalo[:, 0], intervalo[:, 1], color='red', alpha=0.2, label='Confianza 95%')
plt.xlabel('Anio-mes')
plt.ylabel('Numero de Reportes')
plt.legend()
plt.tight_layout()
plt.savefig('img/regresion_reportes.png', dpi=300)
plt.close()


