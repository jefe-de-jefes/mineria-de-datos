import pandas as pd

heads = []

file = open('../../CMPL.txt', 'r')

for linea in file.readlines():
    parts = linea.split()
    if parts and parts[0].isdigit():
        heads.append(parts[1])
    else:
        continue
df = pd.read_csv('COMPLAINTS_RECEIVED_2020-2024.txt', sep='\t', header=None, names=heads)
df.drop(columns=["STATE_OF_INCIDENT", "VEHICLE_OPERATOR"], inplace=True)
is_object =df.dtypes == 'object'
nulos = df.isnull().mean() >.5
columns_to_refill = is_object & nulos
columns_to_change = columns_to_refill[columns_to_refill].index
df[columns_to_change] = df[columns_to_change].fillna('No aplica')
print(df['MILES'].describe())
print((df['MILES'] > 800000).sum())
Q1 = df['MILES'].quantile(0.25)
Q3 = df['MILES'].quantile(0.75)
IQR = Q3 - Q1
superior = Q3 + 1.5 * IQR
inferior = Q1 - 1.5 * IQR
print(superior, inferior)
#df.info()

