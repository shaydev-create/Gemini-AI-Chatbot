#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 LAUNCHER MEJORADO - GEMINI AI CHATBOT
======================================

Script de lanzamiento mejorado que maneja dependencias problemáticas
y proporciona un inicio más estable de la aplicación.
"""

import os
import sys
import signal
import atexit
from pathlib import Path


def setup_environment():
    """Configura el entorno antes de importar dependencias problemáticas."""
    # Agregar el directorio del proyecto al path
    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # Configurar variables de entorno para evitar conflictos
    os.environ.setdefault("PYTHONPATH", str(project_root))

    # Configurar encoding para evitar problemas en Windows
    if sys.platform == "win32":
        os.environ.setdefault("PYTHONIOENCODING", "utf-8")

    # Suprimir warnings de deprecación que pueden causar problemas
    import warnings

    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=UserWarning)


def handle_exit():
    """Maneja la salida limpia de la aplicación."""
    print("\n🛑 Cerrando Gemini AI Chatbot...")
    print("✅ Aplicación cerrada correctamente.")


def signal_handler(signum, frame):
    """Maneja las señales del sistema para cerrar limpiamente."""
    print(f"\n📡 Señal recibida: {signum}")
    handle_exit()
    sys.exit(0)


def main():
    """Función principal mejorada."""
    # Configurar el entorno antes de cualquier import
    setup_environment()

    # Registrar manejadores de salida
    atexit.register(handle_exit)
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, signal_handler)

    print("🔧 GEMINI AI CHATBOT - LAUNCHER MEJORADO")
    print("=" * 50)
    print(f"🐍 Python: {sys.version.split()[0]}")
    print(f"📁 Directorio: {Path(__file__).parent}")

    try:
        # Cargar variables de entorno
        print("📋 Cargando configuración...")
        from dotenv import load_dotenv

        load_dotenv()

        # Importar la aplicación de manera controlada
        print("🏗️  Inicializando aplicación...")
        from app.core.application import create_app

        # Crear la aplicación
        print("⚙️  Creando instancia de la aplicación...")
        app, socketio = create_app()

        # Configuración del servidor
        host = "127.0.0.1"
        port = 5000
        debug = True

        print(f"\n🚀 INICIANDO SERVIDOR")
        print(f"   📍 URL: http://{host}:{port}")
        print(f"   🔧 Debug: {debug}")
        print(f"   ⚡ SocketIO: Habilitado")
        print("\n💡 Para detener la aplicación, presiona Ctrl+C")
        print("=" * 50)

        # Ejecutar el servidor
        socketio.run(
            app,
            host=host,
            port=port,
            debug=debug,
            allow_unsafe_werkzeug=True,
            use_reloader=False,  # Deshabilitamos el reloader para evitar problemas
        )

    except KeyboardInterrupt:
        print("\n🛑 Interrupción por teclado detectada")
        handle_exit()
        sys.exit(0)

    except ImportError as e:
        print(f"\n❌ Error de importación: {e}")
        print("💡 Posibles soluciones:")
        print("   1. Instalar dependencias: pip install -r requirements.txt")
        print("   2. Verificar el entorno virtual")
        print("   3. Verificar GOOGLE_API_KEY en .env")
        sys.exit(1)

    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        print(f"🔍 Tipo de error: {type(e).__name__}")
        import traceback

        print("📋 Traceback completo:")
        traceback.print_exc()
        sys.exit(1)

    finally:
        print("\n🔄 Proceso de cierre completado")


if __name__ == "__main__":
    main()
