#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 Gemini AI Futuristic Chatbot - Servidor Principal
====================================================

ARCHIVO RESTAURADO - Este era el punto de entrada que funcionaba antes
Configuración del servidor local (127.0.0.1:5000)
Requiere clave API de Google Gemini configurada
"""

import os
import sys

# CARGAR VARIABLES DE ENTORNO ANTES QUE NADA
from dotenv import load_dotenv

load_dotenv()

# Agregar el directorio raíz al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar la configuración original que funcionaba
from app.core.application import create_app

if __name__ == "__main__":
    # Crear la aplicación Flask usando la configuración original
    app, socketio = create_app()

    # Configuración del servidor local que funcionaba antes
    # Para desarrollo: 127.0.0.1:5000
    print("🚀 Iniciando servidor original (RESTAURADO)")
    print("📍 URL: http://127.0.0.1:5000")

    # Usar la configuración original que funcionaba
    socketio.run(
        app,
        host="127.0.0.1",
        port=5000,
        debug=True,  # Debug habilitado como estaba antes
        allow_unsafe_werkzeug=True,
    )
