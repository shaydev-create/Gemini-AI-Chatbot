#!/usr/bin/env python3
"""
📦 EMPAQUETADOR PARA CHROME WEB STORE
Crea un paquete completo listo para subir a Chrome Web Store
"""

import os
import shutil
import zipfile
from pathlib import Path
import json
import sys
from datetime import datetime


def create_chrome_extension_package():
    """Crear paquete de extensión de Chrome"""

    # Rutas
    project_root = os.path.dirname(os.path.abspath(__file__))
    # Subir un nivel desde scripts/
    project_root = os.path.dirname(project_root)
    chrome_extension_dir = os.path.join(project_root, 'chrome_extension')

    print(f"📁 Directorio del proyecto: {project_root}")
    print(f"📁 Directorio de extensión: {chrome_extension_dir}")

    # Verificar que existe el directorio de la extensión
    if not os.path.exists(chrome_extension_dir):
        print("❌ Error: No se encontró el directorio chrome_extension")
        return False

    # Archivos requeridos para la extensión
    required_files = [
        'manifest.json',
        'popup.html',
        'popup.js',
        'background.js',
        'content.js',
        'index.html'
    ]

    # Verificar archivos requeridos
    missing_files = []
    for file in required_files:
        file_path = os.path.join(chrome_extension_dir, file)
        if not os.path.exists(file_path):
            missing_files.append(file)

    if missing_files:
        print(
            f"❌ Error: Faltan archivos requeridos: {
                ', '.join(missing_files)}")
        return False

    # Verificar directorio de iconos
    icons_dir = os.path.join(chrome_extension_dir, 'icons')
    if not os.path.exists(icons_dir):
        print("❌ Error: No se encontró el directorio icons")
        return False

    required_icons = ['icon_16.png', 'icon_48.png', 'icon_128.png']
    missing_icons = []
    for icon in required_icons:
        icon_path = os.path.join(icons_dir, icon)
        if not os.path.exists(icon_path):
            missing_icons.append(icon)

    if missing_icons:
        print(f"❌ Error: Faltan iconos requeridos: {', '.join(missing_icons)}")
        return False

    # Leer y validar manifest.json
    manifest_path = os.path.join(chrome_extension_dir, 'manifest.json')
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        print(f"✅ Manifest válido - Nombre: {manifest.get('name', 'N/A')}")
        print(f"✅ Versión: {manifest.get('version', 'N/A')}")

    except json.JSONDecodeError as e:
        print(f"❌ Error: manifest.json no es válido: {e}")
        return False
    except Exception as e:
        print(f"❌ Error leyendo manifest.json: {e}")
        return False

    # Crear nombre del archivo ZIP
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"gemini-ai-chatbot-chrome-{timestamp}.zip"
    zip_path = os.path.join(project_root, zip_filename)

    print(f"📦 Creando paquete: {zip_filename}")

    try:
        # Crear archivo ZIP
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Agregar todos los archivos de la extensión
            for root, dirs, files in os.walk(chrome_extension_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Calcular ruta relativa desde chrome_extension_dir
                    arcname = os.path.relpath(file_path, chrome_extension_dir)
                    zipf.write(file_path, arcname)
                    print(f"  ➕ Agregado: {arcname}")

        # Verificar el archivo creado
        if os.path.exists(zip_path):
            file_size = os.path.getsize(zip_path)
            print(f"✅ Paquete creado exitosamente: {zip_filename}")
            print(f"📊 Tamaño del archivo: {file_size:,} bytes")

            # Listar contenido del ZIP para verificación
            print("\n📋 Contenido del paquete:")
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                for info in zipf.infolist():
                    print(f"  📄 {info.filename} ({info.file_size} bytes)")

            return True
        else:
            print("❌ Error: No se pudo crear el archivo ZIP")
            return False

    except Exception as e:
        print(f"❌ Error creando el paquete: {e}")
        return False


def validate_extension_structure():
    """Validar la estructura de la extensión"""

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    chrome_extension_dir = os.path.join(project_root, 'chrome_extension')

    print("🔍 Validando estructura de la extensión...")

    # Estructura esperada
    expected_structure = {
        'manifest.json': 'Archivo de configuración principal',
        'popup.html': 'Interfaz del popup',
        'popup.js': 'Lógica del popup',
        'background.js': 'Script de fondo',
        'content.js': 'Script de contenido',
        'index.html': 'Página principal de la aplicación',
        'icons/icon_16.png': 'Icono 16x16',
        'icons/icon_48.png': 'Icono 48x48',
        'icons/icon_128.png': 'Icono 128x128'
    }

    validation_results = []

    for file_path, description in expected_structure.items():
        full_path = os.path.join(chrome_extension_dir, file_path)
        exists = os.path.exists(full_path)

        if exists:
            file_size = os.path.getsize(full_path)
            status = f"✅ {file_path} - {description} ({file_size} bytes)"
        else:
            status = f"❌ {file_path} - {description} (FALTANTE)"

        validation_results.append((exists, status))
        print(f"  {status}")

    # Resumen
    total_files = len(validation_results)
    valid_files = sum(1 for exists, _ in validation_results if exists)

    print(f"\n📊 Resumen de validación:")
    print(f"  ✅ Archivos válidos: {valid_files}/{total_files}")
    print(
        f"  📈 Porcentaje de completitud: {(valid_files / total_files) * 100:.1f}%")

    return valid_files == total_files


def main():
    """Función principal"""
    print("🚀 Empaquetador de Extensión Chrome - Gemini AI Chatbot")
    print("=" * 60)

    # Validar estructura
    if not validate_extension_structure():
        print(
            "\n❌ La validación de estructura falló. Corrige los errores antes de continuar.")
        return False

    print("\n" + "=" * 60)

    # Crear paquete
    success = create_chrome_extension_package()

    if success:
        print("\n🎉 ¡Extensión empaquetada exitosamente!")
        print("\n📋 Próximos pasos:")
        print("  1. Abre Chrome y ve a chrome://extensions/")
        print("  2. Activa el 'Modo de desarrollador'")
        print("  3. Haz clic en 'Cargar extensión sin empaquetar'")
        print("  4. Selecciona la carpeta chrome_extension")
        print("  5. O usa 'Empaquetar extensión' con el archivo ZIP creado")
        print("\n🔗 Para publicar en Chrome Web Store:")
        print("  1. Ve a https://chrome.google.com/webstore/devconsole/")
        print("  2. Sube el archivo ZIP creado")
        print("  3. Completa la información requerida")
        print("  4. Envía para revisión")

        return True
    else:
        print("\n❌ Error al empaquetar la extensión")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
