#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 GEMINI AI CHATBOT - LAUNCHER PRINCIPAL
========================================

Script principal para iniciar la aplicación Flask directamente.
Usa el servidor de desarrollo optimizado.

USO:
    python run.py
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main():
    """Ejecuta la aplicación Flask directamente."""
    print("🚀 GEMINI AI CHATBOT")
    print("Iniciando servidor de desarrollo...")
    print()

    try:
        # Configurar variables de entorno básicas
        os.environ.setdefault('FLASK_ENV', 'development')
        os.environ.setdefault('FLASK_DEBUG', '1')
        
        # Importar y crear la aplicación Flask
        from app.core.application import get_flask_app
        
        # Crear la aplicación
        app = get_flask_app("development")
        
        print("✅ Aplicación iniciada correctamente")
        print("🌐 Servidor disponible en: http://127.0.0.1:5000")
        print("🛑 Presiona Ctrl+C para detener el servidor")
        print()
        
        # Ejecutar el servidor
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=True,
            use_reloader=True
        )
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("Asegúrate de que todas las dependencias estén instaladas:")
        print("poetry install")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Aplicación detenida por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
