#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar y corregir la codificación de archivos de documentación
"""

import os
import chardet
import glob


def detect_encoding(file_path):
    """Detecta la codificación de un archivo"""
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            return result['encoding'], result['confidence']
    except Exception as e:
        print(f"Error detectando codificación de {file_path}: {e}")
        return None, 0


def convert_to_utf8(file_path, original_encoding):
    """Convierte un archivo a UTF-8"""
    try:
        # Leer con la codificación original
        with open(file_path, 'r', encoding=original_encoding) as f:
            content = f.read()

        # Escribir en UTF-8
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✅ Convertido {file_path} de {original_encoding} a UTF-8")
        return True
    except Exception as e:
        print(f"❌ Error convirtiendo {file_path}: {e}")
        return False


def main():
    """Función principal"""
    print("🔍 Verificando codificación de archivos de documentación...")

    # Patrones de archivos a verificar
    patterns = [
        "docs/*.md",
        "*.md",
        "chrome_extension/*.html",
        "chrome_extension/*.md"
    ]

    files_to_check = []
    for pattern in patterns:
        files_to_check.extend(glob.glob(pattern))

    print(f"📁 Encontrados {len(files_to_check)} archivos para verificar")

    issues_found = 0
    files_converted = 0

    for file_path in files_to_check:
        if os.path.isfile(file_path):
            encoding, confidence = detect_encoding(file_path)

            if encoding:
                print(
                    f"📄 {file_path}: {encoding} (confianza: {
                        confidence:.2f})")

                # Si no es UTF-8 y tiene alta confianza, convertir
                if encoding.lower() not in [
                        'utf-8', 'ascii'] and confidence > 0.7:
                    print(f"⚠️  Archivo {file_path} no está en UTF-8")
                    issues_found += 1

                    if convert_to_utf8(file_path, encoding):
                        files_converted += 1

                # Verificar si hay caracteres problemáticos
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Buscar caracteres problemáticos comunes
                        problematic_chars = ['�', '\ufffd', '\x00']
                        for char in problematic_chars:
                            if char in content:
                                print(
                                    f"⚠️  Encontrados caracteres problemáticos en {file_path}")
                                issues_found += 1
                                break
                except UnicodeDecodeError:
                    print(f"❌ Error de decodificación UTF-8 en {file_path}")
                    issues_found += 1

    print("\n📊 Resumen:")
    print(f"   - Archivos verificados: {len(files_to_check)}")
    print(f"   - Problemas encontrados: {issues_found}")
    print(f"   - Archivos convertidos: {files_converted}")

    if issues_found == 0:
        print("✅ Todos los archivos tienen codificación correcta")
    else:
        print("⚠️  Se encontraron problemas de codificación")


if __name__ == "__main__":
    main()
