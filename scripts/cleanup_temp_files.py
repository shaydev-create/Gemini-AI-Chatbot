import os
import shutil

# Carpetas y archivos a limpiar
folders_to_clean = [
    'logs',
    'reports',
    'app/__pycache__',
    'config/__pycache__',
    '.pytest_cache',
    '.venv',
    'instance',
    'uploads/audio',
    'uploads/documents',
    'uploads/images',
]
files_to_remove = [
    'e2e_test_output.txt',
    'gemini-ai-chatbot-chrome-store-ready.zip',
    'gemini-ai-chatbot-chrome-v1.0.2-fixed.zip',
    'launch_readiness_report_20250720_045420.json',
]

def remove_files(files):
    for f in files:
        if os.path.exists(f):
            os.remove(f)
            print(f"Eliminado archivo: {f}")

def clean_folders(folders):
    for folder in folders:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"Eliminada carpeta: {folder}")

if __name__ == "__main__":
    remove_files(files_to_remove)
    clean_folders(folders_to_clean)
    print("Limpieza de archivos temporales y obsoletos completada.")
