#!/usr/bin/env python3
"""
Checklist final y verificación antes del lanzamiento
Verifica que todos los archivos estén listos
"""

import os
import zipfile
from pathlib import Path


def check_file_exists(file_path, description):
    """Verificar si un archivo existe"""
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        print(f"✅ {description}: {file_path} ({size} bytes)")
        return True
    else:
        print(f"❌ {description}: {file_path} - NO ENCONTRADO")
        return False


def check_zip_contents(zip_path):
    """Verificar contenido del ZIP"""
    print(f"\n📦 VERIFICANDO CONTENIDO DEL ZIP: {zip_path}")

    if not os.path.exists(zip_path):
        print("❌ ZIP no encontrado")
        return False

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            files = zip_file.namelist()
            print(f"📁 Archivos en el ZIP ({len(files)}):")
            for file in files:
                print(f"   • {file}")

            # Verificar archivos críticos
            critical_files = [
                'manifest.json',
                'index.html',
                'background.js',
                'content.js'
            ]

            missing = []
            for critical in critical_files:
                if not any(critical in f for f in files):
                    missing.append(critical)

            if missing:
                print(f"⚠️ Archivos críticos faltantes: {missing}")
            else:
                print("✅ Todos los archivos críticos presentes")

            return len(missing) == 0

    except Exception as e:
        print(f"❌ Error verificando ZIP: {e}")
        return False


def main():
    """Verificación completa pre-lanzamiento"""

    print("🔍 VERIFICACIÓN FINAL PRE-LANZAMIENTO")
    print("=" * 50)

    base_path = Path(".")
    all_good = True

    # 1. Verificar ZIP principal
    print("\n📦 1. PACKAGE CHROME WEB STORE")
    zip_files = list(base_path.glob("gemini-ai-chatbot-chrome-*.zip"))
    if zip_files:
        zip_path = zip_files[0]
        if check_file_exists(zip_path, "ZIP Package"):
            check_zip_contents(zip_path)
        else:
            all_good = False
    else:
        print("❌ ZIP Package no encontrado")
        all_good = False

    # 2. Verificar screenshots
    print("\n📸 2. SCREENSHOTS")
    screenshots = [
        ("chrome_store_assets/screenshots/screenshot_1_main.png",
         "Screenshot Principal"),
        ("chrome_store_assets/screenshots/screenshot_2_features.png",
         "Screenshot Características"),
        ("chrome_store_assets/screenshots/promo_tile.png",
         "Tile Promocional")]

    for path, desc in screenshots:
        if not check_file_exists(path, desc):
            all_good = False

    # 3. Verificar iconos
    print("\n🎨 3. ICONOS")
    icons = [
        ("static/icons/chrome-webstore-icon-16x16.png", "Icono 16x16"),
        ("static/icons/chrome-webstore-icon-48x48.png", "Icono 48x48"),
        ("static/icons/chrome-webstore-icon-128x128.png", "Icono 128x128"),
        ("static/icons/chrome-webstore-icon-512x512.png", "Icono 512x512")
    ]

    for path, desc in icons:
        if not check_file_exists(path, desc):
            all_good = False

    # 4. Verificar documentos legales
    print("\n📄 4. DOCUMENTOS LEGALES")
    legal_docs = [
        ("templates/privacy_policy.html", "Privacy Policy"),
        ("templates/terms_of_service.html", "Terms of Service")
    ]

    for path, desc in legal_docs:
        if not check_file_exists(path, desc):
            all_good = False

    # 5. Verificar configuración API
    print("\n🔧 5. CONFIGURACIÓN API")
    api_files = [
        ("src/config/vertex_ai.py", "Configuración Vertex AI"),
        ("src/config/vertex_client.py", "Cliente Vertex AI"),
        (".env.vertex", "Variables de entorno Vertex AI")
    ]

    for path, desc in api_files:
        if not check_file_exists(path, desc):
            all_good = False

    # 6. Verificar documentación
    print("\n📚 6. DOCUMENTACIÓN")
    docs = [
        ("docs/LAUNCH_STEP_BY_STEP.md", "Guía paso a paso"),
        ("docs/EXECUTIVE_SUMMARY.md", "Resumen ejecutivo"),
        ("docs/VERTEX_AI_MIGRATION_STEPS.md", "Migración Vertex AI")
    ]

    for path, desc in docs:
        if not check_file_exists(path, desc):
            all_good = False

    # Resultado final
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 ¡TODO LISTO PARA LANZAMIENTO!")
        print("\n🚀 PRÓXIMOS PASOS:")
        print("1. Ir a: https://chrome.google.com/webstore/devconsole/")
        print("2. Pagar $5 USD (registro desarrollador)")
        print("3. Subir ZIP package")
        print("4. Completar información")
        print("5. Subir screenshots")
        print("6. Enviar para revisión")

        print("\n💰 INVERSIÓN TOTAL: $5 USD")
        print("⏱️ TIEMPO ESTIMADO: 30-45 minutos")
        print("📅 PUBLICACIÓN: 1-3 días")

    else:
        print("⚠️ HAY ARCHIVOS FALTANTES")
        print("Revisa los errores arriba y ejecuta los scripts necesarios")

    return all_good


if __name__ == "__main__":
    main()
