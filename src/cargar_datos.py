
from google.cloud import bigquery

def cargarDatos():
 
    # Set your GCP project ID
    project_id = "primer-proyecto-cdp"
    
    # Create client
    client = bigquery.Client(project=project_id)
    
    # SQL Query
    query = "SELECT * FROM `primer-proyecto-cdp.proyecto_final.base_datos_restaurante`"
    df = client.query(query).to_dataframe()
    
    return df