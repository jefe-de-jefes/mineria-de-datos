import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd
from rutas import INTERMEDIOS, DASHBOARD, RES_HALLAZGO


def revisar(nombre, obtenido, esperado):
    estado = 'ok' if obtenido == esperado else 'FALLA'
    extra = '' if estado == 'ok' else f' (esperado {esperado})'
    print(f'[{estado}] {nombre}: {obtenido}{extra}')


q = pd.read_pickle(INTERMEDIOS / 'quejas.pkl')
revisar('quejas', q.shape, (289562, 12))
revisar('vacias', pd.read_pickle(INTERMEDIOS / 'vacias.pkl').shape, (21492, 12))
revisar('con_comp', pd.read_pickle(INTERMEDIOS / 'con_comp.pkl').shape, (267862, 12))

qc = pd.read_pickle(INTERMEDIOS / 'quejas_completas.pkl')
revisar('origen', qc['ORIGEN'].value_counts().to_dict(),
        {'original': 268070, 'predicho': 15239, 'forzado': 6253})

g = pd.read_csv(DASHBOARD / 'grupos.csv')
revisar('semaforo', g['semaforo'].value_counts().to_dict(),
        {'Sin datos suficientes': 9135, 'Verde': 707, 'Amarillo': 244,
         'Alerta de fuego': 119, 'Rojo': 29})

d = pd.read_csv(DASHBOARD / 'dashboard.csv', low_memory=False)
revisar('dashboard', d.shape, (76773, 18))
revisar('dashboard por tipo', d['tipo'].value_counts().to_dict(),
        {'mes': 47847, 'componente': 18692, 'grupo': 10234})

h = pd.read_csv(RES_HALLAZGO / 'hallazgo_componentes.csv')
revisar('componentes probados', len(h), 28)
revisar('componente con mayor efecto', h.iloc[0]['componente'], 'AIR BAGS')
