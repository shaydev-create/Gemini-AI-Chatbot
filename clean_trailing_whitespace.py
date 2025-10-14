#!/usr/bin/env python3
"""Script para limpiar espacios en blanco al final de las líneas."""

import sys


def clean_trailing_whitespace(file_path):
    """Limpiar espacios en blanco al final de las líneas en un archivo.

    Args:
        file_path: Ruta al archivo a limpiar
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Limpiar espacios en blanco al final de cada línea
        cleaned_lines = [line.rstrip() + '\n' for line in lines]

        # Escribir el archivo limpio
        with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
            f.writelines(cleaned_lines)

        print(f"✅ Espacios en blanco limpiados en: {file_path}")
        return True

    except Exception as e:
        print(f"❌ Error limpiando {file_path}: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python clean_trailing_whitespace.py <archivo>")
        sys.exit(1)

    file_path = sys.argv[1]
    clean_trailing_whitespace(file_path)
