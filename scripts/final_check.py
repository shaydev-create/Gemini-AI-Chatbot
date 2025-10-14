#!/usr/bin/env python3
"""
Checklist final y verificación antes del lanzamiento
Verifica que todos los archivos estén listos
"""

import os
import zipfile
from pathlib import Path
from typing import List, Tuple


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
        with zipfile.ZipFile(zip_path, "r") as zip_file:
            files = zip_file.namelist()
            print(f"📁 Archivos en el ZIP ({len(files)}):")
            for file in files:
                print(f"   • {file}")

            # Verificar archivos críticos
            critical_files = [
                "manifest.json",
                "index.html",
                "background.js",
                "content.js",
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


def _check_zip_package(base_path: Path) -> bool:
    """Verificar el paquete ZIP principal."""
    print("\n📦 1. PACKAGE CHROME WEB STORE")
    zip_files = list(base_path.glob("gemini-ai-chatbot-chrome-*.zip"))

    if not zip_files:
        print("❌ ZIP Package no encontrado")
        return False

    zip_path = zip_files[0]
    if not check_file_exists(zip_path, "ZIP Package"):
        return False

    return check_zip_contents(zip_path)


def _check_files_section(section_name: str, files_list: List[Tuple[str, str]]) -> bool:
    """Verificar una sección de archivos."""
    print(f"\n{section_name}")
    all_exist = True

    for path, desc in files_list:
        if not check_file_exists(path, desc):
            all_exist = False

    return all_exist


def _display_final_results(all_good: bool):
    """Mostrar resultados finales de la verificación."""
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


def _get_verification_sections():
    """Definir las secciones de verificación para el checklist."""
    return [
        (
            "📸 2. SCREENSHOTS",
            [
                (
                    "chrome_store_assets/screenshots/screenshot_1_main.png",
                    "Screenshot Principal",
                ),
                (
                    "chrome_store_assets/screenshots/screenshot_2_features.png",
                    "Screenshot Características",
                ),
                ("chrome_store_assets/screenshots/promo_tile.png", "Tile Promocional"),
            ],
        ),
        (
            "🎨 3. ICONOS",
            [
                ("static/icons/chrome-webstore-icon-16x16.png", "Icono 16x16"),
                ("static/icons/chrome-webstore-icon-48x48.png", "Icono 48x48"),
                ("static/icons/chrome-webstore-icon-128x128.png", "Icono 128x128"),
                ("static/icons/chrome-webstore-icon-512x512.png", "Icono 512x512"),
            ],
        ),
        (
            "📄 4. DOCUMENTOS LEGALES",
            [
                ("templates/privacy_policy.html", "Privacy Policy"),
                ("templates/terms_of_service.html", "Terms of Service"),
            ],
        ),
        (
            "🔧 5. CONFIGURACIÓN API",
            [
                ("src/config/vertex_ai.py", "Configuración Vertex AI"),
                ("src/config/vertex_client.py", "Cliente Vertex AI"),
                (".env.vertex", "Variables de entorno Vertex AI"),
            ],
        ),
        (
            "📚 6. DOCUMENTACIÓN",
            [
                ("docs/LAUNCH_STEP_BY_STEP.md", "Guía paso a paso"),
                ("docs/EXECUTIVE_SUMMARY.md", "Resumen ejecutivo"),
                ("docs/VERTEX_AI_MIGRATION_STEPS.md", "Migración Vertex AI"),
            ],
        ),
    ]


def _verify_zip_package(base_path):
    """Verificar el paquete ZIP."""
    return _check_zip_package(base_path)


def _verify_all_sections(sections):
    """Verificar todas las secciones del checklist."""
    all_good = True
    for section_name, files_list in sections:
        if not _check_files_section(section_name, files_list):
            all_good = False
    return all_good


def main():
    """Verificación completa pre-lanzamiento."""
    print("🔍 VERIFICACIÓN FINAL PRE-LANZAMIENTO")
    print("=" * 50)

    base_path = Path(".")

    # Obtener secciones de verificación
    sections = _get_verification_sections()

    # Verificar ZIP package
    zip_ok = _verify_zip_package(base_path)

    # Verificar todas las secciones
    sections_ok = _verify_all_sections(sections)

    # Mostrar resultados finales
    all_good = zip_ok and sections_ok
    _display_final_results(all_good)

    return all_good


if __name__ == "__main__":
    main()
