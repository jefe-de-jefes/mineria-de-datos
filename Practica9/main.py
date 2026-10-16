import pandas as pd
from collections import Counter
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

# df = pd.read_csv('../data/nhtsa_clean.csv', usecols=['CDESCR', 'COMP_MAIN'])

columnas = ['CDESCR', 'COMP_MAIN']
df = pd.read_csv('../data/nhtsa_clean.csv', usecols=columnas)

palabras = df['CDESCR'].str.lower().str.findall(r'[a-z]+')

stopwords = STOPWORDS

conteo = Counter()
for palabra in palabras:
    conteo.update(palabra)

excepciones = {'s', 't'}
filtrado = {k: v for k, v in conteo.items() if k not in stopwords and k not in excepciones}

wordcloud = WordCloud(
    background_color="white", min_font_size=5, width=1920, height=1080
).generate_from_frequencies(filtrado)


# print(Counter(filtrado).most_common(30))


#plot the Wordloud image
# plt.close()
# plt.figure(figsize=(16, 9), facecolor=None, dpi = 120)
# plt.imshow(wordcloud)
# plt.axis("off")
# plt.tight_layout(pad=0)
#
# # plt.show()
# plt.savefig("img/word_cloud.png")
# plt.close()


#config de bigramas
textos = df['CDESCR'].dropna()
vec = CountVectorizer(ngram_range=(2, 2), max_features=5000, stop_words='english')
matriz = vec.fit_transform(textos)

totales = np.asarray(matriz.sum(axis=0)).ravel()
nombres = vec.get_feature_names_out()
conteo_bigramas = dict(zip(nombres, totales))
wordcloud_bigramas = WordCloud(
    background_color="white", min_font_size=5, width=1920, height=1080
).generate_from_frequencies(conteo_bigramas)

#config de boxplot
df['longitud'] = df['CDESCR'].str.split().str.len()
top = df['COMP_MAIN'].value_counts().head(10).index
sub = df[df['COMP_MAIN'].isin(top)]

print(sub.groupby('COMP_MAIN')['longitud'].describe())
#bloxplot
sub.boxplot(column='longitud', by='COMP_MAIN', figsize=(16, 9), rot=45, showfliers=False)
plt.suptitle('')
plt.title('Boxplot de la longitud de las descripciones', fontsize=30)
plt.xlabel('Componente que fallo', fontsize=20)
plt.ylabel('Longitud de descripcion en el reporte', fontsize=20)
plt.tight_layout()
plt.savefig('img/boxplot.png')
plt.close()

# plot the Wordloud image bigramas
plt.close()
plt.figure(figsize=(16, 9), facecolor=None, dpi = 120)
plt.imshow(wordcloud_bigramas)
plt.axis("off")
plt.tight_layout(pad=0)

# plt.show()
plt.savefig("img/word_cloud_bigramas.png")
plt.close()

