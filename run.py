#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 GEMINI AI CHATBOT - LAUNCHER PRINCIPAL
========================================

Script principal para iniciar la aplicación Flask directamente.
Usa el servidor de desarrollo optimizado.

NUEVO: Detecta automáticamente si está en Docker o local:
- Si está en Docker: Solo ejecuta Flask
- Si está local: Gestiona Docker automáticamente (inicia y para)

USO:
    python run.py
"""

import atexit
import os
import signal
import subprocess
import sys
from pathlib import Path

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv

    load_dotenv()
    print("✅ Variables de entorno cargadas desde .env")
except ImportError:
    print("⚠️  python-dotenv no encontrado, usando variables de entorno del sistema")
except Exception as e:
    print(f"⚠️  Error cargando .env: {e}")

# Agregar el directorio raíz al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def is_running_in_docker():
    """Detecta si el script está ejecutándose dentro de Docker."""
    return os.path.exists("/.dockerenv") or os.environ.get("DOCKER_CONTAINER") == "true"


def is_docker_available():
    """Verifica si Docker está disponible y el daemon está ejecutándose."""
    try:
        # Verificar que Docker está instalado
        subprocess.run(["docker", "--version"], capture_output=True, check=True, timeout=5)
        subprocess.run(["docker-compose", "--version"], capture_output=True, check=True, timeout=5)

        # Verificar que el daemon está ejecutándose
        subprocess.run(["docker", "info"], capture_output=True, check=True, timeout=10)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


def start_docker_services():
    """Inicia los servicios Docker si no están ejecutándose."""
    print("🐳 Verificando servicios Docker...")

    try:
        # Verificar si los contenedores ya están ejecutándose
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=10,  # Timeout de 10 segundos
            check=True,
        )

        running_containers = result.stdout.strip().split("\n")
        required_containers = ["gemini-db", "gemini-cache"]

        missing_containers = [c for c in required_containers if c not in running_containers]

        if missing_containers:
            print(f"🚀 Iniciando servicios Docker: {', '.join(missing_containers)}")

            # Iniciar solo los servicios de soporte (DB y Cache)
            subprocess.run(
                ["docker-compose", "-f", "docker-compose.yml", "-f", "docker-compose.dev.yml", "up", "-d", "db", "cache"],
                cwd=project_root,
                check=True,
            )

            print("✅ Servicios Docker iniciados correctamente")
            return True
        else:
            print("✅ Servicios Docker ya están ejecutándose")
            return True

    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"❌ Error iniciando servicios Docker: {e}")
        print("⚠️  Docker Desktop podría no estar ejecutándose o está muy lento.")
        print("💡 Iniciando aplicación sin servicios Docker externos...")
        print("📋 Para usar la base de datos, asegúrate de que Docker Desktop esté ejecutándose")
        return False


def stop_docker_services():
    """Para los servicios Docker al cerrar la aplicación."""
    if not is_docker_available():
        print("⏩ Docker no disponible, saltando limpieza de contenedores")
        return

    print("\n🐳 Parando servicios Docker...")

    try:
        subprocess.run(
            ["docker-compose", "-f", "docker-compose.yml", "-f", "docker-compose.dev.yml", "down"],
            cwd=project_root,
            check=True,
            timeout=15,
        )

        print("✅ Servicios Docker detenidos correctamente")
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"⚠️  No se pudieron detener los servicios Docker: {e}")
        print("💡 Esto puede suceder si Docker Desktop no está ejecutándose")


# Flag global para evitar múltiples limpiezas
_cleanup_done = False


def perform_cleanup():
    """Ejecuta la limpieza una sola vez."""
    global _cleanup_done
    if _cleanup_done:
        return  # Ya se ejecutó la limpieza

    _cleanup_done = True
    if not is_running_in_docker() and is_docker_available():
        stop_docker_services()


def setup_cleanup_handlers():
    """Configura manejadores para limpiar al cerrar."""
    # Solo registrar handlers en el proceso principal (no en reloader)
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        # Registrar cleanup para salida normal
        atexit.register(perform_cleanup)

        # Manejador para Ctrl+C
        def signal_handler(sig, frame):
            print(f"\n🛑 Señal {sig} recibida. Cerrando aplicación...")
            perform_cleanup()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)


def main():
    """Ejecuta la aplicación Flask directamente."""
    # Solo mostrar mensajes en el proceso principal, no en el reloader
    is_reloader = os.environ.get("WERKZEUG_RUN_MAIN") == "true"

    if not is_reloader:
        print("🚀 GEMINI AI CHATBOT")
        print("Iniciando servidor de desarrollo...")

        # Detectar entorno
        in_docker = is_running_in_docker()
        print(f"📍 Entorno detectado: {'Docker Container' if in_docker else 'Local'}")

        if not in_docker:
            # Modo local: gestionar Docker automáticamente
            if not is_docker_available():
                print("❌ Docker no está disponible.")
                print("💡 Ejecutándose sin servicios externos (PostgreSQL/Redis)")
                print("⚠️  Algunas funciones pueden estar limitadas")
            else:
                # Configurar limpieza automática
                setup_cleanup_handlers()

                # Intentar iniciar servicios Docker
                docker_success = start_docker_services()

                if docker_success is not False:
                    # Esperar un momento para que los servicios estén listos
                    import time

                    print("⏳ Esperando que los servicios estén listos...")
                    time.sleep(3)

        print()
    else:
        # En el proceso de reloader, solo configurar handlers sin mensajes repetidos
        if not is_running_in_docker() and is_docker_available():
            setup_cleanup_handlers()

    try:
        # Configurar variables de entorno básicas
        os.environ.setdefault("FLASK_ENV", "development")
        os.environ.setdefault("FLASK_DEBUG", "1")

        # Importar y crear la aplicación Flask
        from app.core.application import get_flask_app

        # Crear la aplicación
        app = get_flask_app("development")

        # Solo mostrar mensajes en el proceso principal
        if not is_reloader:
            print("✅ Aplicación iniciada correctamente")
            print("🛑 Presiona Ctrl+C para detener el servidor")
            if not is_running_in_docker() and is_docker_available():
                print("🔄 Los servicios de Docker se detendrán automáticamente al cerrar")
            print()

        # Ejecutar el servidor (puerto 3000 por restricciones recientes de Windows)
        # NOTA: El puerto 5000 funcionaba antes, pero Windows lo bloqueó recientemente
        host = os.environ.get("FLASK_RUN_HOST", "127.0.0.1")
        port = int(os.environ.get("FLASK_RUN_PORT", "3000"))  # Puerto 3000 - evita bloqueo reciente de Windows
        debug = os.environ.get("FLASK_DEBUG", "1") == "1"
        use_reloader = os.environ.get("FLASK_USE_RELOADER", "true").lower() == "true"

        if not is_reloader:
            print(f"🌐 Servidor disponible en: http://{host}:{port}")

        app.run(host=host, port=port, debug=debug, use_reloader=use_reloader)

    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("Asegúrate de que todas las dependencias estén instaladas:")
        print("poetry install")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Aplicación detenida por el usuario")
        perform_cleanup()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        perform_cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()
