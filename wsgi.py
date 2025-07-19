#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 WSGI ENTRY POINT - GEMINI AI CHATBOT

Punto de entrada WSGI para servidores de producción como Gunicorn.
Configuración optimizada para producción con logging y manejo de errores.
"""

import os
import sys
import logging
from pathlib import Path

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configurar variables de entorno para producción
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_DEBUG', 'False')

# Configurar logging para WSGI
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/wsgi.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

try:
    # Importar la aplicación desde app.main
    from app.main import app
    
    # Configuración adicional para producción
    if not app.debug:
        # Configurar logging de errores
        if not app.logger.handlers:
            file_handler = logging.FileHandler('logs/app_errors.log')
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.ERROR)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
    
    logger.info("🚀 WSGI application loaded successfully")
    
except Exception as e:
    logger.error(f"❌ Error loading WSGI application: {e}")
    raise

# Punto de entrada para Gunicorn
application = app

if __name__ == "__main__":
    # Para testing local del WSGI
    app.run(host='0.0.0.0', port=5000)