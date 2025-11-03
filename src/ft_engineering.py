from cargar_datos import cargarDatos
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, LabelEncoder, OrdinalEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from pandas.api.types import CategoricalDtype
from sklearn.preprocessing import MinMaxScaler

def ft_engineering():
    df = cargarDatos()
    df = df.drop(columns=['id_persona','nombre','apellido','telefono_contacto','correo_electronico'])
    df.drop_duplicates(inplace=True)
    cols_with_nulls = df.columns[df.isna().any()].tolist()

    for col in cols_with_nulls:

        if col == 'preferencias_alimenticias':
            # Imputación por la moda
            mode_vals = df[col].mode(dropna=True)
            if not mode_vals.empty:
                df[col] = df[col].fillna(mode_vals.iloc[0])
        else:
            # Imputación por la mediana (numéricas)
            med = df[col].median()
            df[col] = df[col].fillna(med)
    df['consume_licor'] = df['consume_licor'].map({'Sí': 1, 'No': 0})
    df['consume_licor'] = df['consume_licor'].astype('category')


    # Definir el orden explícito
    orden_tendencia = CategoricalDtype(
        categories=["Bajo", "Medio", "Alto", "Muy Alto"],
        ordered=True
    )

    # Aplicar al DataFrame
    df["estrato_socioeconomico"] = df["estrato_socioeconomico"].astype(orden_tendencia)
    df["genero"] = df["genero"].astype("category")
    df["ciudad_residencia"] = df["ciudad_residencia"].astype("category")
    df["ocio"] = df["ocio"].astype("category")
    df["preferencias_alimenticias"] = df["preferencias_alimenticias"].astype("category")
    df["membresia_premium"] = df["membresia_premium"].astype("category")
    df["tipo_de_pago_mas_usado"] = df["tipo_de_pago_mas_usado"].astype("category")

    df = df[df['edad'] < 110]
    objetivo = 'consume_licor'
    columnas_politomicas = ['genero','ciudad_residencia','estrato_socioeconomico','preferencias_alimenticias','tipo_de_pago_mas_usado']
    columnas_binarias = ['ocio','membresia_premium']

    
    # y (objetivo) con LabelEncoder
    le_objetivo = LabelEncoder()
    y_num = le_objetivo.fit_transform(df[objetivo])

    # Transformaciones de X
    numeric_cols = df.select_dtypes(include='number').columns.tolist()

    # preprocess = ColumnTransformer(
    #     transformers=[
    #         # Usamos OrdinalEncoder para las binarias. Es el equivalente de LabelEncoder para features.
    #         ('bin_encoder', OrdinalEncoder(), columnas_binarias),
    #         ('poly_ohe', OneHotEncoder(drop='first', handle_unknown='ignore', sparse_output=False), columnas_politomicas),
    #         ('', 'passthrough', numeric_cols),
    #     ],
    #     remainder='drop' # Columnas no especificadas se eliminan
    # )

    preprocess = ColumnTransformer(
    transformers=[
        ('bin_encoder', OrdinalEncoder(dtype=int), columnas_binarias),
        ('poly_ohe', OneHotEncoder(drop='first', handle_unknown='ignore', sparse_output=False, dtype=int), columnas_politomicas),
        # Usamos un escalador para las columnas numéricas
        ('numeric', MinMaxScaler(), numeric_cols) 
    ],
    remainder='drop'
)
    pipeline = Pipeline(steps=[('preprocess', preprocess)])

    X = df.drop(columns=[objetivo])
    X_num = pipeline.fit_transform(X)
    feature_names = pipeline.named_steps['preprocess'].get_feature_names_out()
    X_num_df = pd.DataFrame(X_num, columns=feature_names, index=df.index)
    df = pd.concat([X_num_df, pd.Series(y_num, name=objetivo, index=df.index)], axis=1)
    corrected = [col[2:] if col.startswith('_') else col for col in df.columns]
    df.columns = corrected
    return df

