#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 SCRIPT DE CORRECCIÓN RÁPIDA DE TESTS
======================================

Corrige automáticamente las importaciones problemáticas en los tests.
"""

import re
from pathlib import Path


def fix_test_imports():
    """Corregir importaciones problemáticas en los tests."""
    project_root = Path(__file__).parent.parent

    # Correcciones a aplicar
    fixes = [
        # tests/test_main.py
        {
            "file": "tests/test_main.py",
            "replacements": [
                (
                    r"validate_password_strength\(",
                    "AuthManager().validate_password_strength(",
                ),
            ],
        },
        # tests/unit/test_app_auth.py
        {
            "file": "tests/unit/test_app_auth.py",
            "replacements": [
                (
                    r"from app\.auth import.*get_current_user_with_verification.*",
                    "from app.auth import AuthManager",
                ),
                (
                    r"get_current_user_with_verification\(",
                    "AuthManager().get_current_user(",
                ),
            ],
        },
        # tests/unit/test_gemini_service.py
        {
            "file": "tests/unit/test_gemini_service.py",
            "replacements": [
                (
                    r"from app\.services\.gemini_service import gemini_service",
                    "from app.services.gemini_service import GeminiService",
                ),
                (r"gemini_service\.", "GeminiService()."),
            ],
        },
        # tests/unit/test_multimodal_service.py
        {
            "file": "tests/unit/test_multimodal_service.py",
            "replacements": [
                (
                    r"from app\.services\.multimodal_service import.*get_multimodal_service.*",
                    "from app.services.multimodal_service import MultimodalService",
                ),
                (r"get_multimodal_service\(\)", "MultimodalService()"),
            ],
        },
        # tests/unit/test_routes.py
        {
            "file": "tests/unit/test_routes.py",
            "replacements": [
                (
                    r"from app\.api\.routes import register_api_routes",
                    "from app.api.routes import api_bp",
                ),
                (r"register_api_routes\(", "api_bp."),
            ],
        },
    ]

    for fix in fixes:
        file_path = project_root / fix["file"]
        if file_path.exists():
            try:
                content = file_path.read_text(encoding="utf-8")
                original_content = content

                for pattern, replacement in fix["replacements"]:
                    content = re.sub(pattern, replacement, content)

                if content != original_content:
                    file_path.write_text(content, encoding="utf-8")
                    print(f"✅ Corregido: {fix['file']}")
                else:
                    print(f"ℹ️  Sin cambios: {fix['file']}")

            except Exception as e:
                print(f"❌ Error en {fix['file']}: {e}")
        else:
            print(f"⚠️  No encontrado: {fix['file']}")


if __name__ == "__main__":
    fix_test_imports()
    print("\n🎯 Correcciones aplicadas. Ejecuta pytest nuevamente.")
