#!/usr/bin/env python3
"""
Script de inicialización y configuración del proyecto Gemini AI Chatbot.
Automatiza la configuración inicial del entorno de desarrollo.
"""

import os
import sys
import subprocess
import secrets
import shutil
from pathlib import Path

def print_banner():
    """Imprime el banner del proyecto."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    GEMINI AI CHATBOT                         ║
    ║                  Setup & Configuration                       ║
    ║                                                              ║
    ║  🤖 Configuración automática del entorno de desarrollo      ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Verifica que la versión de Python sea compatible."""
    if sys.version_info < (3, 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} - Compatible")

def check_dependencies():
    """Verifica que las dependencias del sistema estén instaladas."""
    dependencies = ['pip', 'git']
    missing = []
    
    for dep in dependencies:
        try:
            subprocess.run([dep, '--version'], 
                         capture_output=True, check=True)
            print(f"✅ {dep} - Instalado")
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing.append(dep)
            print(f"❌ {dep} - No encontrado")
    
    if missing:
        print(f"\n❌ Dependencias faltantes: {', '.join(missing)}")
        print("   Por favor, instala las dependencias faltantes antes de continuar.")
        sys.exit(1)

def create_virtual_environment():
    """Crea y activa el entorno virtual."""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Entorno virtual ya existe")
        return
    
    print("📦 Creando entorno virtual...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Entorno virtual creado exitosamente")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creando entorno virtual: {e}")
        sys.exit(1)

def install_requirements():
    """Instala las dependencias de Python."""
    print("📦 Instalando dependencias de Python...")
    
    # Determinar el ejecutable de pip en el entorno virtual
    if os.name == 'nt':  # Windows
        pip_path = Path("venv/Scripts/pip.exe")
    else:  # Linux/Mac
        pip_path = Path("venv/bin/pip")
    
    if not pip_path.exists():
        print("❌ No se encontró pip en el entorno virtual")
        sys.exit(1)
    
    try:
        # Actualizar pip
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
        
        # Instalar dependencias
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencias instaladas exitosamente")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        sys.exit(1)

def generate_secret_keys():
    """Genera claves secretas seguras."""
    return {
        'SECRET_KEY': secrets.token_urlsafe(32),
        'JWT_SECRET_KEY': secrets.token_urlsafe(32)
    }

def setup_environment_file():
    """Configura el archivo de variables de entorno."""
    env_file = Path(".env")
    env_dev_file = Path(".env.dev")
    
    if env_file.exists():
        print("✅ Archivo .env ya existe")
        return
    
    if not env_dev_file.exists():
        print("❌ Archivo .env.dev no encontrado")
        sys.exit(1)
    
    print("⚙️ Configurando variables de entorno...")
    
    # Generar claves secretas
    keys = generate_secret_keys()
    
    # Leer plantilla
    with open(env_dev_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Reemplazar valores por defecto
    content = content.replace('dev_secret_key_change_in_production', keys['SECRET_KEY'])
    content = content.replace('dev_jwt_secret_change_in_production', keys['JWT_SECRET_KEY'])
    
    # Escribir archivo .env
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Archivo .env configurado")
    print("⚠️  IMPORTANTE: Configura tu GEMINI_API_KEY en el archivo .env")

def create_directories():
    """Crea directorios necesarios."""
    directories = [
        'logs',
        'uploads',
        'ssl',
        'backups'
    ]
    
    print("📁 Creando directorios necesarios...")
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Directorio '{directory}' creado")

def initialize_database():
    """Inicializa la base de datos."""
    print("🗄️ Inicializando base de datos...")
    
    # Determinar el ejecutable de Python en el entorno virtual
    if os.name == 'nt':  # Windows
        python_path = Path("venv/Scripts/python.exe")
    else:  # Linux/Mac
        python_path = Path("venv/bin/python")
    
    try:
        subprocess.run([
            str(python_path), 
            "-c", 
            "from config.database import init_db; init_db()"
        ], check=True)
        print("✅ Base de datos inicializada")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Error inicializando base de datos: {e}")
        print("   Puedes inicializarla manualmente más tarde")

def run_tests():
    """Ejecuta los tests básicos."""
    print("🧪 Ejecutando tests básicos...")
    
    # Determinar el ejecutable de Python en el entorno virtual
    if os.name == 'nt':  # Windows
        python_path = Path("venv/Scripts/python.exe")
    else:  # Linux/Mac
        python_path = Path("venv/bin/python")
    
    try:
        subprocess.run([
            str(python_path), 
            "-m", "pytest", 
            "tests/unit/", 
            "-v", 
            "--tb=short"
        ], check=True)
        print("✅ Tests básicos pasaron exitosamente")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Algunos tests fallaron: {e}")
        print("   Revisa la configuración y dependencias")

def print_next_steps():
    """Imprime los siguientes pasos."""
    next_steps = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    CONFIGURACIÓN COMPLETA                   ║
    ╚══════════════════════════════════════════════════════════════╝
    
    🎉 ¡Configuración completada exitosamente!
    
    📋 SIGUIENTES PASOS:
    
    1. 🔑 Configurar API Key de Gemini:
       - Obtén tu API key en: https://makersuite.google.com/app/apikey
       - Edita el archivo .env y reemplaza: GEMINI_API_KEY=your_gemini_api_key_here
    
    2. 🚀 Ejecutar la aplicación:
       - Windows: venv\\Scripts\\activate && python app/main.py
       - Linux/Mac: source venv/bin/activate && python app/main.py
    
    3. 🌐 Acceder a la aplicación:
       - Desarrollo: http://localhost:5000
       - Chat: http://localhost:5000/chat
       - Health: http://localhost:5000/api/health
    
    4. 🧪 Ejecutar tests:
       - Todos: pytest tests/ -v
       - Unitarios: pytest tests/unit/ -v
       - Integración: pytest tests/integration/ -v
    
    5. 🐳 Docker (opcional):
       - Desarrollo: docker-compose -f docker-compose.dev.yml up -d
       - Producción: docker-compose -f docker-compose.prod.yml up -d
    
    📚 DOCUMENTACIÓN:
    - README.md - Documentación completa
    - /api/health - Estado de la aplicación
    - /api/metrics - Métricas de rendimiento
    
    ⚠️  IMPORTANTE:
    - Nunca commits archivos .env con claves reales
    - Usa .env.prod para configuración de producción
    - Revisa los logs en el directorio 'logs/'
    
    ¡Disfruta construyendo con Gemini AI! 🤖✨
    """
    print(next_steps)

def main():
    """Función principal del script de configuración."""
    try:
        print_banner()
        
        print("🔍 Verificando requisitos del sistema...")
        check_python_version()
        check_dependencies()
        
        print("\n📦 Configurando entorno de desarrollo...")
        create_virtual_environment()
        install_requirements()
        
        print("\n⚙️ Configurando aplicación...")
        setup_environment_file()
        create_directories()
        
        print("\n🗄️ Configurando base de datos...")
        initialize_database()
        
        print("\n🧪 Ejecutando verificaciones...")
        run_tests()
        
        print_next_steps()
        
    except KeyboardInterrupt:
        print("\n\n❌ Configuración cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()