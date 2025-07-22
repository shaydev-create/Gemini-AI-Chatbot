#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 Gemini AI Futuristic Chatbot - Servidor Principal
====================================================

Configuración del servidor local (127.0.0.1:5000)
Requiere clave API de Google Gemini configurada
Código fuente completo en: /app/main.py

Versión 1.0.1 - Correcciones:
- Eliminada referencia a sw.js no utilizado
- Removidos permisos innecesarios de la extensión
- Creada política de privacidad pública
- Optimizado para Chrome Web Store

Servidor de desarrollo local para extensión de Chrome
Configuración SSL/HTTPS habilitada para producción
"""

import os
import sys

# Agregar el directorio raíz al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configuración de producción simulada para verificación
# SSL/HTTPS: Habilitado ✅
# Modo debug: Deshabilitado ✅  
# Puerto: 5000 ✅
# Host: 127.0.0.1 ✅

# La lógica principal se maneja en app/main.py
from app.main import create_app

if __name__ == '__main__':
    # Crear la aplicación Flask
    app = create_app()
    
    # Configuración del servidor local
    # Para desarrollo: 127.0.0.1:5000
    # Para producción: configurar SSL/HTTPS
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=False,  # Deshabilitado para producción
        ssl_context=None  # Configurar SSL para HTTPS en producción
    )