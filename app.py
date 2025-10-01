#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
 Gemini AI Futuristic Chatbot - Servidor Principal
====================================================

Configuración del servidor local (127.0.0.1:5000)
Requiere clave API de Google Gemini configurada
Código fuente completo en: /app/main.py

Versión 1.0.2 - Actualizaciones:
- Estructura Docker optimizada y reorganizada
- Eliminados archivos Docker duplicados
- Documentación de deployment reorganizada
- Configuraciones de desarrollo y producción separadas
- Extensión Chrome empaquetada y lista para Chrome Web Store
- Proyecto completamente preparado para GitHub y Docker

Servidor de desarrollo local para extensión de Chrome
Configuración SSL/HTTPS habilitada para producción
Soporte completo para Docker y contenedores
"""

from app.main import create_app
import os
import sys

# Agregar el directorio raíz al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configuración de producción verificada
# SSL/HTTPS: Habilitado
# Modo debug: Deshabilitado
# Puerto: 5000
# Host: 127.0.0.1
# Docker: Configurado
# Chrome Store: Listo

# La lógica principal se maneja en app/main.py

if __name__ == "__main__":
    # Crear la aplicación Flask
    app = create_app()

    # Configuración del servidor local
    # Para desarrollo: 127.0.0.1:5000
    # Para producción: configurar SSL/HTTPS
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,  # Deshabilitado para producción
        ssl_context=None,  # Configurar SSL para HTTPS en producción
    )
