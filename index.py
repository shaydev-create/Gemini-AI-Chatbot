#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 ENTRY POINT PRINCIPAL PARA VERCEL
====================================

Archivo principal que Vercel usará para ejecutar la aplicación Flask.
"""

import os
import sys

# Añadir el directorio actual al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Importar y crear la aplicación
    from app.core.application import create_app
    
    # Crear la aplicación con configuración de producción
    app, socketio = create_app()
    
    # Para debugging en Vercel
    app.logger.info("🚀 Aplicación Flask iniciada desde index.py")
    app.logger.info(f"🔧 Modo debug: {app.debug}")
    app.logger.info(f"🌐 Configuración: {app.config.get('ENV', 'unknown')}")
    
    # Verificar variables de entorno críticas
    gemini_key = os.environ.get('GEMINI_API_KEY')
    if gemini_key:
        app.logger.info("🔑 GEMINI_API_KEY configurada correctamente")
    else:
        app.logger.warning("⚠️ GEMINI_API_KEY no encontrada")
    
    # Función para compatibilidad con Vercel
    def handler(request):
        """Handler para requests de Vercel."""
        return app(request.environ, lambda status, headers: None)
    
    # Entry point para Vercel
    if __name__ == "__main__":
        app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

except Exception as e:
    # En caso de error, crear una app mínima que muestre el error
    from flask import Flask
    
    app = Flask(__name__)
    
    @app.route('/')
    def error_info():
        return f"""
        <html>
        <head><title>Error de Configuración</title></head>
        <body>
        <h1>🚨 Error de Configuración</h1>
        <p><strong>Error:</strong> {str(e)}</p>
        <p><strong>Tipo:</strong> {type(e).__name__}</p>
        <p><strong>Directorio actual:</strong> {os.getcwd()}</p>
        <p><strong>Python path:</strong> {sys.path}</p>
        <p><strong>Variables de entorno FLASK:</strong></p>
        <ul>
        <li>FLASK_ENV: {os.environ.get('FLASK_ENV', 'No definida')}</li>
        <li>GEMINI_API_KEY: {'Configurada' if os.environ.get('GEMINI_API_KEY') else 'No configurada'}</li>
        </ul>
        <hr>
        <p>Verifica la configuración en Vercel Dashboard</p>
        </body>
        </html>
        """
    
    print(f"❌ Error al crear la aplicación: {e}")
    import traceback
    traceback.print_exc()