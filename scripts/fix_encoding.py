#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar y corregir la codificación de archivos de documentación
"""

import glob
import os

import chardet


def detect_encoding(file_path):
    """Detecta la codificación de un archivo"""
    try:
        with open(file_path, "rb") as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            return result["encoding"], result["confidence"]
    except Exception as e:
        print(f"Error detectando codificación de {file_path}: {e}")
        return None, 0


def convert_to_utf8(file_path, original_encoding):
    """Convierte un archivo a UTF-8"""
    try:
        # Leer con la codificación original
        with open(file_path, "r", encoding=original_encoding) as f:
            content = f.read()

        # Escribir en UTF-8
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ Convertido {file_path} de {original_encoding} a UTF-8")
        return True
    except Exception as e:
        print(f"❌ Error convirtiendo {file_path}: {e}")
        return False


def get_files_to_check(patterns):
    files = []
    for pattern in patterns:
        files.extend(glob.glob(pattern))
    return files


def check_and_convert_file(file_path):
    issues = 0
    converted = 0
    encoding, confidence = detect_encoding(file_path)
    if encoding:
        print(f"📄 {file_path}: {encoding} (confianza: {confidence:.2f})")
        if encoding.lower() not in ["utf-8", "ascii"] and confidence > 0.7:
            print(f"⚠️  Archivo {file_path} no está en UTF-8")
            issues += 1
            if convert_to_utf8(file_path, encoding):
                converted += 1
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                problematic_chars = ["�", "\ufffd", "\x00"]
                for char in problematic_chars:
                    if char in content:
                        print(f"⚠️  Encontrados caracteres problemáticos en {file_path}")
                        issues += 1
                        break
        except UnicodeDecodeError:
            print(f"❌ Error de decodificación UTF-8 en {file_path}")
            issues += 1
    return issues, converted


def print_summary(total, issues, converted):
    print("\n📊 Resumen:")
    print(f"   - Archivos verificados: {total}")
    print(f"   - Problemas encontrados: {issues}")
    print(f"   - Archivos convertidos: {converted}")
    if issues == 0:
        print("✅ Todos los archivos tienen codificación correcta")
    else:
        print("⚠️  Se encontraron problemas de codificación")


def main():
    print("🔍 Verificando codificación de archivos de documentación...")
    patterns = ["docs/*.md", "*.md", "chrome_extension/*.html", "chrome_extension/*.md"]
    files_to_check = get_files_to_check(patterns)
    print(f"📁 Encontrados {len(files_to_check)} archivos para verificar")
    issues_found = 0
    files_converted = 0
    for file_path in files_to_check:
        if os.path.isfile(file_path):
            issues, converted = check_and_convert_file(file_path)
            issues_found += issues
            files_converted += converted
    print_summary(len(files_to_check), issues_found, files_converted)


if __name__ == "__main__":
    main()
