#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear iconos PNG desde SVG para la aplicación
"""

import base64
from PIL import Image, ImageDraw
import io

def create_icon_png(size=128):
    """Crea un icono PNG programáticamente"""
    # Crear imagen con fondo transparente
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Colores del gradiente
    center = size // 2
    radius = size // 2 - 4
    
    # Crear círculo de fondo con gradiente simulado
    for i in range(radius):
        alpha = int(255 * (1 - i / radius))
        # Colores del gradiente: azul a púrpura a rosa
        if i < radius // 3:
            color = (102, 126, 234, alpha)  # Azul
        elif i < 2 * radius // 3:
            color = (118, 75, 162, alpha)  # Púrpura
        else:
            color = (240, 147, 251, alpha)  # Rosa
        
        draw.ellipse([center - radius + i, center - radius + i, 
                     center + radius - i, center + radius - i], 
                    fill=color)
    
    # Dibujar burbuja de chat
    chat_left = size // 4
    chat_top = size // 3
    chat_right = 3 * size // 4
    chat_bottom = 2 * size // 3
    
    # Burbuja principal
    draw.rounded_rectangle([chat_left, chat_top, chat_right, chat_bottom], 
                          radius=8, fill=(255, 255, 255, 200))
    
    # Cola de la burbuja
    tail_points = [
        (chat_left + 8, chat_bottom),
        (chat_left, chat_bottom + 12),
        (chat_left + 16, chat_bottom)
    ]
    draw.polygon(tail_points, fill=(255, 255, 255, 200))
    
    # Estrella central (símbolo de Gemini)
    star_center_x = center
    star_center_y = center - 8
    star_size = 8
    
    # Puntos de la estrella
    star_points = []
    for i in range(10):  # 5 puntas, 2 puntos por punta
        angle = i * 36  # 360 / 10
        if i % 2 == 0:
            # Puntas externas
            x = star_center_x + star_size * 1.2 * (1 if angle == 0 else 
                0.951 if angle == 36 else 0.309 if angle == 72 else 
                -0.309 if angle == 108 else -0.951 if angle == 144 else
                -1 if angle == 180 else -0.951 if angle == 216 else
                -0.309 if angle == 252 else 0.309 if angle == 288 else 0.951)
            y = star_center_y + star_size * 1.2 * (0 if angle == 0 else 
                0.309 if angle == 36 else 0.951 if angle == 72 else 
                0.951 if angle == 108 else 0.309 if angle == 144 else
                0 if angle == 180 else -0.309 if angle == 216 else
                -0.951 if angle == 252 else -0.951 if angle == 288 else -0.309)
        else:
            # Puntas internas
            x = star_center_x + star_size * 0.5 * (0.809 if angle == 18 else 
                0.809 if angle == 54 else 0 if angle == 90 else 
                -0.809 if angle == 126 else -0.809 if angle == 162 else
                -0.809 if angle == 198 else -0.809 if angle == 234 else
                0 if angle == 270 else 0.809 if angle == 306 else 0.809)
            y = star_center_y + star_size * 0.5 * (0.588 if angle == 18 else 
                0.588 if angle == 54 else 1 if angle == 90 else 
                0.588 if angle == 126 else -0.588 if angle == 162 else
                -0.588 if angle == 198 else -0.588 if angle == 234 else
                -1 if angle == 270 else -0.588 if angle == 306 else 0.588)
        
        star_points.append((int(x), int(y)))
    
    # Dibujar estrella simplificada
    draw.ellipse([star_center_x - 6, star_center_y - 6, 
                 star_center_x + 6, star_center_y + 6], 
                fill=(255, 255, 255, 255))
    
    # Puntos decorativos
    draw.ellipse([center - 20, center - 5, center - 16, center - 1], 
                fill=(255, 255, 255, 180))
    draw.ellipse([center + 16, center - 8, center + 20, center - 4], 
                fill=(255, 255, 255, 180))
    draw.ellipse([center + 8, center + 12, center + 12, center + 16], 
                fill=(255, 255, 255, 180))
    
    return img

def save_icon():
    """Guarda el icono en formato PNG"""
    try:
        icon = create_icon_png(128)
        icon.save('static/images/icon.png', 'PNG')
        print("✅ Icono PNG creado exitosamente: static/images/icon.png")
        
        # Crear también versiones más pequeñas
        for size in [16, 32, 48, 64]:
            small_icon = create_icon_png(size)
            small_icon.save(f'static/images/icon_{size}.png', 'PNG')
            print(f"✅ Icono {size}x{size} creado: static/images/icon_{size}.png")
            
    except Exception as e:
        print(f"❌ Error al crear icono: {str(e)}")
        print("Instalando Pillow...")
        import subprocess
        subprocess.run(['pip', 'install', 'Pillow'], check=True)
        
        # Intentar de nuevo
        icon = create_icon_png(128)
        icon.save('static/images/icon.png', 'PNG')
        print("✅ Icono PNG creado exitosamente: static/images/icon.png")

if __name__ == "__main__":
    save_icon()