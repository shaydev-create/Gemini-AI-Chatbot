#!/usr/bin/env python3
"""
Script to restore incorrectly removed return statements.
The previous fix_mypy_errors.py script incorrectly commented out valid return statements.
This script will restore them.
"""

import re
from pathlib import Path


def restore_returns_in_file(file_path: str) -> bool:
    """Restore incorrectly commented return statements in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Pattern to match commented return statements
        # # return ... # Removed incorrect return
        pattern = r'(\s*)# (return .+?) # Removed incorrect return'

        def replace_func(match):
            indent = match.group(1)
            return_statement = match.group(2)
            return f"{indent}{return_statement}"

        content = re.sub(pattern, replace_func, content)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to restore return statements in all Python files."""
    app_dir = Path("app")

    if not app_dir.exists():
        print("Error: 'app' directory not found")
        return

    files_fixed = 0

    # Process all Python files in the app directory
    for py_file in app_dir.rglob("*.py"):
        if restore_returns_in_file(str(py_file)):
            print(f"Fixed: {py_file}")
            files_fixed += 1

    print(f"\nRestored return statements in {files_fixed} files.")

if __name__ == "__main__":
    main()
