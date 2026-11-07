from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent       # carpeta PIA
DATOS_NHTSA = RAIZ.parent / 'data' / 'nhtsa_clean.csv'
INTERMEDIOS = RAIZ / 'intermedios'
RES_MODELO = RAIZ / 'resultados' / 'modelo'
RES_REVISION = RAIZ / 'resultados' / 'revision'
RES_HALLAZGO = RAIZ / 'resultados' / 'hallazgo'
DASHBOARD = RAIZ / 'dashboard'
IMG = RAIZ / 'img'

for carpeta in (INTERMEDIOS, RES_MODELO, RES_REVISION, RES_HALLAZGO, DASHBOARD, IMG):
    carpeta.mkdir(parents=True, exist_ok=True)
