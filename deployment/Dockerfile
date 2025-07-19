# 🐳 Dockerfile para Gemini AI Chatbot - Producción Optimizada
# Imagen base optimizada para Python
FROM python:3.11-slim-bullseye

# Metadatos
LABEL maintainer="Gemini AI Chatbot Team"
LABEL version="1.0.0"
LABEL description="Gemini AI Chatbot - Interfaz Futurista con Google Gemini AI"

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    FLASK_APP=app.py \
    PYTHONPATH=/app:/app/src \
    DEBIAN_FRONTEND=noninteractive

# Crear usuario no-root para seguridad
RUN groupadd -r geminiuser && useradd -r -g geminiuser geminiuser

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Crear directorios de trabajo
WORKDIR /app

# Copiar requirements primero para aprovechar cache de Docker
COPY requirements.txt .
COPY requirements-prod.txt* ./

# Instalar dependencias Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    if [ -f requirements-prod.txt ]; then pip install --no-cache-dir -r requirements-prod.txt; fi

# Copiar código de la aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p /app/logs /app/data/instance /app/static && \
    chown -R geminiuser:geminiuser /app

# Configurar nginx
COPY docker/nginx.conf /etc/nginx/sites-available/gemini-chatbot
RUN ln -sf /etc/nginx/sites-available/gemini-chatbot /etc/nginx/sites-enabled/default

# Configurar supervisor
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Exponer puertos
EXPOSE 80 5000

# Comando de inicio (supervisord debe ejecutarse como root)
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1