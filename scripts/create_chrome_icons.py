#!/usr/bin/env python3
"""
🎨 CONVERTIDOR SIMPLE DE ICONOS PARA CHROME WEB STORE
Crea iconos PNG básicos para Chrome Web Store
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def create_chrome_icons():
    """Crea iconos PNG para Chrome Web Store"""

    icons_dir = Path("static/icons")
    icons_dir.mkdir(exist_ok=True)

    # Tamaños requeridos para Chrome Web Store
    sizes = [16, 48, 128, 512]

    # Colores del tema
    bg_color = "#1a1a2e"
    accent_color = "#00d4ff"
    text_color = "#ffffff"

    print("🎨 Creando iconos PNG para Chrome Web Store...")

    for size in sizes:
        # Crear imagen
        img = Image.new("RGBA", (size, size), bg_color)
        draw = ImageDraw.Draw(img)

        # Dibujar círculo de fondo
        margin = size // 8
        circle_bbox = [margin, margin, size - margin, size - margin]
        draw.ellipse(
            circle_bbox, fill=accent_color, outline=text_color, width=max(1, size // 64)
        )

        # Dibujar letra "G" en el centro
        try:
            # Intentar usar una fuente del sistema
            font_size = size // 2
            font = ImageFont.truetype("arial.ttf", font_size)
        except BaseException:
            # Usar fuente por defecto si no encuentra arial
            font = ImageFont.load_default()

        # Calcular posición del texto
        text = "G"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (size - text_width) // 2
        y = (size - text_height) // 2 - size // 16  # Ajuste vertical

        # Dibujar texto
        draw.text((x, y), text, fill=text_color, font=font)

        # Guardar imagen
        filename = f"chrome-webstore-icon-{size}x{size}.png"
        filepath = icons_dir / filename
        img.save(filepath, "PNG")

        print(f"✅ Creado: {filename}")

    print("🎉 ¡Iconos PNG creados exitosamente!")
    return True


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
            "512": "static/icons/chrome-webstore-icon-512x512.png",
        },
        "action": {
            "default_popup": "index.html",
            "default_title": "Gemini AI Chatbot",
            "default_icon": {
                "16": "static/icons/chrome-webstore-icon-16x16.png",
                "48": "static/icons/chrome-webstore-icon-48x48.png",
                "128": "static/icons/chrome-webstore-icon-128x128.png",
            },
        },
        "background": {"service_worker": "static/sw.js"},
        "permissions": ["storage", "activeTab", "scripting"],
        "host_permissions": [
            "https://127.0.0.1:5000/*",
            "https://localhost:5000/*",
            "https://*.gemini-ai.com/*",
        ],
        "content_security_policy": {
            "extension_pages": "script-src 'self'; object-src 'self'; style-src 'self' 'unsafe-inline'"
        },
        "web_accessible_resources": [
            {
                "resources": ["static/*", "templates/*", "*.html", "*.css", "*.js"],
                "matches": ["<all_urls>"],
            }
        ],
    }

    # Guardar manifest para Chrome Web Store
    chrome_manifest_path = Path("chrome_extension_manifest.json")

    import json

    with open(chrome_manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"✅ Manifest para Chrome creado: {chrome_manifest_path}")
    return chrome_manifest_path


def create_popup_html():
    """Crea un archivo HTML simple para el popup de la extensión"""

    popup_html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gemini AI Chatbot</title>
    <style>
        body {
            width: 350px;
            height: 500px;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #ffffff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        .header {
            text-align: center;
            margin-bottom: 20px;
        }

        .logo {
            width: 64px;
            height: 64px;
            margin: 0 auto 10px;
            background: linear-gradient(135deg, #00d4ff, #0099cc);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            font-weight: bold;
        }

        h1 {
            margin: 0;
            font-size: 18px;
            color: #00d4ff;
        }

        .description {
            text-align: center;
            margin-bottom: 20px;
            font-size: 14px;
            opacity: 0.8;
        }

        .button {
            display: block;
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            background: linear-gradient(135deg, #00d4ff, #0099cc);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
            transition: transform 0.2s;
        }

        .button:hover {
            transform: translateY(-2px);
        }

        .features {
            margin-top: 20px;
        }

        .feature {
            display: flex;
            align-items: center;
            margin: 8px 0;
            font-size: 12px;
        }

        .feature-icon {
            margin-right: 8px;
            font-size: 16px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">G</div>
        <h1>Gemini AI Chatbot</h1>
    </div>

    <div class="description">
        Asistente de IA avanzado con Google Gemini
    </div>

    <a href="https://127.0.0.1:5000" target="_blank" class="button">
        🚀 Abrir Aplicación
    </a>

    <a href="https://127.0.0.1:5000/auth/login" target="_blank" class="button">
        🔐 Iniciar Sesión
    </a>

    <div class="features">
        <div class="feature">
            <span class="feature-icon">🤖</span>
            Chat inteligente con IA
        </div>
        <div class="feature">
            <span class="feature-icon">📄</span>
            Análisis de documentos
        </div>
        <div class="feature">
            <span class="feature-icon">🎵</span>
            Transcripción de audio
        </div>
        <div class="feature">
            <span class="feature-icon">🔒</span>
            Seguro y privado
        </div>
    </div>

    <script>
        // Abrir enlaces en nueva pestaña
        document.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                chrome.tabs.create({ url: link.href });
            });
        });
    </script>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(popup_html)

    print("✅ Archivo popup HTML creado: index.html")


def main():
    """Función principal"""
    print("🚀 PREPARACIÓN PARA CHROME WEB STORE")
    print("=" * 50)

    # Crear iconos PNG
    if create_chrome_icons():
        print("\n✅ Iconos PNG creados exitosamente")
    else:
        print("\n❌ Error creando iconos")
        return False

    # Crear manifest para Chrome
    create_chrome_manifest()

    # Crear popup HTML
    create_popup_html()

    print("\n🎯 ARCHIVOS CREADOS:")
    print("✅ Iconos PNG (16x16, 48x48, 128x128, 512x512)")
    print("✅ chrome_extension_manifest.json")
    print("✅ index.html (popup)")

    print("\n📋 PRÓXIMOS PASOS:")
    print("1. 📸 Crear screenshots de la aplicación")
    print("2. 📋 Escribir Privacy Policy y Terms of Service")
    print("3. 🏪 Registrar cuenta de desarrollador Chrome ($5)")
    print("4. 📦 Crear package ZIP para subir")

    return True


if __name__ == "__main__":
    main()
