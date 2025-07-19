#!/usr/bin/env python3
"""
🎨 CONVERTIDOR DE ICONOS SVG A PNG PARA CHROME WEB STORE
Convierte los iconos SVG optimizados a PNG para cumplir con los requisitos de Chrome Web Store
"""

import os
import subprocess
import sys
from pathlib import Path

def convert_svg_to_png():
    """Convierte iconos SVG a PNG usando cairosvg o inkscape"""
    
    # Directorio de iconos
    icons_dir = Path("static/icons")
    
    # Iconos a convertir para Chrome Web Store
    conversions = [
        {
            "input": "chrome-webstore-icon-128x128.svg",
            "output": "chrome-webstore-icon-128x128.png",
            "size": (128, 128)
        },
        {
            "input": "chrome-webstore-icon-128x128.svg", 
            "output": "chrome-webstore-icon-16x16.png",
            "size": (16, 16)
        },
        {
            "input": "chrome-webstore-icon-128x128.svg",
            "output": "chrome-webstore-icon-48x48.png", 
            "size": (48, 48)
        },
        {
            "input": "playstore-icon-512x512.svg",
            "output": "chrome-webstore-icon-512x512.png",
            "size": (512, 512)
        }
    ]
    
    print("🎨 Iniciando conversión de iconos SVG a PNG...")
    
    # Intentar usar cairosvg primero
    try:
        import cairosvg
        from PIL import Image
        import io
        
        for conversion in conversions:
            input_path = icons_dir / conversion["input"]
            output_path = icons_dir / conversion["output"]
            
            if not input_path.exists():
                print(f"❌ No se encontró: {input_path}")
                continue
                
            print(f"🔄 Convirtiendo {conversion['input']} → {conversion['output']}")
            
            # Convertir SVG a PNG usando cairosvg
            png_data = cairosvg.svg2png(
                url=str(input_path),
                output_width=conversion["size"][0],
                output_height=conversion["size"][1]
            )
            
            # Guardar PNG
            with open(output_path, 'wb') as f:
                f.write(png_data)
                
            print(f"✅ Creado: {output_path}")
            
        print("🎉 ¡Conversión completada exitosamente!")
        return True
        
    except ImportError:
        print("⚠️ cairosvg no está instalado. Intentando con Pillow...")
        
        # Método alternativo usando Pillow (limitado para SVG)
        try:
            from PIL import Image
            from wand.image import Image as WandImage
            
            for conversion in conversions:
                input_path = icons_dir / conversion["input"]
                output_path = icons_dir / conversion["output"]
                
                if not input_path.exists():
                    print(f"❌ No se encontró: {input_path}")
                    continue
                    
                print(f"🔄 Convirtiendo {conversion['input']} → {conversion['output']}")
                
                # Usar Wand (ImageMagick) para SVG
                with WandImage(filename=str(input_path)) as img:
                    img.format = 'png'
                    img.resize(conversion["size"][0], conversion["size"][1])
                    img.save(filename=str(output_path))
                    
                print(f"✅ Creado: {output_path}")
                
            print("🎉 ¡Conversión completada exitosamente!")
            return True
            
        except ImportError:
            print("❌ No se encontraron las librerías necesarias.")
            print("💡 Instalando cairosvg...")
            
            # Instalar cairosvg
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "cairosvg"])
                print("✅ cairosvg instalado. Reintentando conversión...")
                return convert_svg_to_png()  # Reintentar
            except subprocess.CalledProcessError:
                print("❌ Error instalando cairosvg")
                return False

def create_chrome_manifest():
    """Crea el manifest.json específico para Chrome Web Store"""
    
    manifest = {
        "manifest_version": 3,
        "name": "Gemini AI Chatbot",
        "short_name": "GeminiChat",
        "version": "1.0.0",
        "description": "Asistente de IA avanzado con Google Gemini. Chat inteligente, análisis de documentos y más.",
        
        "icons": {
            "16": "static/icons/chrome-webstore-icon-16x16.png",
            "48": "static/icons/chrome-webstore-icon-48x48.png", 
            "128": "static/icons/chrome-webstore-icon-128x128.png",
            "512": "static/icons/chrome-webstore-icon-512x512.png"
        },
        
        "action": {
            "default_popup": "templates/index.html",
            "default_title": "Gemini AI Chatbot",
            "default_icon": {
                "16": "static/icons/chrome-webstore-icon-16x16.png",
                "48": "static/icons/chrome-webstore-icon-48x48.png",
                "128": "static/icons/chrome-webstore-icon-128x128.png"
            }
        },
        
        "background": {
            "service_worker": "static/sw.js"
        },
        
        "permissions": [
            "storage",
            "activeTab"
        ],
        
        "host_permissions": [
            "https://127.0.0.1:5000/*",
            "https://localhost:5000/*"
        ],
        
        "content_security_policy": {
            "extension_pages": "script-src 'self'; object-src 'self'"
        },
        
        "web_accessible_resources": [
            {
                "resources": ["static/*", "templates/*"],
                "matches": ["<all_urls>"]
            }
        ]
    }
    
    # Guardar manifest para Chrome Web Store
    chrome_manifest_path = Path("chrome_extension_manifest.json")
    
    import json
    with open(chrome_manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Manifest para Chrome creado: {chrome_manifest_path}")
    return chrome_manifest_path

def main():
    """Función principal"""
    print("🚀 PREPARACIÓN PARA CHROME WEB STORE")
    print("=" * 50)
    
    # Convertir iconos
    if convert_svg_to_png():
        print("\n✅ Iconos convertidos exitosamente")
    else:
        print("\n❌ Error convirtiendo iconos")
        return False
        
    # Crear manifest para Chrome
    manifest_path = create_chrome_manifest()
    
    print("\n🎯 PRÓXIMOS PASOS:")
    print("1. ✅ Iconos PNG creados")
    print("2. ✅ Manifest para Chrome creado")
    print("3. 📸 Crear screenshots de la aplicación")
    print("4. 📋 Escribir Privacy Policy y Terms of Service")
    print("5. 🏪 Registrar cuenta de desarrollador Chrome ($5)")
    print("6. 📦 Crear package ZIP para subir")
    
    return True

if __name__ == "__main__":
    main()