import pandas as pd
import numpy as np
from tabulate import tabulate
from scipy import stats

df = pd.read_csv('../data/nhtsa_clean.csv', parse_dates=['FAILDATE', 'DATEA', 'LDATE'])

def print_tabulate(df):
    print(tabulate(df, headers=df.columns, tablefmt='grid'))

def cohen_d(a, b):
    n1, n2 = len(a), len(b)
    s_pooled = (((n1 - 1) * a.std()**2 + (n2 - 1) * b.std()**2) / (n1 + n2 - 2)) ** 0.5
    return (a.mean() - b.mean()) / s_pooled

def eta_cuadrado(grupos):
    todos = np.concatenate(grupos)
    gran_media = todos.mean()
    ss_total = ((todos - gran_media) ** 2).sum()
    ss_entre = sum(len(g) * (g.mean() - gran_media) ** 2 for g in grupos)
    return ss_entre / ss_total

def eta_cuadrado_H(H, n):
    return H / (n - 1)
# =========================================================
# COMPARACIÓN 1 — VEH_SPEED según CRASH (2 grupos)
# =========================================================

df_speed = df[df['VEH_SPEED'].notna()]
conteo_crash = df_speed.groupby('CRASH')['VEH_SPEED'].count()
print("Datos servibles VEH_SPEED por grupo CRASH:")
print_tabulate(conteo_crash.to_frame('n'))

grupo_si = df_speed[df_speed['CRASH'] == 'Y']['VEH_SPEED']
grupo_no = df_speed[df_speed['CRASH'] == 'N']['VEH_SPEED']

levene_speed = stats.levene(grupo_si, grupo_no)
print(f"\nLevene VEH_SPEED~CRASH: stat={levene_speed.statistic:.3f}, p={levene_speed.pvalue:.4f}")

t_result = stats.ttest_ind(grupo_si, grupo_no, equal_var=False)
u_result = stats.mannwhitneyu(grupo_si, grupo_no, alternative='two-sided')
d = cohen_d(grupo_si, grupo_no)

print(f"\nMedia VEH_SPEED (CRASH=N): {grupo_no.mean():.2f}")
print(f"Media VEH_SPEED (CRASH=Y): {grupo_si.mean():.2f}")
print(f"t-test (Welch): stat={t_result.statistic:.3f}, p={t_result.pvalue:.6f}")
print(f"Mann-Whitney: stat={u_result.statistic:.3f}, p={u_result.pvalue:.6f}")
print(f"Cohen's d: {d:.3f}")

# =========================================================
# COMPARACIÓN 2 — MILES según COMP_MAIN (n grupos)
# =========================================================

df_miles = df[df['MILES'].notna()]
top_comp = df_miles['COMP_MAIN'].value_counts()
comp_validos = top_comp[top_comp >= 5000].index
df_miles_filtrado = df_miles[df_miles['COMP_MAIN'].isin(comp_validos)]

conteo_comp = df_miles_filtrado.groupby('COMP_MAIN')['MILES'].count()
print("\nDatos servibles MILES por componente:")
print_tabulate(conteo_comp.sort_values(ascending=False).to_frame('n'))

grupos_comp = [g['MILES'].values for _, g in df_miles_filtrado.groupby('COMP_MAIN')]
nombres_comp = [nombre for nombre, _ in df_miles_filtrado.groupby('COMP_MAIN')]

levene_miles = stats.levene(*grupos_comp)
print(f"\nLevene MILES~COMP_MAIN: stat={levene_miles.statistic:.3f}, p={levene_miles.pvalue:.4f}")
# p < 0.05 -> varianzas NO homogéneas

medianas_comp = df_miles_filtrado.groupby('COMP_MAIN')['MILES'].median().sort_values()
print("\nMediana de MILES por componente:")
print_tabulate(medianas_comp.to_frame('mediana_miles'))

anova_result = stats.f_oneway(*grupos_comp)
kruskal_result = stats.kruskal(*grupos_comp)
eta2 = eta_cuadrado(grupos_comp)
n_total = sum(len(g) for g in grupos_comp)
eta2_H = eta_cuadrado_H(kruskal_result.statistic, n_total)

print(f"\nANOVA: stat={anova_result.statistic:.3f}, p={anova_result.pvalue:.6f}")
print(f"Kruskal-Wallis: stat={kruskal_result.statistic:.3f}, p={kruskal_result.pvalue:.6f}")
print(f"Eta-cuadrado (clásico, ANOVA): {eta2:.4f}")
print(f"Eta-cuadrado (basado en H, compatible con Kruskal-Wallis): {eta2_H:.4f}")
