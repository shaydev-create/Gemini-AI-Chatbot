# Dockerfile para Gemini AI Chatbot - Optimizado
FROM python:3.11-slim as base

# Metadatos
LABEL maintainer="Gemini AI Chatbot Team"
LABEL version="2.0"
LABEL description="Gemini AI Chatbot con Python 3.11"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Crear usuario no-root para seguridad
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copiar archivos de requisitos primero (para cache de Docker)
COPY requirements-minimal.txt requirements.txt ./

# Actualizar pip e instalar dependencias
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements-minimal.txt

# Copiar código de la aplicación
COPY app/ ./app/
COPY config/ ./config/
COPY scripts/ ./scripts/
COPY .env.example .env
COPY app.py .

# Crear directorios necesarios
RUN mkdir -p logs uploads instance && \
    chown -R appuser:appuser /app

# Cambiar a usuario no-root
USER appuser

# Exponer puerto
EXPOSE 5000

# Variables de entorno de la aplicación
ENV FLASK_APP=app.py \
    FLASK_ENV=production \
    PYTHONPATH=/app

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]
