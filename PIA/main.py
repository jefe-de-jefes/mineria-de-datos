import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
SALTAR = {'02_modelo'}      # set() para entrenar también

PASOS = ['01_preparar', '02_modelo', '03_comparar', '04_rellenar',
         '05_revisar', '06_riesgo', '07_hallazgo', '08_dashboard']

for paso in PASOS:
    if paso in SALTAR:
        print(f'=== saltando {paso} ===')
        continue
    print(f'=== {paso} ===', flush=True)
    r = subprocess.run([sys.executable, str(RAIZ / 'scripts' / f'{paso}.py')], cwd=RAIZ)
    if r.returncode != 0:
        sys.exit(f'Falló {paso}')
print('listo')
