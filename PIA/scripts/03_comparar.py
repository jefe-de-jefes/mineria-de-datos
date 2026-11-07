import pandas as pd
from rutas import INTERMEDIOS, RES_MODELO

pd.set_option('display.max_rows', None)
pd.set_option('display.width', 200)

a = pd.read_csv(RES_MODELO /'reporte_sin_balancear.csv', index_col=0)
b = pd.read_csv(RES_MODELO /'reporte_balanceado.csv', index_col=0)
comp = pd.DataFrame({'recall_sin': a['recall'], 'recall_bal': b['recall'],
                     'prec_sin': a['precision'], 'prec_bal': b['precision'],
                     'f1_sin': a['f1-score'], 'f1_bal': b['f1-score'], 'support': a['support']})
print(comp.round(2))

pd.set_option('display.max_colwidth', 200)

t = pd.read_pickle(INTERMEDIOS /'quejas_completas.pkl')
print(t.groupby('ORIGEN')['COMP_FINAL'].apply(lambda s: s.apply(len).mean()))
