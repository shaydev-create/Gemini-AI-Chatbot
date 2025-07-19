#!/usr/bin/env python3
"""
🎨 GENERADOR DE ICONOS FUTURISTAS PARA CHROME
Crea iconos PNG con diseño futurista de IA
"""

from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path

def create_futuristic_icon(size):
    """Crea un icono futurista de IA en el tamaño especificado"""
    
    # Crear imagen con fondo transparente
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Colores futuristas
    bg_color = (15, 15, 35, 255)  # Azul oscuro
    core_color = (0, 212, 255, 255)  # Azul cian brillante
    accent_color = (255, 107, 53, 255)  # Naranja futurista
    white = (255, 255, 255, 255)
    
    # Dibujar fondo circular
    margin = size // 16
    circle_bbox = [margin, margin, size - margin, size - margin]
    draw.ellipse(circle_bbox, fill=bg_color, outline=core_color, width=max(1, size//32))
    
    # Dibujar núcleo central
    center = size // 2
    core_radius = size // 4
    core_bbox = [center - core_radius, center - core_radius, 
                 center + core_radius, center + core_radius]
    draw.ellipse(core_bbox, fill=core_color, outline=white, width=max(1, size//64))
    
    # Dibujar conexiones neuronales (líneas cruzadas)
    line_width = max(1, size//64)
    offset = core_radius // 2
    
    # Líneas principales
    draw.line([center - offset, center - offset, center + offset, center + offset], 
              fill=white, width=line_width)
    draw.line([center + offset, center - offset, center - offset, center + offset], 
              fill=white, width=line_width)
    draw.line([center, center - offset, center, center + offset], 
              fill=white, width=line_width)
    draw.line([center - offset, center, center + offset, center], 
              fill=white, width=line_width)
    
    # Dibujar nodos neuronales
    node_radius = max(1, size//64)
    positions = [
        (center - offset, center - offset),
        (center + offset, center - offset),
        (center - offset, center + offset),
        (center + offset, center + offset),
        (center, center)
    ]
    
    for x, y in positions:
        node_bbox = [x - node_radius, y - node_radius, x + node_radius, y + node_radius]
        draw.ellipse(node_bbox, fill=core_color)
    
    # Dibujar elementos orbitales
    orbit_radius = size // 3
    particle_radius = max(1, size//128)
    
    # Partículas en órbita
    orbital_positions = [
        (center + orbit_radius, center),
        (center - orbit_radius, center),
        (center, center + orbit_radius),
        (center, center - orbit_radius)
    ]
    
    for x, y in orbital_positions:
        particle_bbox = [x - particle_radius, y - particle_radius, 
                        x + particle_radius, y + particle_radius]
        draw.ellipse(particle_bbox, fill=accent_color)
    
    # Dibujar anillos orbitales
    ring_width = max(1, size//128)
    for radius in [orbit_radius - size//16, orbit_radius + size//16]:
        ring_bbox = [center - radius, center - radius, center + radius, center + radius]
        draw.ellipse(ring_bbox, fill=None, outline=core_color, width=ring_width)
    
    return img

def main():
    """Función principal para crear todos los iconos"""
    
    print("🎨 Creando iconos futuristas para Chrome Web Store...")
    
    # Crear directorio de iconos
    icons_dir = Path("static/icons")
    icons_dir.mkdir(exist_ok=True)
    
    # Tamaños requeridos para Chrome Web Store
    sizes = [16, 48, 128, 512]
    
    for size in sizes:
        print(f"📐 Creando icono {size}x{size}...")
        
        # Crear icono
        icon = create_futuristic_icon(size)
        
        # Guardar icono
        filename = f"chrome-webstore-icon-{size}x{size}.png"
        filepath = icons_dir / filename
        icon.save(filepath, "PNG")
        
        print(f"✅ Guardado: {filename}")
    
    # También crear iconos para la extensión
    chrome_dir = Path("chrome_extension/icons")
    chrome_dir.mkdir(exist_ok=True)
    
    for size in [16, 48, 128]:
        icon = create_futuristic_icon(size)
        filename = f"icon_{size}.png"
        filepath = chrome_dir / filename
        icon.save(filepath, "PNG")
        print(f"✅ Icono Chrome: {filename}")
    
    print("🎉 ¡Todos los iconos futuristas creados exitosamente!")

if __name__ == "__main__":
    main()