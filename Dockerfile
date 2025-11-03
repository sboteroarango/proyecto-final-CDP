# Dockerfile

# 1. Usar una imagen base oficial de Python
FROM python:3.9-slim

# 2. Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# 3. Copiar el archivo de requerimientos primero para aprovechar el cache de Docker
COPY requirements.txt .

# 4. Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar todo el código fuente de la aplicación (incluyendo el modelo)
# Esto copia el contenido de la carpeta 'src' al directorio de trabajo '/app'
COPY src/ .

# 6. Exponer el puerto en el que la aplicación se ejecutará
EXPOSE 8000

# 7. Comando para ejecutar la aplicación usando Uvicorn
# "model_deploy:app" se refiere al objeto 'app' dentro del archivo 'model_deploy.py'
CMD ["uvicorn", "model_deploy:app", "--host", "0.0.0.0", "--port", "8000"]