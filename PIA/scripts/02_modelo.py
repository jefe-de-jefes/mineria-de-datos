import time
import joblib
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report
from rutas import INTERMEDIOS, RES_MODELO

con_comp = pd.read_pickle(INTERMEDIOS /'con_comp.pkl')

mlb = MultiLabelBinarizer()
Y = mlb.fit_transform(con_comp['COMP_MAIN'])
X_tr, X_te, Y_tr, Y_te = train_test_split(con_comp['CDESCR'], Y, test_size=0.2, random_state=42)

vec = TfidfVectorizer(stop_words='english', min_df=5, max_features=50000)
A_tr = vec.fit_transform(X_tr)
A_te = vec.transform(X_te)

configuraciones = {'sin_balancear': None, 'balanceado': 'balanced'}

for nombre, peso in configuraciones.items():
    t0 = time.perf_counter()
    modelo = OneVsRestClassifier(LinearSVC(class_weight=peso), n_jobs=-1)
    modelo.fit(A_tr, Y_tr)
    print(nombre, 'fit:', round(time.perf_counter() - t0), 'segundos')

    pred = modelo.predict(A_te)
    reporte = classification_report(Y_te, pred, target_names=mlb.classes_,
                                    zero_division=0, output_dict=True)
    pd.DataFrame(reporte).T.to_csv(RES_MODELO /f'reporte_{nombre}.csv')
    joblib.dump({'vec': vec, 'mlb': mlb, 'modelo': modelo}, INTERMEDIOS /f'modelo_{nombre}.joblib')
