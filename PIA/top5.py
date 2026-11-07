import pandas as pd
from scripts.rutas import RES_HALLAZGO
t = pd.read_csv(RES_HALLAZGO / 'hallazgo_componentes.csv')
print(t.sort_values('epsilon2', ascending=False).head(5).to_string())
