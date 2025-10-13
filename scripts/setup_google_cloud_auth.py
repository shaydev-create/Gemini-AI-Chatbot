#!/usr/bin/env python3
"""Script para configurar autenticación de Google Cloud y Vertex AI."""

import logging
import os
import sys
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_requirements() -> bool:
    """Verificar que las dependencias necesarias estén instaladas.

    Returns:
        bool: True si todas las dependencias están disponibles
    """
    required_packages = [
        "google-cloud-aiplatform",
        "google-auth",
        "google-auth-oauthlib",
        "vertexai",
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            logger.info(f"✅ {package} está instalado")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"❌ {package} no está instalado")

    if missing_packages:
        logger.error("\n🔧 Para instalar las dependencias faltantes, ejecuta:")
        logger.error(f"pip install {' '.join(missing_packages)}")
        return False

    return True


def get_project_root() -> Path:
    """Obtener la ruta raíz del proyecto.

    Returns:
        Path: Ruta al directorio raíz del proyecto
    """
    current_path = Path(__file__).parent

    # Buscar hacia arriba hasta encontrar requirements.txt o .git
    while current_path.parent != current_path:
        if (current_path / "requirements.txt").exists() or (
            current_path / ".git"
        ).exists():
            return current_path
        current_path = current_path.parent

    return Path(__file__).parent.parent


def create_service_account_guide() -> str:
    """Crear guía para configurar service account.

    Returns:
        str: Guía en formato texto
    """
    guide = """
🔐 GUÍA PARA CONFIGURAR GOOGLE CLOUD SERVICE ACCOUNT

1. Crear proyecto en Google Cloud Console:
   - Ir a: https://console.cloud.google.com/
   - Crear nuevo proyecto o seleccionar existente
   - Anotar el PROJECT_ID

2. Habilitar APIs necesarias:
   - Vertex AI API
   - AI Platform API
   - Cloud Resource Manager API

   Comando CLI:
   gcloud services enable aiplatform.googleapis.com
   gcloud services enable ml.googleapis.com
   gcloud services enable cloudresourcemanager.googleapis.com

3. Crear Service Account:
   - Ir a: IAM & Admin > Service Accounts
   - Crear nueva cuenta de servicio
   - Nombre: vertex-ai-service
   - Descripción: Service account para Vertex AI

4. Asignar roles necesarios:
   - Vertex AI User
   - AI Platform Developer
   - Storage Object Viewer (si usas Cloud Storage)

5. Crear y descargar clave JSON:
   - En la cuenta de servicio creada
   - Ir a "Keys" > "Add Key" > "Create new key"
   - Seleccionar JSON
   - Descargar archivo

6. Configurar variables de entorno:
   - GOOGLE_APPLICATION_CREDENTIALS=ruta/al/archivo.json
   - VERTEX_AI_PROJECT_ID=tu-project-id
   - VERTEX_AI_LOCATION=us-central1 (o tu región preferida)

7. Verificar configuración:
   - Ejecutar: python scripts/setup_google_cloud_auth.py --verify
"""
    return guide


def setup_credentials_directory() -> Path:
    """Crear directorio para credenciales.

    Returns:
        Path: Ruta al directorio de credenciales
    """
    project_root = get_project_root()
    credentials_dir = project_root / "credentials"

    # Crear directorio si no existe
    credentials_dir.mkdir(exist_ok=True)

    # Crear .gitignore para proteger credenciales
    gitignore_path = credentials_dir / ".gitignore"
    if not gitignore_path.exists():
        with open(gitignore_path, "w") as f:
            f.write("# Ignorar todos los archivos de credenciales\n")
            f.write("*.json\n")
            f.write("*.key\n")
            f.write("*.pem\n")
            f.write("service-account-*\n")

    logger.info(f"📁 Directorio de credenciales: {credentials_dir}")
    return credentials_dir


def create_env_template() -> None:
    """Crear template de variables de entorno."""
    project_root = get_project_root()
    env_template_path = project_root / ".env.vertex_ai.template"

    template_content = """
# Configuración de Google Cloud y Vertex AI
# Copiar a .env y completar con valores reales

# === GOOGLE CLOUD CONFIGURATION ===
# ID del proyecto en Google Cloud
VERTEX_AI_PROJECT_ID=tu-project-id

# Región donde ejecutar Vertex AI (ej: us-central1, europe-west1)
VERTEX_AI_LOCATION=us-central1

# Ruta al archivo JSON de service account
# Puede ser absoluta o relativa al proyecto
GOOGLE_APPLICATION_CREDENTIALS=credentials/service-account-key.json

# === VERTEX AI CONFIGURATION ===
# Habilitar Vertex AI (true/false)
VERTEX_AI_ENABLED=true

# Modelo por defecto (gemini-1.5-flash, gemini-1.5-pro, gemini-1.0-pro)
VERTEX_AI_DEFAULT_MODEL=gemini-1.5-flash

# Límites de uso
VERTEX_AI_MAX_DAILY_COST=10.00
VERTEX_AI_MAX_TOKENS_PER_REQUEST=8192
VERTEX_AI_MAX_DAILY_REQUESTS=1000

# === FALLBACK CONFIGURATION ===
# API Key para Gemini API (fallback)
GOOGLE_API_KEY=tu-api-key-aqui
GEMINI_API_KEY=tu-api-key-aqui

# === MONITORING ===
# Habilitar logging detallado
VERTEX_AI_DEBUG=false

# Intervalo de health check en segundos
VERTEX_AI_HEALTH_CHECK_INTERVAL=300
"""

    with open(env_template_path, "w", encoding="utf-8") as f:
        f.write(template_content)

    logger.info(f"📝 Template creado: {env_template_path}")
    logger.info("💡 Copia este archivo a .env y completa con tus valores")


def verify_authentication() -> bool:
    """Verificar que la autenticación esté configurada correctamente.

    Returns:
        bool: True si la autenticación funciona
    """
    try:
        from google.auth import default

        __import__("google.cloud.aiplatform")
        import vertexai

        logger.info("🔍 Verificando autenticación...")

        # Verificar credenciales por defecto
        try:
            credentials, project_id = default()
            logger.info(f"✅ Credenciales encontradas para proyecto: {project_id}")
        except Exception as e:
            logger.error(f"❌ Error obteniendo credenciales por defecto: {e}")
            return False

        # Verificar variables de entorno
        vertex_project = os.getenv("VERTEX_AI_PROJECT_ID")
        vertex_location = os.getenv("VERTEX_AI_LOCATION", "us-central1")

        if not vertex_project:
            logger.error("❌ VERTEX_AI_PROJECT_ID no está configurado")
            return False

        logger.info(f"✅ Proyecto Vertex AI: {vertex_project}")
        logger.info(f"✅ Ubicación: {vertex_location}")

        # Intentar inicializar Vertex AI
        try:
            vertexai.init(project=vertex_project, location=vertex_location)
            logger.info("✅ Vertex AI inicializado correctamente")
        except Exception as e:
            logger.error(f"❌ Error inicializando Vertex AI: {e}")
            return False

        # Verificar acceso a modelos
        try:
            from vertexai.generative_models import GenerativeModel

            GenerativeModel("gemini-1.5-flash")
            logger.info("✅ Modelo Gemini accesible")
        except Exception as e:
            logger.warning(f"⚠️ Advertencia con modelo: {e}")

        logger.info("🎉 Autenticación verificada correctamente")
        return True

    except ImportError as e:
        logger.error(f"❌ Dependencias faltantes: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error verificando autenticación: {e}")
        return False


def show_current_config() -> None:
    """Mostrar configuración actual."""
    logger.info("\n📋 CONFIGURACIÓN ACTUAL:")

    # Variables de entorno relevantes
    env_vars = [
        "GOOGLE_APPLICATION_CREDENTIALS",
        "VERTEX_AI_PROJECT_ID",
        "VERTEX_AI_LOCATION",
        "VERTEX_AI_ENABLED",
        "VERTEX_AI_DEFAULT_MODEL",
        "GOOGLE_API_KEY",
        "GEMINI_API_KEY",
    ]

    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Ocultar claves sensibles
            if "key" in var.lower() or "credentials" in var.lower():
                display_value = (
                    f"{value[:10]}...{value[-4:]}" if len(value) > 14 else "***"
                )
            else:
                display_value = value
            logger.info(f"  {var}: {display_value}")
        else:
            logger.info(f"  {var}: ❌ No configurado")


def main():
    """Función principal."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Configurar autenticación de Google Cloud y Vertex AI"
    )
    parser.add_argument(
        "--verify", action="store_true", help="Verificar configuración actual"
    )
    parser.add_argument(
        "--setup", action="store_true", help="Configurar directorios y templates"
    )
    parser.add_argument(
        "--guide", action="store_true", help="Mostrar guía de configuración"
    )
    parser.add_argument(
        "--config", action="store_true", help="Mostrar configuración actual"
    )

    args = parser.parse_args()

    # Si no se especifica ninguna acción, mostrar ayuda
    if not any([args.verify, args.setup, args.guide, args.config]):
        parser.print_help()
        return

    logger.info("🚀 Configurador de Google Cloud y Vertex AI")
    logger.info("=" * 50)

    # Verificar dependencias
    if not check_requirements():
        sys.exit(1)

    # Ejecutar acciones solicitadas
    if args.guide:
        print(create_service_account_guide())

    if args.setup:
        logger.info("\n🔧 Configurando directorios y templates...")
        setup_credentials_directory()
        create_env_template()
        logger.info("✅ Configuración inicial completada")

    if args.config:
        show_current_config()

    if args.verify:
        logger.info("\n🔍 Verificando configuración...")
        if verify_authentication():
            logger.info("\n🎉 ¡Configuración verificada exitosamente!")
        else:
            logger.error("\n❌ Configuración incompleta o incorrecta")
            logger.info("\n💡 Ejecuta con --guide para ver la guía de configuración")
            sys.exit(1)


if __name__ == "__main__":
    main()
