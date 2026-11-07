import joblib
import pandas as pd
import numpy as np
from rutas import INTERMEDIOS

MODELO = 'sin_balancear'   # 'balanceado' o 'sin_balancear', según tu comparación de reportes
FORZAR = True          # True: si no predice nada, se asigna el componente con mayor puntaje

quejas = pd.read_pickle(INTERMEDIOS /'quejas.pkl')
vacias = pd.read_pickle(INTERMEDIOS /'vacias.pkl')

paquete = joblib.load(INTERMEDIOS /f'modelo_{MODELO}.joblib')
vec, mlb, modelo = paquete['vec'], paquete['mlb'], paquete['modelo']

# Predecir las quejas sin componente
A = vec.transform(vacias['CDESCR'])
pred = modelo.predict(A)
conjuntos = [set(t) for t in mlb.inverse_transform(pred)]

vacio_antes = [len(c) == 0 for c in conjuntos]

if FORZAR:
    puntajes = modelo.decision_function(A)
    mejor = mlb.classes_[puntajes.argmax(axis=1)]
    conjuntos = [c if len(c) > 0 else {m} for c, m in zip(conjuntos, mejor)]

print('modelo usado:', MODELO, '| FORZAR:', FORZAR)
print('promedio de componentes por queja predicha:', sum(len(c) for c in conjuntos) / len(conjuntos))

pred_series = pd.Series(conjuntos, index=vacias.index, dtype=object)

# Tabla final: originales + predichos, sin tocar COMP_MAIN
tiene_original = quejas['COMP_MAIN'].apply(len) > 0
quejas['COMP_FINAL'] = quejas['COMP_MAIN'].where(tiene_original, pred_series)
quejas['ORIGEN'] = 'original'
quejas.loc[vacias.index, 'ORIGEN'] = np.where(vacio_antes, 'forzado', 'predicho')
print('quejas sin componente:', len(vacias))
print('con prediccion no vacia:', sum(len(c) > 0 for c in conjuntos))
print(quejas['ORIGEN'].value_counts())

quejas.to_pickle(INTERMEDIOS /'quejas_completas.pkl')
