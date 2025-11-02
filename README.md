# Proyecto Final: Ciencia de Datos en Producción

Este proyecto aborda el ciclo de vida completo de un proyecto de ciencia de datos, desde la estructuración del código y los datos hasta la automatización, el entrenamiento y el despliegue de modelos en un entorno de nube, culminando con un análisis comparativo de plataformas.

## Fases del Proyecto

### Fase 1: Repositorio en GitHub

Se establece la base del proyecto con un repositorio de estructura modular. Esta fase cubre el ciclo de vida de un modelo de machine learning, incluyendo la carga de datos, análisis exploratorio, ingeniería de características, modelamiento, evaluación y la creación de una imagen Docker para el despliegue.

### Fase 2: Jenkinsfile para CI/CD

Se enfoca en la automatización del flujo de trabajo mediante la creación de un `Jenkinsfile`. Este pipeline automatiza la clonación del repositorio, la ejecución de pruebas y el envío de notificaciones, sentando las bases para la Integración Continua y el Despliegue Continuo (CI/CD).

### Fase 3: Entrenamiento y Despliegue en GCP

Utilización de Google Cloud Platform (GCP) para el entrenamiento y despliegue de modelos. Se explora el uso de servicios gestionados como Vertex AI AutoML y la creación de pipelines personalizados (Vertex Pipelines) para comparar rendimiento, estabilidad y consistencia. Se extraen y analizan métricas clave como Accuracy, F1-score, y ROC-AUC.

### Fase 4: Comparación de Nubes (GCP vs. Azure)

Se realiza una comparación reflexiva entre Google Cloud Platform y Microsoft Azure. El análisis se basa tanto en la experiencia práctica obtenida en el proyecto como en investigación externa, evaluando aspectos como la facilidad de uso, costos, herramientas de MLOps, automatización, gobernanza y capacidades para entornos empresariales.
