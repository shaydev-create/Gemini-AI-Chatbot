#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 CONFIGURACIÓN DE GUNICORN - GEMINI AI CHATBOT

Configuración optimizada para producción con múltiples workers,
logging avanzado y configuración de seguridad.
"""

import os
import multiprocessing

# ===== CONFIGURACIÓN BÁSICA =====
bind = "0.0.0.0:5000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True
timeout = 120
keepalive = 5

# ===== CONFIGURACIÓN DE PROCESOS =====
user = os.getenv('GUNICORN_USER', 'www-data')
group = os.getenv('GUNICORN_GROUP', 'www-data')
tmp_upload_dir = None
worker_tmp_dir = "/dev/shm"

# ===== CONFIGURACIÓN SSL =====
keyfile = os.getenv('SSL_KEYFILE', '/app/ssl/key.pem')
certfile = os.getenv('SSL_CERTFILE', '/app/ssl/cert.pem')
ssl_version = 2  # TLS 1.2+
ciphers = 'ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS'

# ===== CONFIGURACIÓN DE LOGGING =====
accesslog = os.getenv('GUNICORN_ACCESS_LOG', '/app/logs/gunicorn_access.log')
errorlog = os.getenv('GUNICORN_ERROR_LOG', '/app/logs/gunicorn_error.log')
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# ===== CONFIGURACIÓN DE SEGURIDAD =====
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# ===== CONFIGURACIÓN DE PERFORMANCE =====
# Configuración de memoria
max_requests = 1000
max_requests_jitter = 50

# Configuración de timeouts
timeout = 120
graceful_timeout = 30
keepalive = 5

# ===== HOOKS DE GUNICORN =====


def when_ready(server):
    """Hook ejecutado cuando el servidor está listo."""
    server.log.info("🚀 Gemini AI Chatbot - Servidor Gunicorn iniciado")
    server.log.info(f"📊 Workers: {workers}")
    server.log.info(
        f"🔒 SSL: {
            'Habilitado' if keyfile and certfile else 'Deshabilitado'}")


def worker_int(worker):
    """Hook ejecutado cuando un worker recibe SIGINT."""
    worker.log.info(f"⚠️ Worker {worker.pid} recibió SIGINT")


def pre_fork(server, worker):
    """Hook ejecutado antes de hacer fork de un worker."""
    server.log.info(f"🔄 Iniciando worker {worker.age}")


def post_fork(server, worker):
    """Hook ejecutado después de hacer fork de un worker."""
    server.log.info(f"✅ Worker {worker.pid} iniciado correctamente")


def worker_abort(worker):
    """Hook ejecutado cuando un worker es abortado."""
    worker.log.error(f"❌ Worker {worker.pid} abortado")


def pre_exec(server):
    """Hook ejecutado antes de exec."""
    server.log.info("🔄 Reiniciando servidor Gunicorn")


def on_exit(server):
    """Hook ejecutado al salir del servidor."""
    server.log.info("🛑 Gemini AI Chatbot - Servidor Gunicorn detenido")


def on_reload(server):
    """Hook ejecutado al recargar configuración."""
    server.log.info("🔄 Recargando configuración de Gunicorn")

# ===== CONFIGURACIÓN ESPECÍFICA POR ENTORNO =====


# Desarrollo
if os.getenv('FLASK_ENV') == 'development':
    workers = 1
    reload = True
    loglevel = 'debug'
    timeout = 0  # Sin timeout en desarrollo

# Producción
elif os.getenv('FLASK_ENV') == 'production':
    workers = multiprocessing.cpu_count() * 2 + 1
    preload_app = True
    max_requests = 1000
    max_requests_jitter = 50

    # Configuración de seguridad adicional para producción
    forwarded_allow_ips = '*'
    secure_scheme_headers = {
        'X-FORWARDED-PROTOCOL': 'ssl',
        'X-FORWARDED-PROTO': 'https',
        'X-FORWARDED-SSL': 'on'
    }

# ===== CONFIGURACIÓN DE MONITOREO =====
statsd_host = os.getenv('STATSD_HOST')
statsd_prefix = 'gemini_chatbot'

# ===== CONFIGURACIÓN AVANZADA =====
# Configuración de memoria compartida
worker_tmp_dir = "/dev/shm"

# Configuración de señales
graceful_timeout = 30
timeout = 120

# Configuración de conexiones
worker_connections = 1000
keepalive = 5

print("🚀 Configuración de Gunicorn cargada correctamente")
print(f"📊 Workers configurados: {workers}")
print(f"🔗 Bind: {bind}")
print(f"⏱️ Timeout: {timeout}s")
print(f"🔒 SSL: {'Habilitado' if keyfile and certfile else 'Deshabilitado'}")
