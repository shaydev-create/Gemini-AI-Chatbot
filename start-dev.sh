#!/bin/sh
# Script de wrapper para ejecutar Flask en desarrollo
export PATH="/app/.venv/bin:$PATH"
exec /app/.venv/bin/python -m flask run --host=0.0.0.0 --port=5000