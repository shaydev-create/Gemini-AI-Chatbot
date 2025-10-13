from dotenv import load_dotenv
# Cargar variables de entorno desde .env ANTES de importar la app.
load_dotenv()

import os
from app.core.application import create_app

# La función create_app ahora devuelve una tupla (app, socketio)
app, socketio = create_app()

def main():
    """Punto de entrada principal para el servidor de desarrollo."""
    # CONFIGURACIÓN SIMPLE Y DIRECTA - Como en app_original.py que funciona
    host = '127.0.0.1'  # Hardcoded para que funcione
    port = 5000         # Hardcoded para que funcione
    debug = True        # Hardcoded para que funcione - ESTO ERA EL PROBLEMA
    
    print(f"🚀 Iniciando servidor en http://{host}:{port}")
    print(f"🔧 Debug mode: {debug}")
    print("📝 Configuración simplificada para garantizar funcionamiento")

    # Usar la configuración simple que funciona
    socketio.run(
        app,
        host=host,
        port=port,
        debug=debug,
        allow_unsafe_werkzeug=True
    )

if __name__ == "__main__":
    main()