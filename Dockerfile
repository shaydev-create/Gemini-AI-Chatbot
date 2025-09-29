# Dockerfile para Gemini AI Chatbot
FROM python:3.9-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de requisitos
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY app/ ./app/
COPY config/ ./config/
COPY scripts/ ./scripts/
COPY .env.example .env

# Crear directorio para logs
RUN mkdir -p logs

# Exponer puerto
EXPOSE 5000

# Variables de entorno
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Comando para ejecutar la aplicación
CMD ["python", "app/app.py"]
