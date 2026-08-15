import pandas as pd

def load_columns(doc_path: str) -> list:
    heads = []
    file = open(doc_path, 'r')
    for linea in file.readlines():
        parts = linea.split()
        if parts and parts[0].isdigit():
            heads.append(parts[1])
        else:
            continue
    return heads

def load_data(data_path: str, doc_path: str) -> pd.DataFrame:
    heads = load_columns(doc_path)
    df = pd.read_csv(data_path, sep='\t', header=None, names=heads)
    return df

def delete_unused_columns(df) -> pd.DataFrame:
    return df.drop(columns=["STATE_OF_INCIDENT", "VEHICLE_OPERATOR", "OCCURENCES", "PURCH_DT", "NUM_CYLS", "MANUF_DT"], inplace=False)

def refill_empty_object_columns(df, comment: str, percentage: float) -> pd.DataFrame:
    is_object =df.dtypes == 'object'
    nulos = df.isnull().mean() > percentage
    columns_to_refill = is_object & nulos
    columns_to_change = columns_to_refill[columns_to_refill].index
    df[columns_to_change] = df[columns_to_change].fillna(comment)
    return df

def refill_middle_empty_columns(df, columns: list[str], comment: str) -> pd.DataFrame: 
    df[columns] = df[columns].fillna(comment)
    return df

def clean_miles(df, column='MILES')-> pd.DataFrame:
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    superior = Q3 + 1.5 * IQR
    print(f"El IQR sugiere un limite maximo de {superior}, pero se usaran 400000 como maximo millaje considerando conocimiento en el area")
    return df[(df[column] <= 400000) | (df[column].isnull())]

def delete_empty_rows(df, columns: list[str]) -> pd.DataFrame:
    return df.dropna(subset=columns, inplace=False)

def convert_dates(df, columns: list[str])-> pd.DataFrame:
    for col in columns:
        df[col] = pd.to_datetime(df[col], format='%Y%m%d', errors='coerce')
    return df

def filter_by_product_type(df, product_type: str)-> pd.DataFrame:
    return df[df['PROD_TYPE'] == product_type]

def delete_invalid_states(df, codes:list[str])-> pd.DataFrame:
    return df[~df['STATE'].isin(codes)]

def delete_invalid_dates(df)-> pd.DataFrame:
    return df[(df['FAILDATE'] <= df['LDATE']) & (df['FAILDATE'] >= '1995-01-01')]

def refill_year(df)-> pd.DataFrame:
    df['YEARTXT'] = df['YEARTXT'].replace(9999, pd.NA)
    return df

def normalizar_marca(df: pd.DataFrame, specials: dict) -> pd.DataFrame:
    df["MAKETXT"] = df["MAKETXT"].str.upper().str.replace("-", " ").str.split().str.join(" ")
    df["MAKETXT"] = df["MAKETXT"].replace(specials)
    return df

def main ():
    data_path = 'COMPLAINTS_RECEIVED_2020-2024.txt'
    doc_path = "CMPL.txt"
    middle_empty_columns = ["ORIG_OWNER_YN", "ANTI_BRAKES_YN", "CRUISE_CONT_YN", "VEHICLES_TOWED_YN", "VIN"]
    columns_with_empty_rows = ["MFR_NAME", "MAKETXT", "MODELTXT","YEARTXT","COMPDESC", "CITY","CDESCR", "PROD_TYPE"]
    date_columns = ["FAILDATE", "DATEA", "LDATE"]
    invalid_states = ['PR', 'GU', 'VI', 'AS', 'MP', 'AE', 'AA', 'AP', 'NN', 'CD', 'UN', '??', '00']
    specials = {
        "UNKNOWN MANUFACTURER": "UNKNOWN",
        "4 STAR TRAILER": "4 STAR",
        "LIVIN' LITE": "LIVIN LITE",
    }

    df = load_data(data_path, doc_path)
    print(df.shape)
    df = filter_by_product_type(df, "V")
    df = delete_invalid_states(df, invalid_states)
    df = delete_unused_columns(df)
    df = refill_empty_object_columns(df, "No aplica", 0.5)
    df = refill_middle_empty_columns(df, middle_empty_columns, "Desconocido")
    df = clean_miles(df)
    df = delete_empty_rows(df, columns_with_empty_rows)
    df = convert_dates(df, date_columns)
    df = delete_invalid_dates(df)
    df = refill_year(df)
    df = normalizar_marca(df, specials)
    print(df['MAKETXT'].nunique())
    print(sorted(df['MAKETXT'].unique()))
    print(df.shape)
main()
