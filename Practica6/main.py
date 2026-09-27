import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

columnas = ['MAKETXT', 'YEARTXT', 'MILES', 'VEH_SPEED', 'CRASH', 'FIRE', 'COMP_MAIN']
df_known = pd.read_csv('../data/nhtsa_clean.csv', usecols=columnas)

# df_unknown = df_known[df_known['COMP_MAIN'] == 'UNKNOWN']
# df_unknown = df_unknown.dropna()

df_known = df_known[df_known['COMP_MAIN'] != 'UNKNOWN']

df_known = df_known.dropna()

#seleccion de top 7 componentes a evaluar
top7 = df_known['COMP_MAIN'].value_counts().head(7).index.tolist()
df_knn = df_known[df_known['COMP_MAIN'].isin(top7)].copy()

#limpieza de nulos
df_knn = df_knn.dropna(subset=['YEARTXT', 'MILES', 'VEH_SPEED', 'CRASH', 'FIRE', 'MAKETXT'])

#ocnvertir variables de caracter a binarias
df_knn['CRASH'] = (df_knn['CRASH'] == 'Y').astype(int)
df_knn['FIRE'] = (df_knn['FIRE'] == 'Y').astype(int)

#seleccion de top 20 marcas
top_20 = df_knn['MAKETXT'].value_counts().head(20).index
df_knn['MAKETXT'] = df_knn['MAKETXT'].apply(lambda x: x if x in top_20 else 'OTHER')

#one hot encoding
df_encoded = pd.get_dummies(df_knn, columns=['MAKETXT'], drop_first=True)

#separacion de datos
X = df_encoded.drop(columns='COMP_MAIN')
y = df_encoded['COMP_MAIN']

#dividir en entrenamiento y test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Escalar datos con standard scaler 
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

#entrenar el modelo con k
k=31
knn = KNeighborsClassifier(n_neighbors=k)
knn.fit(X_train_scaled, y_train)

#evaluacion del modelo
y_pred = knn.predict(X_test_scaled)
print(classification_report(y_test, y_pred, zero_division=0))

#matriz de confusion
matriz = confusion_matrix(y_test, y_pred, labels=knn.classes_)
sns.heatmap(matriz, annot=True, fmt='d', xticklabels=knn.classes_, yticklabels=knn.classes_, cmap='Blues')
plt.xlabel('Predicción')
plt.ylabel('Real')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('img/matriz_confusion.png', dpi=300)
plt.close()
