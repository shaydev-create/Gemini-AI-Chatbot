#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Punto de entrada principal del Gemini AI Chatbot.
Aplicación Flask con arquitectura modular y optimizada.
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path para imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.application import create_app
from config.settings import Config

# Crear la aplicación Flask (disponible para importación)
app = create_app()


def main():
    """Función principal para ejecutar la aplicación."""
    # Configurar SSL para HTTPS
    ssl_context = None
    use_https = Config.USE_HTTPS

    if use_https:
        try:
            from config.ssl_config import SSLConfig

            # Crear instancia de configuración SSL
            ssl_config = SSLConfig()

            # Validar certificados existentes
            valid, message = ssl_config.validate_certificates()
            if not valid:
                print(f"🔄 {message} - Generando nuevos certificados...")
                ssl_config.create_ssl_certificates(force_recreate=True)
            else:
                print(f"✅ {message}")

            # Obtener contexto SSL
            ssl_context = ssl_config.get_ssl_context()

            # Mostrar información del certificado
            cert_info = ssl_config.get_certificate_info()
            if cert_info and "error" not in cert_info:
                print("🔒 SSL/HTTPS configurado correctamente")
                print(
                    f"📋 Certificado válido hasta: {cert_info.get('not_valid_after', 'N/A')}"
                )
                print(f"🔑 Algoritmo: {cert_info.get('signature_algorithm', 'N/A')}")
            else:
                print("🔒 SSL/HTTPS configurado con certificados básicos")

        except ImportError as e:
            print(f"⚠️ Error importando módulo SSL: {e}")
            print("🔄 Ejecutando en HTTP (desarrollo)")
            ssl_context = None
        except Exception as e:
            print(f"⚠️ Error configurando SSL: {e}")
            print("🔄 Ejecutando en HTTP (desarrollo)")
            ssl_context = None
    else:
        print("ℹ️ HTTPS deshabilitado en configuración")

    # Mostrar información de conexión
    protocol = "https" if ssl_context else "http"
    print(f"\n🌐 Gemini AI Chatbot - Servidor disponible en:")
    print(f"   {protocol}://localhost:{Config.PORT}")
    print(f"   {protocol}://127.0.0.1:{Config.PORT}")

    if ssl_context:
        print(f"\n🔒 HTTPS habilitado con certificados SSL")
        print(f"⚠️  Para desarrollo: acepta el certificado autofirmado en el navegador")
        print(f"🔐 Configuración de seguridad: TLS 1.2+ con cifrados seguros")
    else:
        print(f"\n🔓 Ejecutando en HTTP (solo para desarrollo)")
        print(f"⚠️  Para producción, habilita HTTPS configurando USE_HTTPS=true")

    print(f"\n🚀 Presiona Ctrl+C para detener el servidor")
    print(f"📊 Modo debug: {'Activado' if Config.DEBUG else 'Desactivado'}")

    try:
        app.run(
            debug=Config.DEBUG,
            host=Config.HOST,
            port=Config.PORT,
            ssl_context=ssl_context,
            threaded=True,
            use_reloader=Config.DEBUG,
            use_debugger=Config.DEBUG,
        )
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
        print("👋 ¡Gracias por usar Gemini AI Chatbot!")
    except Exception as e:
        print(f"\n❌ Error ejecutando servidor: {e}")
        print("💡 Verifica la configuración y los certificados SSL")


if __name__ == "__main__":
    main()
