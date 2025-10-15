"""
Script: fix_types.py
---------------------------------
Corrige automáticamente errores comunes de tipado (mypy) en todo el proyecto:
 - Agrega `-> None` a funciones sin tipo de retorno.
 - Agrega tipos inteligentes a variables: dict, list, set, Optional.
 - Inserta automáticamente `from typing import Any, Optional` si falta.
 - Procesa todos los archivos dentro de `app/`.

Uso:
    python scripts/fix_types.py
"""

import os
import re
from pathlib import Path

# Directorio base
BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"

# Expresiones regulares
FUNC_DEF_PATTERN = re.compile(r"^(\s*)def\s+(\w+)\((.*?)\)(\s*):(\s*)$")
VAR_ASSIGN_PATTERN = re.compile(r"^(\s*)(\w+)\s*=\s*(.+)$")

def ensure_typing_import(content: str) -> str:
    """Agrega importación de typing si no existe."""
    if "from typing import Any" not in content and "import Any" not in content:
        lines = content.splitlines()
        for i, line in enumerate(lines):
            # Insertar después del último import existente
            if line.startswith("import") or line.startswith("from"):
                continue
            lines.insert(i, "from typing import Any, Optional")
            break
        return "\n".join(lines)
    return content

def infer_type_from_value(value: str) -> str:
    """Detecta tipo adecuado a partir del valor asignado."""
    value = value.strip()
    if value in ("None", "null", "NULL"):
        return "Optional[Any]"
    if value.startswith("{") and value.endswith("}"):
        return "dict[str, Any]"
    if value.startswith("[") and value.endswith("]"):
        return "list[Any]"
    if value.startswith("set(") or value == "set()":
        return "set[Any]"
    if value.startswith('"') or value.startswith("'"):
        return "str"
    if re.match(r"^-?\d+$", value):
        return "int"
    if re.match(r"^-?\d+\.\d+$", value):
        return "float"
    if value.lower() in ("true", "false"):
        return "bool"
    return "Any"

def fix_file(path: Path):
    """Corrige tipos básicos en un archivo Python."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content
    content = ensure_typing_import(content)

    lines = content.splitlines()
    new_lines = []
    for line in lines:
        stripped = line.strip()

        # Ignorar comentarios, imports o decoradores
        if not stripped or stripped.startswith("#") or stripped.startswith("@") or stripped.startswith("import") or stripped.startswith("from"):
            new_lines.append(line)
            continue

        # Corrige funciones sin tipo de retorno
        match_func = FUNC_DEF_PATTERN.match(line)
        if match_func:
            indent, name, args, spacing, endspace = match_func.groups()
            if "->" not in line:
                line = f"{indent}def {name}({args}) -> None:"
            new_lines.append(line)
            continue

        # Corrige variables sin tipo explícito
        match_var = VAR_ASSIGN_PATTERN.match(line)
        if match_var:
            indent, var_name, value = match_var.groups()
            # Evita modificar declaraciones ya tipadas o constantes
            if ":" not in line and not var_name.isupper():
                inferred_type = infer_type_from_value(value)
                line = f"{indent}{var_name}: {inferred_type} = {value}"

        new_lines.append(line)

    new_content = "\n".join(new_lines)

    # Guardar si hubo cambios
    if new_content != original_content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"✅ Tipos corregidos en: {path}")
    else:
        print(f"✔️  Sin cambios: {path}")

def process_directory(directory: Path):
    """Procesa todos los archivos .py dentro del directorio."""
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith(".py"):
                fix_file(Path(root) / filename)

def main():
    print(f"🔧 Iniciando corrección inteligente de tipos en: {APP_DIR}")
    process_directory(APP_DIR)
    print("\n✨ Corrección automática avanzada completada.")

if __name__ == "__main__":
    main()
