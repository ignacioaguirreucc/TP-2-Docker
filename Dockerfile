# 🐳 Dockerfile para API de Tareas con PostgreSQL
# Versión 2.0 - Integración con base de datos

# 1. FROM: Imagen base
FROM python:3.11-slim

# 2. Metadatos
LABEL maintainer="estudiante@universidad.edu"
LABEL description="API de Tareas con PostgreSQL - TP Docker 2025"
LABEL version="2.0"

# 3. Directorio de trabajo
WORKDIR /app

# 4. Copiar dependencias primero (optimización de cache)
COPY requirements.txt .

# 5. Instalar dependencias Python (ahora incluye psycopg2)
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiar archivos de la aplicación
COPY app.py .
COPY index.html .

# 7. Puerto que expone Flask
EXPOSE 5000

# 8. Variables de entorno por defecto
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1
ENV DB_HOST=localhost
ENV DB_NAME=tareas_db
ENV DB_USER=postgres
ENV DB_PASSWORD=password123
ENV DB_PORT=5432

# 9. Comando para ejecutar la aplicación
CMD ["python", "app.py"]