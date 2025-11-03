# src/model_deploy.py

import pandas as pd
import xgboost as xgb
from fastapi import FastAPI,Response, HTTPException
from pydantic import BaseModel
from typing import List
import uvicorn
from model_evaluation import evaluation
from model_monitoring import detectar_data_drift_numerico
from ft_engineering import ft_engineering
import os
# --- 1. Definición de los modelos de datos con Pydantic ---

# Define la estructura de una única entrada para la predicción.
# Los nombres de los campos DEBEN coincidir exactamente con las columnas de tus datos de entrenamiento.
class PredictionInput(BaseModel):
    bin_encoder_ocio: float
    bin_encoder_membresia_premium: float
    poly_ohe_genero_Masculino: float
    poly_ohe_ciudad_residencia_Chicago: float
    poly_ohe_ciudad_residencia_Dallas: float
    poly_ohe_ciudad_residencia_Denver: float
    poly_ohe_ciudad_residencia_Houston: float
    poly_ohe_ciudad_residencia_Miami: float
    poly_ohe_ciudad_residencia_NYC: float
    poly_ohe_ciudad_residencia_Phoenix: float
    poly_ohe_ciudad_residencia_San_Diego: float
    poly_ohe_ciudad_residencia_Seattle: float
    poly_ohe_estrato_socioeconomico_Bajo: float
    poly_ohe_estrato_socioeconomico_Medio: float
    poly_ohe_estrato_socioeconomico_Muy_Alto: float
    poly_ohe_preferencias_alimenticias_Mariscos: float
    poly_ohe_preferencias_alimenticias_Otro: float
    poly_ohe_preferencias_alimenticias_Pescado: float
    poly_ohe_preferencias_alimenticias_Vegano: float
    poly_ohe_preferencias_alimenticias_Vegetariano: float
    poly_ohe_tipo_de_pago_mas_usado_Criptomoneda: float
    poly_ohe_tipo_de_pago_mas_usado_Efectivo: float
    poly_ohe_tipo_de_pago_mas_usado_Tarjeta: float
    numeric_edad: float
    numeric_frecuencia_visita: float
    numeric_promedio_gasto_comida: float
    numeric_ingresos_mensuales: float

# Define la estructura para una solicitud por batch (lote).
class BatchPredictionInput(BaseModel):
    data: List[PredictionInput]


# --- 2. Inicialización de la aplicación y carga del modelo ---

# Inicializar la aplicación FastAPI
app = FastAPI(
    title="API de Predicción de Consumo de Licor",
    description="Despliega un modelo XGBoost para predicciones por batch.",
    version="1.0.0"
)

# --- CONSTRUIR RUTA ABSOLUTA ---
# Obtiene la ruta del directorio donde se encuentra este script (es decir, /src)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Une la ruta del directorio con el nombre del archivo del modelo
model_path = os.path.join(script_dir, "xgb_model.json")
try:
    model = xgb.Booster()
    model.load_model(model_path)
    # Es una buena práctica guardar los nombres de las features para asegurar el orden
    model_features = model.feature_names
except Exception as e:
    print(f"Error cargando el modelo: {e}")
    model = None

# --- 3. Definición del endpoint de predicción ---

@app.post('/predict')
async def predict_batch(input_data: BatchPredictionInput):
    """
    Endpoint para predicciones por batch.
    Recibe una lista de registros y devuelve una lista de predicciones.
    """
    if model is None:
        return {"error": "El modelo no pudo ser cargado. Revisa los logs del servidor."}

    try:
        # Convierte la lista de objetos Pydantic a una lista de diccionarios
        input_list = [item.dict() for item in input_data.data]

        # Crea un DataFrame de pandas
        df = pd.DataFrame(input_list)

        # Reordena las columnas del DataFrame para que coincidan con el orden del modelo
        # Esto es CRUCIAL para evitar errores si los datos llegan en otro orden.
        df = df[model_features]

        # Crea la DMatrix para XGBoost
        dmatrix = xgb.DMatrix(df)

        # Realiza las predicciones
        predictions_proba = model.predict(dmatrix)

        threshold = 0.5
        final_predictions = [1 if prob >= threshold else 0 for prob in predictions_proba]

        # Devuelve las predicciones en formato JSON
        return {'predictions': final_predictions}

    except Exception as e:
        return {'error': f"Ocurrió un error durante la predicción: {str(e)}"}

@app.get("/")
def read_root():
    return {"status": "OK", "message": "API de predicción está en línea. Usa el endpoint /predict."}

@app.get("/evaluation",
         responses={200: {"content": {"image/png": {}}}},
         description="Retorna una imagen PNG con la visualización de las métricas de evaluación del modelo."
)
async def serve_evaluation_plot():
    """
    Endpoint para visualizar la evaluación del modelo.
    Llama a la función importada para generar el gráfico y lo devuelve.
    """
    image_buffer = evaluation() # <-- ¡Aquí usamos la función importada!
    if image_buffer:
        return Response(content=image_buffer.getvalue(), media_type="image/png")
    else:
        return {"error": "No se pudo generar el gráfico de evaluación."}
    
@app.post("/monitor", tags=["Monitoreo"])
async def monitor_data_drift(datos_produccion: BatchPredictionInput):
    """
    Recibe un lote de datos de producción y lo compara con el dataset de 
    referencia (generado por ft_engineering) para detectar Data Drift.
    """
    # 1. Generar el DataFrame de referencia
    try:
        df_referencia = ft_engineering()
        # Asegurarse de que las columnas están limpias
        df_referencia.columns = [x.replace('__','_') for x in df_referencia.columns]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el DataFrame de referencia: {e}")

    # 2. Convertir el payload de producción a un DataFrame
    if not datos_produccion.data:
        raise HTTPException(status_code=400, detail="El payload no contiene datos de producción.")
    
    lista_de_datos_prod = [item.dict() for item in datos_produccion.data]
    df_produccion = pd.DataFrame(lista_de_datos_prod)

    # 3. Ejecutar la función de detección de drift
    #    (Asegúrate de que las columnas de df_produccion coincidan con las de df_referencia)
    columnas_comunes = [col for col in df_referencia.columns if col in df_produccion.columns]
    reporte = detectar_data_drift_numerico(df_referencia[columnas_comunes], df_produccion[columnas_comunes])
    
    if reporte.empty:
        return {"status": "Análisis no realizado. No se encontraron columnas numéricas comunes para analizar."}

    # 4. Formatear y devolver la respuesta
    reporte_json = reporte.reset_index().rename(columns={'index': 'variable'}).to_dict('records')
    hay_drift = any(item['drift_detectado'] for item in reporte_json)

    return {
        "status": "Drift detectado" if hay_drift else "No se detectó drift significativo",
        "hay_drift": hay_drift,
        "reporte_drift": reporte_json
    }

# Esto permite ejecutar el script directamente para pruebas locales
if __name__ == '__main__':
    uvicorn.run("model_deploy:app", host="0.0.0.0", port=8000, reload=True)