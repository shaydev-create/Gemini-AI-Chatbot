#!/usr/bin/env python3
"""
Script específico para corregir anotaciones de tipo incorrectas en SecurityEvent.
"""

import re
from pathlib import Path

def fix_security_events():
    """Corrige anotaciones de tipo en SecurityEvent constructors."""
    file_path = Path(__file__).parent.parent / "app" / "core" / "security.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Corregir event_type: str = "valor"
    content = re.sub(r'event_type:\s*str\s*=\s*', 'event_type=', content)
    
    # Corregir severity: str = "valor"
    content = re.sub(r'severity:\s*str\s*=\s*', 'severity=', content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Corregido: {file_path}")
        return True
    return False

if __name__ == "__main__":
    if fix_security_events():
        print("✨ SecurityEvent constructors corregidos.")
    else:
        print("ℹ️ No se encontraron cambios necesarios.")