# 🤖 GEMINI AI CHATBOT - SISTEMA COMPLETO

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com)
[![Gemini](https://img.shields.io/badge/Gemini-AI-orange.svg)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Sistema completo de chatbot con inteligencia artificial, procesamiento multimedia y autenticación avanzada.

## 🌟 Características Principales

### 🤖 Inteligencia Artificial
- **Gemini AI Integration**: Chat inteligente con el modelo Gemini Pro de Google
- **Conversaciones Contextuales**: Mantiene el contexto de la conversación
- **Respuestas Inteligentes**: Procesamiento avanzado de lenguaje natural

### 🔐 Sistema de Autenticación
- **Registro y Login**: Sistema completo de usuarios
- **JWT Tokens**: Autenticación segura con tokens
- **Recuperación de Contraseña**: Sistema de reset por email
- **Perfiles de Usuario**: Gestión completa de perfiles
- **Límites de Uso**: Control de uso por usuario

### 📄 Procesamiento de Documentos
- **PDF Processing**: Extracción de texto de documentos PDF
- **OCR de Imágenes**: Reconocimiento óptico de caracteres
- **Múltiples Formatos**: Soporte para PDF, imágenes y texto
- **Análisis Inteligente**: Procesamiento con IA de documentos

### 🎵 Transcripción de Audio
- **Múltiples Formatos**: MP3, WAV, M4A, OGG
- **Alta Precisión**: Transcripción precisa de audio a texto
- **Procesamiento Rápido**: Optimizado para velocidad

### 🌐 Interfaz Web Moderna
- **Diseño Responsivo**: Compatible con todos los dispositivos
- **UI/UX Avanzada**: Interfaz moderna y intuitiva
- **Tiempo Real**: Actualizaciones en tiempo real
- **PWA Ready**: Funcionalidad de aplicación web progresiva

### 🔒 Seguridad Avanzada
- **HTTPS/SSL**: Comunicación segura
- **Rate Limiting**: Protección contra abuso
- **Validación de Datos**: Validación completa de entrada
- **Sanitización**: Protección contra XSS y inyecciones

## 🚀 Instalación Rápida

### 1. Clonar el Repositorio
```bash
git clone <repository-url>
cd gemini-ai-chatbot
```

### 2. Instalación Automática
```bash
# Instalar todas las dependencias automáticamente
python install_dependencies.py
```

### 3. Configuración
```bash
# Copiar archivo de configuración
cp .env.example .env

# Editar configuración (especialmente GEMINI_API_KEY)
nano .env
```

### 4. Inicio Rápido
```bash
# Iniciar con configuración automática
python quick_start.py
```

## 📋 Instalación Manual

### Requisitos del Sistema
- **Python 3.8+**
- **pip** (gestor de paquetes de Python)
- **Tesseract OCR** (opcional, para OCR de imágenes)

### Dependencias Python
```bash
pip install -r requirements.txt
```

### Dependencias Principales
- `Flask==3.0.3` - Framework web
- `Flask-JWT-Extended==4.6.0` - Autenticación JWT
- `Flask-SQLAlchemy==3.1.1` - ORM de base de datos
- `google-generativeai==0.8.3` - API de Gemini
- `Pillow==10.4.0` - Procesamiento de imágenes
- `PyPDF2==3.0.1` - Procesamiento de PDF
- `PyMuPDF==1.23.26` - Procesamiento avanzado de PDF
- `pytesseract==0.3.10` - OCR de imágenes
- `opencv-python==4.9.0.80` - Visión por computadora
- `bcrypt==4.2.0` - Hashing de contraseñas

### Instalación de Tesseract OCR

#### Windows
1. Descargar desde: https://github.com/UB-Mannheim/tesseract/wiki
2. Ejecutar instalador como administrador
3. Agregar al PATH: `C:\Program Files\Tesseract-OCR`

#### macOS
```bash
brew install tesseract
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-spa
```

## ⚙️ Configuración

### Variables de Entorno (.env)

```env
# API de Gemini (REQUERIDO)
GEMINI_API_KEY=tu_api_key_aqui

# Seguridad
JWT_SECRET_KEY=clave_secreta_jwt
SECRET_KEY=clave_secreta_flask

# Base de datos
DATABASE_URL=sqlite:///instance/ai_chatbot.db

# Servidor
PORT=5000
HOST=0.0.0.0
DEBUG=False

# HTTPS
ENABLE_HTTPS=True
SSL_CERT_PATH=ssl/cert.pem
SSL_KEY_PATH=ssl/key.pem

# Límites
DAILY_MESSAGE_LIMIT=100
DAILY_UPLOAD_LIMIT=50
MAX_CONTENT_LENGTH=50
```

### Obtener API Key de Gemini
1. Visita: https://aistudio.google.com/
2. Inicia sesión con tu cuenta de Google
3. Crea una nueva API key
4. Copia la key al archivo `.env`

## 🏃‍♂️ Uso

### Inicio del Servidor

#### Método 1: Inicio Rápido (Recomendado)
```bash
python quick_start.py
```

#### Método 2: Inicio Manual
```bash
python app.py
```

#### Método 3: Con HTTPS
```bash
python start_https.py
```

### Acceso a la Aplicación
- **HTTP**: http://localhost:5000
- **HTTPS**: https://localhost:5000

## 📡 API Endpoints

### Autenticación
- `POST /auth/register` - Registro de usuario
- `POST /auth/login` - Inicio de sesión
- `POST /auth/logout` - Cerrar sesión
- `GET /auth/profile` - Perfil de usuario
- `POST /auth/forgot-password` - Recuperar contraseña
- `POST /auth/reset-password` - Resetear contraseña

### Chat
- `POST /api/chat` - Enviar mensaje al chatbot
- `GET /api/chat/history` - Historial de conversaciones

### Archivos
- `POST /api/upload` - Subir archivo
- `POST /api/transcribe` - Transcribir audio
- `POST /api/process-document` - Procesar documento

### Sistema
- `GET /api/health` - Estado del sistema
- `GET /api/metrics` - Métricas de rendimiento

## 🗂️ Estructura del Proyecto

```
gemini-ai-chatbot/
├── 📁 app.py                 # Aplicación principal
├── 📁 quick_start.py         # Script de inicio rápido
├── 📁 install_dependencies.py # Instalador de dependencias
├── 📁 requirements.txt       # Dependencias Python
├── 📁 .env.example          # Configuración de ejemplo
├── 📁 auth_routes.py         # Rutas de autenticación
├── 📁 core/
│   ├── 📄 routes.py          # Rutas principales
│   └── 📄 chat_sessions.py   # Gestión de sesiones
├── 📁 src/
│   ├── 📄 models.py          # Modelos de base de datos
│   ├── 📄 database.py        # Configuración de BD
│   ├── 📄 auth.py           # Utilidades de autenticación
│   └── 📄 config.py         # Configuración
├── 📁 utils/
│   └── 📁 media/
│       ├── 📄 document_utils.py # Procesamiento de documentos
│       └── 📄 audio_utils.py    # Procesamiento de audio
├── 📁 templates/
│   ├── 📄 index.html         # Página principal
│   ├── 📄 chat.html          # Interfaz de chat
│   └── 📁 auth/              # Templates de autenticación
├── 📁 static/
│   ├── 📁 css/              # Estilos
│   ├── 📁 js/               # JavaScript
│   └── 📁 images/           # Imágenes
├── 📁 uploads/              # Archivos subidos
├── 📁 ssl/                  # Certificados SSL
└── 📁 logs/                 # Archivos de log
```

## 🔧 Funcionalidades Detalladas

### Sistema de Chat
- **Conversaciones Persistentes**: Las conversaciones se guardan en base de datos
- **Contexto Inteligente**: El bot mantiene el contexto de la conversación
- **Respuestas Rápidas**: Optimizado para respuestas en tiempo real
- **Formato Rico**: Soporte para markdown y formato de texto

### Procesamiento de Documentos
- **PDF Inteligente**: Extracción de texto con PyPDF2 y PyMuPDF
- **OCR Avanzado**: Reconocimiento de texto en imágenes con Tesseract
- **Análisis de Contenido**: Procesamiento inteligente del contenido extraído
- **Múltiples Formatos**: PDF, PNG, JPG, JPEG, GIF, TXT

### Transcripción de Audio
- **Alta Calidad**: Transcripción precisa de audio a texto
- **Formatos Múltiples**: MP3, WAV, M4A, OGG
- **Procesamiento Rápido**: Optimizado para velocidad
- **Integración con Chat**: Los audios transcritos se pueden enviar al chat

### Seguridad
- **Autenticación JWT**: Tokens seguros con expiración
- **Hashing de Contraseñas**: bcrypt para seguridad de contraseñas
- **Rate Limiting**: Protección contra ataques de fuerza bruta
- **Validación de Entrada**: Sanitización completa de datos
- **HTTPS/SSL**: Comunicación encriptada

## 🛠️ Desarrollo

### Modo de Desarrollo
```bash
# Activar modo debug
export FLASK_ENV=development
export DEBUG=True
python app.py
```

### Testing
```bash
# Ejecutar tests
python -m pytest tests/

# Test de audio
python test_audio_transcription.py
```

### Logs
```bash
# Ver logs en tiempo real
tail -f logs/ai_chatbot.log
```

## 🐳 Docker

### Construcción
```bash
docker build -t gemini-chatbot .
```

### Ejecución
```bash
docker run -p 5000:5000 -e GEMINI_API_KEY=tu_key gemini-chatbot
```

### Docker Compose
```bash
docker-compose up -d
```

## 📊 Monitoreo

### Métricas Disponibles
- **Rendimiento**: Tiempo de respuesta, uso de memoria
- **Uso**: Número de mensajes, archivos procesados
- **Errores**: Logs de errores y excepciones
- **Usuarios**: Estadísticas de usuarios activos

### Endpoints de Monitoreo
- `GET /api/health` - Estado del sistema
- `GET /api/metrics` - Métricas detalladas
- `GET /api/stats` - Estadísticas de uso

## 🔍 Solución de Problemas

### Problemas Comunes

#### Error: "Gemini API key not configured"
**Solución**: Configura tu API key en el archivo `.env`
```bash
GEMINI_API_KEY=tu_api_key_real_aqui
```

#### Error: "Tesseract not found"
**Solución**: Instala Tesseract OCR y agrégalo al PATH
```bash
# Windows
set PATH=%PATH%;C:\Program Files\Tesseract-OCR

# Linux/macOS
export PATH=$PATH:/usr/local/bin
```

#### Error: "Database not found"
**Solución**: Ejecuta el script de inicialización
```bash
python install_dependencies.py
```

#### Error de permisos en uploads
**Solución**: Verifica permisos de directorio
```bash
chmod 755 uploads/
chmod 755 uploads/temp/
```

### Logs de Debug
```bash
# Activar logging detallado
export LOG_LEVEL=DEBUG
python app.py
```

## 🤝 Contribución

### Cómo Contribuir
1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

### Estándares de Código
- **PEP 8**: Seguir estándares de Python
- **Documentación**: Documentar funciones y clases
- **Tests**: Incluir tests para nuevas funcionalidades
- **Commits**: Mensajes descriptivos en español

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🙏 Agradecimientos

- **Google Gemini AI** - Por la API de inteligencia artificial
- **Flask Community** - Por el excelente framework web
- **Tesseract OCR** - Por el motor de OCR
- **OpenCV** - Por las herramientas de visión por computadora

## 📞 Soporte

### Documentación Adicional
- [README_AUDIO_TRANSCRIPTION.md](README_AUDIO_TRANSCRIPTION.md) - Transcripción de audio
- [README_HTTPS.md](README_HTTPS.md) - Configuración HTTPS
- [README_DEPENDENCIES.md](README_DEPENDENCIES.md) - Gestión de dependencias

### Contacto
- **Issues**: Reporta problemas en GitHub Issues
- **Discussions**: Únete a las discusiones del proyecto
- **Wiki**: Consulta la documentación extendida

---

**🚀 ¡Disfruta tu chatbot con IA!**

*Desarrollado con ❤️ por Gemini AI Assistant*