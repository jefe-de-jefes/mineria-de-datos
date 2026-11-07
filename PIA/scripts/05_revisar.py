import joblib
import pandas as pd
from rutas import INTERMEDIOS, RES_REVISION

# paquete = joblib.load('modelo_sin_balancear.joblib')
# vec, modelo = paquete['vec'], paquete['modelo']
#
# con_comp = pd.read_pickle('con_comp.pkl').sample(20000, random_state=1)
# vacias = pd.read_pickle('vacias.pkl').sample(20000, random_state=1)
#
# for nombre, tabla in [('con componente', con_comp), ('sin componente', vacias)]:
#     pred = modelo.predict(vec.transform(tabla['CDESCR']))
#     print(nombre, pred.sum(axis=1).mean())
#

t = pd.read_pickle(INTERMEDIOS /'quejas_completas.pkl')
t[t['ORIGEN'] == 'predicho'].sample(100, random_state=1)[['CDESCR', 'COMP_FINAL']].to_csv(RES_REVISION /'revision_predicho.csv')
t[t['ORIGEN'] == 'forzado'].sample(50, random_state=1)[['CDESCR', 'COMP_FINAL']].to_csv(RES_REVISION /'revision_forzado.csv')
print(
    t[t['ORIGEN'] == 'forzado']['COMP_FINAL'].apply(list).explode().value_counts()
)
