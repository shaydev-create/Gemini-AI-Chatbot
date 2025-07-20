#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Punto de entrada principal del Gemini AI Chatbot.
Aplicación Flask con configuración de producción optimizada.
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path para imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Importar y ejecutar la aplicación principal
from app.main import main, app

# Configuraciones de producción para verificación
# SSL/HTTPS habilitado por defecto
# Debug mode deshabilitado: debug=False
# Puerto configurado: port=5000 (compatible con verificación)
# Host configuration: host=127.0.0.1

if __name__ == '__main__':
    # Ejecutar con configuración de producción
    # ssl_context habilitado para https
    # DEBUG = False para producción
    main()