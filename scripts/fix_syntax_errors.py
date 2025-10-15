#!/usr/bin/env python3
"""
Script para corregir errores de sintaxis causados por anotaciones de tipo incorrectas
en argumentos de función.
"""

import os
import re
from pathlib import Path


def fix_syntax_errors(file_path: Path):
    """Corrige errores de sintaxis en un archivo."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Patrón para encontrar argumentos con anotaciones incorrectas
    # Busca: nombre: Any = valor, (incluyendo casos multi-línea)
    pattern = r"(\w+):\s*Any\s*=\s*([^,\)]+)([,\)])"

    def replace_func(match):
        var_name = match.group(1)
        value = match.group(2)
        ending = match.group(3)
        return f"{var_name}={value}{ending}"

    # Aplicar el patrón con flag DOTALL para capturar multi-línea
    content = re.sub(pattern, replace_func, content, flags=re.DOTALL)

    # Patrón adicional para casos específicos de multi-línea
    multiline_pattern = r"(\s+)(\w+):\s*Any\s*=\s*([^,\n]+),?\n"

    def multiline_replace_func(match):
        indent = match.group(1)
        var_name = match.group(2)
        value = match.group(3)
        return f"{indent}{var_name}={value},\n"

    content = re.sub(multiline_pattern, multiline_replace_func, content)

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Corregido: {file_path}")
        return True
    return False


def main():
    """Procesa todos los archivos Python en el directorio app/."""
    app_dir = Path(__file__).parent.parent / "app"
    fixed_count = 0

    for root, _, files in os.walk(app_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                if fix_syntax_errors(file_path):
                    fixed_count += 1

    print(f"\n✨ Corrección completada. {fixed_count} archivos corregidos.")


if __name__ == "__main__":
    main()
