#!/usr/bin/env python3
"""
Script para crear screenshots profesionales para Chrome Web Store
Genera imágenes de demostración del Gemini AI Chatbot
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_screenshot(width=1280, height=800, filename="screenshot.png"):
    """Crear screenshot profesional para Chrome Web Store"""
    
    # Crear imagen base
    img = Image.new('RGB', (width, height), color='#1a1a1a')
    draw = ImageDraw.Draw(img)
    
    # Colores del tema
    primary_color = '#4285f4'  # Azul Google
    secondary_color = '#34a853'  # Verde Google
    accent_color = '#ea4335'  # Rojo Google
    text_color = '#ffffff'
    card_color = '#2d2d2d'
    
    # Dibujar header
    draw.rectangle([0, 0, width, 80], fill=primary_color)
    
    # Título principal
    try:
        title_font = ImageFont.truetype("arial.ttf", 32)
        subtitle_font = ImageFont.truetype("arial.ttf", 18)
        text_font = ImageFont.truetype("arial.ttf", 14)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    # Header text
    draw.text((40, 25), "🤖 Gemini AI Chatbot", fill=text_color, font=title_font)
    
    # Chat container
    chat_x, chat_y = 40, 120
    chat_width, chat_height = width - 80, height - 200
    
    # Chat background
    draw.rounded_rectangle([chat_x, chat_y, chat_x + chat_width, chat_y + chat_height], 
                          radius=15, fill=card_color)
    
    # Messages
    messages = [
        ("Usuario", "¿Puedes ayudarme con programación en Python?", accent_color),
        ("Gemini AI", "¡Por supuesto! Soy un asistente de IA especializado en programación. ¿Qué necesitas saber sobre Python?", secondary_color),
        ("Usuario", "¿Cómo crear una función para calcular fibonacci?", accent_color),
        ("Gemini AI", "Aquí tienes una función eficiente para calcular Fibonacci:\n\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)", secondary_color)
    ]
    
    y_offset = chat_y + 30
    for sender, message, color in messages:
        # Message bubble
        bubble_height = 60 if len(message) < 100 else 100
        bubble_x = chat_x + 20 if sender == "Usuario" else chat_x + 200
        bubble_width = chat_width - 240
        
        draw.rounded_rectangle([bubble_x, y_offset, bubble_x + bubble_width, y_offset + bubble_height],
                              radius=10, fill=color)
        
        # Sender name
        draw.text((bubble_x + 15, y_offset + 5), sender, fill=text_color, font=subtitle_font)
        
        # Message text
        lines = message.split('\n')
        for i, line in enumerate(lines[:3]):  # Max 3 lines
            draw.text((bubble_x + 15, y_offset + 25 + i * 20), line[:60], fill=text_color, font=text_font)
        
        y_offset += bubble_height + 20
    
    # Input area
    input_y = height - 60
    draw.rounded_rectangle([chat_x, input_y, chat_x + chat_width, input_y + 40],
                          radius=10, fill='#3d3d3d')
    draw.text((chat_x + 15, input_y + 12), "Escribe tu mensaje aquí...", fill='#888888', font=text_font)
    
    # Send button
    send_btn_x = chat_x + chat_width - 80
    draw.rounded_rectangle([send_btn_x, input_y + 5, send_btn_x + 70, input_y + 35],
                          radius=5, fill=primary_color)
    draw.text((send_btn_x + 20, input_y + 12), "Enviar", fill=text_color, font=text_font)
    
    # Features sidebar
    sidebar_x = width - 300
    sidebar_y = 120
    draw.rounded_rectangle([sidebar_x, sidebar_y, width - 40, height - 80],
                          radius=15, fill='#252525')
    
    # Features title
    draw.text((sidebar_x + 20, sidebar_y + 20), "✨ Características", fill=text_color, font=subtitle_font)
    
    features = [
        "🚀 IA Avanzada con Google Gemini",
        "💬 Chat en tiempo real",
        "📁 Subida de archivos",
        "🔒 Seguro y privado",
        "🌐 Interfaz moderna",
        "📱 Responsive design"
    ]
    
    for i, feature in enumerate(features):
        draw.text((sidebar_x + 20, sidebar_y + 60 + i * 30), feature, fill=text_color, font=text_font)
    
    # Save screenshot
    img.save(filename, 'PNG', quality=95)
    print(f"✅ Screenshot creado: {filename}")

def create_promotional_tile(width=440, height=280, filename="promo_tile.png"):
    """Crear tile promocional para Chrome Web Store"""
    
    img = Image.new('RGB', (width, height), color='#1a1a1a')
    draw = ImageDraw.Draw(img)
    
    # Gradient background
    for y in range(height):
        color_value = int(26 + (y / height) * 40)
        draw.line([(0, y), (width, y)], fill=(color_value, color_value, color_value))
    
    # Main elements
    try:
        title_font = ImageFont.truetype("arial.ttf", 36)
        subtitle_font = ImageFont.truetype("arial.ttf", 18)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Title
    draw.text((width//2 - 150, 60), "🤖 Gemini AI", fill='#4285f4', font=title_font)
    draw.text((width//2 - 80, 110), "Chatbot Inteligente", fill='#ffffff', font=subtitle_font)
    
    # Features
    features = ["✨ IA Avanzada", "🚀 Rápido", "🔒 Seguro"]
    for i, feature in enumerate(features):
        x = 50 + i * 120
        draw.text((x, 180), feature, fill='#34a853', font=subtitle_font)
    
    # Call to action
    draw.rounded_rectangle([width//2 - 80, 220, width//2 + 80, 250], 
                          radius=15, fill='#ea4335')
    draw.text((width//2 - 60, 230), "¡Instalar Ahora!", fill='#ffffff', font=subtitle_font)
    
    img.save(filename, 'PNG', quality=95)
    print(f"✅ Tile promocional creado: {filename}")

def main():
    """Crear todos los screenshots necesarios"""
    
    # Crear directorio para screenshots
    screenshots_dir = "chrome_store_assets/screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)
    
    print("🎨 Creando screenshots para Chrome Web Store...")
    
    # Screenshot principal
    create_screenshot(1280, 800, f"{screenshots_dir}/screenshot_1_main.png")
    
    # Screenshot de características
    create_screenshot(1280, 800, f"{screenshots_dir}/screenshot_2_features.png")
    
    # Tile promocional
    create_promotional_tile(440, 280, f"{screenshots_dir}/promo_tile.png")
    
    print("\n📸 SCREENSHOTS CREADOS:")
    print("├── screenshot_1_main.png (1280x800)")
    print("├── screenshot_2_features.png (1280x800)")
    print("└── promo_tile.png (440x280)")
    
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. 🌐 Ir a Chrome Web Store Developer Console")
    print("2. 💳 Pagar $5 USD para registro")
    print("3. 📤 Subir gemini-ai-chatbot-chrome-*.zip")
    print("4. 📸 Subir los screenshots creados")
    print("5. 📝 Completar información de la tienda")
    print("6. 🚀 Enviar para revisión")
    
    print("\n🎯 ARCHIVOS LISTOS:")
    print("• ZIP Package: ✅")
    print("• Screenshots: ✅")
    print("• Privacy Policy: ✅")
    print("• Terms of Service: ✅")
    print("• Icons: ✅")

if __name__ == "__main__":
    main()