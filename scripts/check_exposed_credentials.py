#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 DETECTOR DE CREDENCIALES EXPUESTAS - GEMINI AI CHATBOT

Este script analiza el historial de Git para detectar posibles credenciales expuestas.
Úsalo para verificar si hay información sensible que necesita ser limpiada.
"""

import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Patrones de credenciales a buscar
PATTERNS = {
    "API Key de Google/Gemini": [
        r'GOOGLE_API_KEY\s*=\s*["\']([^"\'\s]{35,})["\']',
        r'GEMINI_API_KEY\s*=\s*["\']([^"\'\s]{35,})["\']',
        r"AIza[0-9A-Za-z\-_]{35,}",
    ],
    "Claves secretas": [
        r'SECRET_KEY\s*=\s*["\']([^"\'\s]{16,})["\']',
        r'JWT_SECRET_KEY\s*=\s*["\']([^"\'\s]{16,})["\']',
    ],
    "Credenciales de email": [r'MAIL_PASSWORD\s*=\s*["\']([^"\'\s]{8,})["\']'],
    "Claves PWA": [r'VAPID_PRIVATE_KEY\s*=\s*["\']([^"\'\s]{20,})["\']'],
}


def print_banner():
    """Mostrar banner del script"""
    print("🔍 DETECTOR DE CREDENCIALES EXPUESTAS - GEMINI AI CHATBOT")
    print("=" * 70)
    print()


def run_command(command):
    """Ejecutar comando y devolver salida"""
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,
        )
        return result.stdout
    except Exception as e:
        print(f"❌ Error al ejecutar comando: {e}")
        return ""


def _is_git_repository() -> bool:
    """Verificar si estamos en un repositorio Git."""
    if not os.path.exists(".git"):
        print("❌ No se encontró un repositorio Git en este directorio")
        return False
    return True


def _get_commits_list() -> List[str]:
    """Obtener lista de commits del repositorio."""
    commits_output = run_command("git log --format=%H").strip()
    commits = commits_output.split("\n") if commits_output else []

    if not commits or commits[0] == "":
        print("❌ No se encontraron commits en el repositorio")
        return []

    return commits


def _get_commit_metadata(commit_hash: str) -> Optional[Dict[str, str]]:
    """Obtener metadatos de un commit específico."""
    commit_info = run_command(
        f"git show --name-only --format='%h|%an|%ad|%s' {commit_hash} --date=short"
    )

    if not commit_info:
        return None

    lines = commit_info.split("\n")
    if not lines:
        return None

    try:
        commit_meta = lines[0].split("|")
        return {
            "short_hash": commit_meta[0],
            "author": commit_meta[1],
            "date": commit_meta[2],
            "subject": commit_meta[3],
        }
    except (IndexError, ValueError):
        return None


def _analyze_commit_for_credentials(
    commit_hash: str, metadata: Dict[str, str]
) -> List[str]:
    """Analizar un commit específico en busca de credenciales."""
    commit_content = run_command(f"git show {commit_hash}")
    report_lines = []

    for cred_type, patterns in PATTERNS.items():
        for pattern in patterns:
            matches = re.findall(pattern, commit_content)
            if matches:
                # Ocultar parte de la credencial para el reporte
                safe_matches = []
                for match in matches:
                    if len(match) > 8:
                        safe_match = match[:4] + "*" * (len(match) - 8) + match[-4:]
                    else:
                        safe_match = "*" * len(match)
                    safe_matches.append(safe_match)

                # Añadir al reporte
                report_lines.extend(
                    [
                        f"⚠️  {cred_type} encontrada en commit {metadata['short_hash']}",
                        f"   Fecha: {metadata['date']}, Autor: {metadata['author']}",
                        f"   Asunto: {metadata['subject']}",
                        f"   Credencial parcial: {', '.join(safe_matches)}",
                        "",
                    ]
                )

    return report_lines


def _display_results(found_credentials: bool, report_lines: List[str]):
    """Mostrar resultados del análisis."""
    if found_credentials:
        print("⚠️  SE ENCONTRARON CREDENCIALES EXPUESTAS EN EL HISTORIAL DE GIT")
        print("=" * 70)
        print("\n".join(report_lines))
        print("")
        print("🛡️  RECOMENDACIONES:")
        print(
            "1. Ejecuta 'python scripts/secure_env.py' para limpiar credenciales actuales"
        )
        print("2. Lee la guía de seguridad en 'docs/SEGURIDAD_CREDENCIALES.md'")
        print("3. Considera usar BFG Repo-Cleaner para limpiar el historial de Git")
        print("   https://rtyley.github.io/bfg-repo-cleaner/")
        print("")
    else:
        print("✅ No se encontraron credenciales expuestas en el historial de Git")


def check_git_history():
    """Analizar historial de Git para buscar credenciales."""
    print("🔍 Analizando historial de Git...")
    print()

    # Verificar repositorio Git
    if not _is_git_repository():
        return False

    # Obtener lista de commits
    commits = _get_commits_list()
    if not commits:
        return False

    found_credentials = False
    report_lines = []

    # Analizar cada commit
    for commit in commits:
        if not commit.strip():
            continue

        # Obtener metadatos del commit
        metadata = _get_commit_metadata(commit)
        if not metadata:
            continue

        # Analizar commit en busca de credenciales
        commit_report = _analyze_commit_for_credentials(commit, metadata)
        if commit_report:
            found_credentials = True
            report_lines.extend(commit_report)

    # Mostrar resultados
    _display_results(found_credentials, report_lines)
    return found_credentials


def generate_report(found_credentials):
    """Generar reporte de análisis"""
    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = report_dir / f"credential_scan_{timestamp}.txt"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("🔍 REPORTE DE ANÁLISIS DE CREDENCIALES - GEMINI AI CHATBOT\n")
        f.write("=" * 70 + "\n\n")
        f.write(
            f"Fecha de análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        )

        if found_credentials:
            f.write(
                "⚠️  SE ENCONTRARON CREDENCIALES EXPUESTAS EN EL HISTORIAL DE GIT\n\n"
            )
            f.write("🛡️  RECOMENDACIONES:\n")
            f.write(
                "1. Ejecuta 'python scripts/secure_env.py' para limpiar credenciales actuales\n"
            )
            f.write("2. Lee la guía de seguridad en 'docs/SEGURIDAD_CREDENCIALES.md'\n")
            f.write(
                "3. Considera usar BFG Repo-Cleaner para limpiar el historial de Git\n"
            )
            f.write("   https://rtyley.github.io/bfg-repo-cleaner/\n\n")
        else:
            f.write(
                "✅ No se encontraron credenciales expuestas en el historial de Git\n\n"
            )

    print(f"\n📋 Reporte guardado en: {report_file}")


def main():
    """Función principal"""
    print_banner()

    found_credentials = check_git_history()
    generate_report(found_credentials)

    print("\n✅ ANÁLISIS COMPLETADO")
    return 0 if not found_credentials else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Operación cancelada por el usuario.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
