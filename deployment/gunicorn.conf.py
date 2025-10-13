#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 GUNICORN CONFIGURATION - GEMINI AI CHATBOT
Optimized configuration for production environments using gevent workers,
structured JSON logging, and modern security settings.
"""

import json
import logging
import multiprocessing
import os
import ssl
import traceback

# --- Environment Loading ---
# Load environment variables from .env file if it exists, for local testing.
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# --- Core Process Configuration ---
# Bind to all network interfaces on the specified port.
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"

# Use sync workers for stable performance.
# For high-concurrency, use "gthread" with multiple threads.
worker_class = "gthread"

# Dynamically calculate the number of workers.
# The formula is a common recommendation: (2 * number_of_cores) + 1
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))

# Number of threads per worker. For gthread, use 2-4 threads.
threads = int(os.getenv("GUNICORN_THREADS", 4))

# Recycle workers after a number of requests to prevent memory leaks.
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", 2000))
max_requests_jitter = int(os.getenv("GUNICORN_MAX_REQUESTS_JITTER", 500))

# Preload the application code before forking workers.
# This saves memory and speeds up worker startup.
preload_app = os.getenv("GUNICORN_PRELOAD", "true").lower() == "true"

# --- Timeout Configuration ---
# Worker timeout for handling requests.
timeout = int(os.getenv("GUNICORN_TIMEOUT", 120))

# Graceful timeout for workers to finish requests before being killed.
graceful_timeout = int(os.getenv("GUNICORN_GRACEFUL_TIMEOUT", 60))

# Keep-alive connections timeout.
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", 5))

# --- Security Configuration ---
# Run Gunicorn with a non-root user and group.
# These should be created in your Dockerfile or on your host system.
user = os.getenv("GUNICORN_USER", "nobody")
group = os.getenv("GUNICORN_GROUP", "nogroup")

# Set process name for easier identification.
proc_name = "gemini-ai-chatbot"

# SSL/TLS configuration.
# It's recommended to handle SSL termination at a load balancer/reverse proxy level.
# These settings are here if you need to run Gunicorn with SSL directly.
if os.getenv("GUNICORN_USE_SSL", "false").lower() == "true":
    keyfile = os.getenv("SSL_KEYFILE", "/app/ssl/key.pem")
    certfile = os.getenv("SSL_CERTFILE", "/app/ssl/cert.pem")
    # Use modern TLS protocol.
    ssl_version = ssl.PROTOCOL_TLS_SERVER
    # Use a strong cipher suite.
    ciphers = (
        "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:"
        "ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:"
        "ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:"
        "DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384"
    )
else:
    keyfile = None
    certfile = None

# Headers from a trusted reverse proxy.
# '*' is a security risk. Only set this if your proxy setup is secure.
# It's better to list the specific IP addresses of your proxies.
forwarded_allow_ips = os.getenv("GUNICORN_FORWARDED_ALLOW_IPS", "127.0.0.1")
secure_scheme_headers = {
    "X-FORWARDED-PROTO": "https",
}

# --- Logging Configuration ---
# Log to stdout/stderr, the standard for containerized applications.
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")


# Use a custom JSON formatter for structured logging.
# This requires `python-json-logger` to be installed.
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "pid": record.process,
        }
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(log_record)


# Gunicorn's logconfig_dict for advanced logging setup.
logconfig_dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": JsonFormatter,
        },
        "generic": {
            "format": "%(asctime)s [%(process)d] [%(levelname)s] %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
            "class": "logging.Formatter",
        },
    },
    "handlers": {
        "error_console": {
            "class": "logging.StreamHandler",
            "formatter": "json"
            if os.getenv("FLASK_ENV") == "production"
            else "generic",
            "stream": "ext://sys.stderr",
        },
        "access_console": {
            "class": "logging.StreamHandler",
            "formatter": "json"
            if os.getenv("FLASK_ENV") == "production"
            else "generic",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "gunicorn.error": {
            "handlers": ["error_console"],
            "level": loglevel.upper(),
            "propagate": False,
        },
        "gunicorn.access": {
            "handlers": ["access_console"],
            "level": loglevel.upper(),
            "propagate": False,
        },
    },
    "root": {
        "level": loglevel.upper(),
        "handlers": ["error_console"],
    },
}


# --- Server Hooks ---
def on_starting(server):
    """Hook executed when the master process is starting."""
    server.log.info("🚀 Master process is starting...")


def when_ready(server):
    """Hook executed when the server is ready to accept connections."""
    server.log.info("✅ Server is ready. Spawning workers...")
    server.log.info(f"🔗 Bind: {bind}")
    server.log.info(f"👷 Worker Class: {worker_class}")
    server.log.info(f"🔥 Workers: {workers}, Threads: {threads}")
    server.log.info(f"⏱️ Timeout: {timeout}s")
    if keyfile:
        server.log.info("🔒 SSL is ENABLED.")


def on_exit(server):
    """Hook executed when the server is shutting down."""
    server.log.info("🛑 Server is shutting down. Goodbye!")


def worker_abort(worker):
    """Hook executed when a worker is aborted."""
    worker.log.critical(f"❌ Worker {worker.pid} aborted!")
    # Log the full traceback
    exc_info = traceback.format_exc()
    worker.log.error(f"Traceback: {exc_info}")


def worker_int(worker):
    """Hook executed when a worker receives SIGINT."""
    worker.log.warning(f"⚠️ Worker {worker.pid} received SIGINT. Graceful shutdown.")


# --- Environment Specific Overrides ---
if os.getenv("FLASK_ENV") == "development":
    # In development, use a single worker and enable auto-reloading.
    workers = 1
    threads = 1
    reload = True
    loglevel = "debug"
    # Update logconfig_dict for development verbosity
    logconfig_dict["loggers"]["gunicorn.error"]["level"] = "DEBUG"
    logconfig_dict["loggers"]["gunicorn.access"]["level"] = "DEBUG"
    logconfig_dict["root"]["level"] = "DEBUG"
