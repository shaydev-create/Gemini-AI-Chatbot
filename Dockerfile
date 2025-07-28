# 🚀 Dockerfile para Gemini AI Chatbot - Versión Optimizada
FROM python:3.11-slim

# Metadatos
LABEL maintainer="Gemini AI Chatbot Team"
LABEL version="2.0.0"
LABEL description="Chatbot AI con Google Gemini - Versión Limpia"

# Establecer directorio de trabajo
WORKDIR /app

# Variables de entorno optimizadas
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.main:app \
    FLASK_ENV=production \
    PYTHONPATH=/app

# Instalar dependencias del sistema (mínimas)
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    libmagic1 \
    libmagic-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copiar solo requirements primero (para cache de Docker)
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Crear usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash --uid 1000 app

# Copiar código de la aplicación (estructura limpia)
COPY app/ ./app/
COPY config/ ./config/
COPY .env .
COPY wsgi.py .

# Crear directorios necesarios con permisos correctos
RUN mkdir -p logs uploads instance && \
    chown -R app:app /app && \
    chmod -R 755 /app

# Cambiar a usuario no-root
USER app

# Exponer puerto
EXPOSE 5000

# Health check mejorado
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Comando optimizado para producción
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "4", \
     "--worker-class", "sync", \
     "--timeout", "120", \
     "--keep-alive", "2", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "100", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "wsgi:app"]