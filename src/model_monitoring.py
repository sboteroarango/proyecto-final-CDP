# model_monitoring.py (Versión solo numérica)

import pandas as pd
from scipy.stats import ks_2samp
import numpy as np

def detectar_data_drift_numerico(df_referencia: pd.DataFrame, df_produccion: pd.DataFrame, umbral_p_value: float = 0.05) -> pd.DataFrame:
    """
    Compara dos DataFrames (uno de referencia y otro de producción) para detectar
    Data Drift en cada columna numérica utilizando el test de Kolmogorov-Smirnov (KS).

    Ignora las columnas que no sean numéricas.

    Args:
        df_referencia (pd.DataFrame): DataFrame con los datos de entrenamiento o una
                                     muestra de referencia estable.
        df_produccion (pd.DataFrame): DataFrame con los datos recientes de producción
                                     (log de predicciones).
        umbral_p_value (float, optional): El umbral de significancia para determinar
                                          si hay drift. Defaults to 0.05.

    Returns:
        pd.DataFrame: Un DataFrame que sirve como reporte, indicando para cada columna
                      numérica si se detectó drift, el p-value obtenido y el test utilizado.
    """
    reporte_drift = {}

    # Seleccionar solo columnas numéricas que existan en ambos DataFrames
    columnas_numericas_ref = df_referencia.select_dtypes(include=np.number).columns
    columnas_numericas_prod = df_produccion.select_dtypes(include=np.number).columns
    columnas_comunes = [col for col in columnas_numericas_ref if col in columnas_numericas_prod]
    
    for columna in columnas_comunes:
        serie_referencia = df_referencia[columna].dropna()
        serie_produccion = df_produccion[columna].dropna()

        # Si alguna de las series está vacía, no se puede hacer el test
        if serie_referencia.empty or serie_produccion.empty:
            continue

        # Test de Kolmogorov-Smirnov
        stat, p_value = ks_2samp(serie_referencia, serie_produccion)
        drift_detectado = p_value < umbral_p_value
        
        reporte_drift[columna] = {
            'drift_detectado': drift_detectado,
            'p_value': p_value,
            'test': 'Kolmogorov-Smirnov'
        }
            
    # Si no se encontraron columnas numéricas comunes, devolver un DataFrame vacío
    if not reporte_drift:
        return pd.DataFrame()
        
    return pd.DataFrame(reporte_drift).T.sort_values(by='p_value', ascending=True)
