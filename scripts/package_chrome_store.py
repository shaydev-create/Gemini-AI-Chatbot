#!/usr/bin/env python3
"""
📦 EMPAQUETADOR PARA CHROME WEB STORE
Crea el package ZIP final listo para subir a Chrome Web Store
"""

import os
import zipfile
import json
import shutil
from pathlib import Path
from datetime import datetime

def create_chrome_package():
    """Crea el package completo para Chrome Web Store"""
    
    print("📦 CREANDO PACKAGE PARA CHROME WEB STORE")
    print("=" * 50)
    
    # Directorio temporal para el package
    package_dir = Path("chrome_package")
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    # Archivos necesarios para Chrome Web Store
    files_to_include = [
        # Manifest
        ("chrome_extension_manifest.json", "manifest.json"),
        
        # HTML principal
        ("index.html", "index.html"),
        
        # Iconos PNG
        ("static/icons/chrome-webstore-icon-16x16.png", "icons/icon-16.png"),
        ("static/icons/chrome-webstore-icon-48x48.png", "icons/icon-48.png"),
        ("static/icons/chrome-webstore-icon-128x128.png", "icons/icon-128.png"),
        ("static/icons/chrome-webstore-icon-512x512.png", "icons/icon-512.png"),
        
        # Service Worker
        ("static/sw.js", "sw.js"),
        
        # CSS y JS esenciales
        ("static/css/style.css", "css/style.css"),
        ("static/js/app.js", "js/app.js"),
        
        # Documentos legales
        ("templates/privacy_policy.html", "privacy_policy.html"),
        ("templates/terms_of_service.html", "terms_of_service.html"),
    ]
    
    print("📁 Copiando archivos...")
    
    for source, destination in files_to_include:
        source_path = Path(source)
        dest_path = package_dir / destination
        
        # Crear directorio de destino si no existe
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        if source_path.exists():
            shutil.copy2(source_path, dest_path)
            print(f"✅ {source} → {destination}")
        else:
            print(f"⚠️ No encontrado: {source}")
    
    # Crear archivos adicionales necesarios
    create_background_script(package_dir)
    create_content_script(package_dir)
    create_popup_css(package_dir)
    
    # Crear ZIP final
    zip_filename = f"gemini-ai-chatbot-chrome-{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    
    print(f"\n📦 Creando archivo ZIP: {zip_filename}")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = Path(root) / file
                arc_name = file_path.relative_to(package_dir)
                zipf.write(file_path, arc_name)
                print(f"📄 Agregado: {arc_name}")
    
    # Limpiar directorio temporal
    shutil.rmtree(package_dir)
    
    print(f"\n🎉 ¡Package creado exitosamente!")
    print(f"📦 Archivo: {zip_filename}")
    print(f"📏 Tamaño: {os.path.getsize(zip_filename) / 1024:.1f} KB")
    
    return zip_filename

def create_background_script(package_dir):
    """Crea script de background para la extensión"""
    
    background_js = """
// Background script para Gemini AI Chatbot Chrome Extension

// Configuración
const CONFIG = {
    APP_URL: 'https://127.0.0.1:5000',
    FALLBACK_URL: 'https://localhost:5000',
    EXTENSION_NAME: 'Gemini AI Chatbot'
};

// Instalación de la extensión
chrome.runtime.onInstalled.addListener((details) => {
    console.log('Gemini AI Chatbot instalado:', details.reason);
    
    if (details.reason === 'install') {
        // Primera instalación
        chrome.tabs.create({
            url: CONFIG.APP_URL
        });
    }
});

// Click en el icono de la extensión
chrome.action.onClicked.addListener((tab) => {
    // Abrir la aplicación en nueva pestaña
    chrome.tabs.create({
        url: CONFIG.APP_URL
    });
});

// Manejo de mensajes
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'openApp') {
        chrome.tabs.create({
            url: CONFIG.APP_URL
        });
        sendResponse({success: true});
    }
    
    if (request.action === 'getConfig') {
        sendResponse(CONFIG);
    }
});

// Notificaciones (opcional)
function showNotification(title, message) {
    chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icons/icon-48.png',
        title: title,
        message: message
    });
}

// Manejo de errores
chrome.runtime.onSuspend.addListener(() => {
    console.log('Gemini AI Chatbot suspendido');
});
"""
    
    bg_path = package_dir / "background.js"
    with open(bg_path, 'w', encoding='utf-8') as f:
        f.write(background_js)
    
    print("✅ Background script creado")

def create_content_script(package_dir):
    """Crea content script para la extensión"""
    
    content_js = """
// Content script para Gemini AI Chatbot Chrome Extension

// Detectar si estamos en la página de la aplicación
if (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost') {
    console.log('Gemini AI Chatbot detectado');
    
    // Mejorar la experiencia en la aplicación
    document.addEventListener('DOMContentLoaded', () => {
        // Agregar clase para identificar que se ejecuta como extensión
        document.body.classList.add('chrome-extension-mode');
        
        // Opcional: Agregar funcionalidades específicas de la extensión
        addExtensionFeatures();
    });
}

function addExtensionFeatures() {
    // Agregar botón de "Abrir en nueva ventana" si es necesario
    const header = document.querySelector('header, .header, nav');
    if (header) {
        const extensionBadge = document.createElement('div');
        extensionBadge.innerHTML = '🔌 Extensión Chrome';
        extensionBadge.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            background: #00d4ff;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 12px;
            z-index: 10000;
            font-family: Arial, sans-serif;
        `;
        document.body.appendChild(extensionBadge);
        
        // Auto-ocultar después de 3 segundos
        setTimeout(() => {
            extensionBadge.style.opacity = '0';
            extensionBadge.style.transition = 'opacity 0.5s';
        }, 3000);
    }
}

// Comunicación con background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'ping') {
        sendResponse({status: 'active'});
    }
});
"""
    
    content_path = package_dir / "content.js"
    with open(content_path, 'w', encoding='utf-8') as f:
        f.write(content_js)
    
    print("✅ Content script creado")

def create_popup_css(package_dir):
    """Crea CSS para el popup"""
    
    popup_css = """
/* CSS para el popup de Gemini AI Chatbot Chrome Extension */

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    width: 350px;
    min-height: 500px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    color: #ffffff;
    overflow-x: hidden;
}

.header {
    text-align: center;
    padding: 20px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo {
    width: 64px;
    height: 64px;
    margin: 0 auto 15px;
    background: linear-gradient(135deg, #00d4ff, #0099cc);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32px;
    font-weight: bold;
    box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
}

h1 {
    font-size: 18px;
    color: #00d4ff;
    margin-bottom: 5px;
}

.subtitle {
    font-size: 12px;
    opacity: 0.7;
}

.content {
    padding: 20px;
}

.description {
    text-align: center;
    margin-bottom: 20px;
    font-size: 14px;
    opacity: 0.8;
    line-height: 1.4;
}

.button {
    display: block;
    width: 100%;
    padding: 12px 15px;
    margin: 10px 0;
    background: linear-gradient(135deg, #00d4ff, #0099cc);
    color: white;
    text-decoration: none;
    border-radius: 8px;
    text-align: center;
    font-weight: 600;
    font-size: 14px;
    transition: all 0.3s ease;
    border: none;
    cursor: pointer;
}

.button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0, 212, 255, 0.4);
}

.button.secondary {
    background: linear-gradient(135deg, #4a5568, #2d3748);
}

.button.secondary:hover {
    box-shadow: 0 4px 15px rgba(74, 85, 104, 0.4);
}

.features {
    margin-top: 25px;
    padding-top: 20px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.features h3 {
    font-size: 14px;
    margin-bottom: 15px;
    color: #00d4ff;
    text-align: center;
}

.feature {
    display: flex;
    align-items: center;
    margin: 10px 0;
    font-size: 12px;
    padding: 8px 0;
}

.feature-icon {
    margin-right: 10px;
    font-size: 16px;
    width: 20px;
    text-align: center;
}

.footer {
    padding: 15px 20px;
    text-align: center;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    margin-top: 20px;
}

.footer a {
    color: #00d4ff;
    text-decoration: none;
    font-size: 11px;
    margin: 0 5px;
}

.footer a:hover {
    text-decoration: underline;
}

/* Animaciones */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.content > * {
    animation: fadeIn 0.3s ease-out;
}

/* Scrollbar personalizado */
::-webkit-scrollbar {
    width: 6px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
}

::-webkit-scrollbar-thumb {
    background: #00d4ff;
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: #0099cc;
}
"""
    
    css_dir = package_dir / "css"
    css_dir.mkdir(exist_ok=True)
    
    css_path = css_dir / "popup.css"
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(popup_css)
    
    print("✅ Popup CSS creado")

def show_submission_guide():
    """Muestra la guía para subir a Chrome Web Store"""
    
    print("\n" + "="*60)
    print("🚀 GUÍA PARA SUBIR A CHROME WEB STORE")
    print("="*60)
    
    print("\n📋 PASOS PARA PUBLICAR:")
    print("1. 🌐 Ir a: https://chrome.google.com/webstore/devconsole/")
    print("2. 💳 Pagar $5 USD (registro de desarrollador)")
    print("3. 📤 Subir el archivo ZIP creado")
    print("4. 📝 Completar información de la tienda:")
    
    print("\n   📊 INFORMACIÓN REQUERIDA:")
    print("   • Nombre: Gemini AI Chatbot")
    print("   • Descripción corta: Asistente de IA avanzado con Google Gemini")
    print("   • Descripción detallada: [Ver archivo de descripción]")
    print("   • Categoría: Productivity")
    print("   • Idioma: Spanish")
    
    print("\n   🖼️ IMÁGENES REQUERIDAS:")
    print("   • Screenshots: 1280x800 (mínimo 1, máximo 5)")
    print("   • Icono de la tienda: 128x128 (ya incluido)")
    print("   • Tile promocional: 440x280 (opcional)")
    
    print("\n   📋 DOCUMENTOS LEGALES:")
    print("   • Privacy Policy: ✅ Creada (privacy_policy.html)")
    print("   • Terms of Service: ✅ Creados (terms_of_service.html)")
    
    print("\n⏱️ TIEMPO DE REVISIÓN:")
    print("• Revisión automática: 1-3 días")
    print("• Publicación: Inmediata tras aprobación")
    
    print("\n💡 CONSEJOS:")
    print("• Usa keywords relevantes en la descripción")
    print("• Agrega screenshots atractivos")
    print("• Responde rápidamente a comentarios de revisión")
    print("• Mantén la extensión actualizada")

def main():
    """Función principal"""
    
    # Crear package
    zip_file = create_chrome_package()
    
    # Mostrar guía
    show_submission_guide()
    
    print(f"\n🎯 ARCHIVO LISTO PARA SUBIR:")
    print(f"📦 {zip_file}")
    print(f"📏 Tamaño: {os.path.getsize(zip_file) / 1024:.1f} KB")
    
    print(f"\n✅ TODO LISTO PARA CHROME WEB STORE!")
    
    return zip_file

if __name__ == "__main__":
    main()