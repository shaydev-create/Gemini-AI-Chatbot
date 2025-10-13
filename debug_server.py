#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 SERVIDOR DE DESARROLLO SIMPLE - SIN SOCKETIO
Para diagnosticar problemas con la API.
"""

from dotenv import load_dotenv
load_dotenv()

import os
from app.core.application import create_app

# Crear la aplicación
app, socketio = create_app()

if __name__ == "__main__":
    host = app.config.get("HOST", "127.0.0.1")
    port = int(app.config.get("PORT", 5000))
    debug = app.config.get("DEBUG", False)
    
    print(f"🚀 Iniciando servidor simple en http://{host}:{port}")
    print("📝 Nota: Sin WebSockets para diagnostico")
    
    # Usar solo Flask, sin SocketIO
    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=False  # Deshabilitar reloader para evitar problemas
    )