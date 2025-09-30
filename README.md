# 🚀 Gemini AI Futuristic Chatbot - Versión 2025

Un chatbot inteligente potenciado por Google Gemini AI con interfaz web moderna y extensión de Chrome.

[![Chrome Web Store](https://img.shields.io/badge/Chrome%20Web%20Store-Available-brightgreen)](https://chrome.google.com/webstore)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/shaydev-create/Gemini-AI-Chatbot)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Privacy Policy](https://img.shields.io/badge/Privacy-Policy-green)](docs/PRIVACY_POLICY.md)

## ✨ Características

 - 🤖 **IA Avanzada**: Integración con Google Gemini AI
 - 🌐 **Interfaz Web**: Diseño moderno, responsivo y accesible (ARIA, skip links, selector de idioma)
 - 🔌 **Extensión Chrome**: Acceso rápido desde el navegador
 - 🔒 **Seguro**: HTTPS, autenticación, validación y protección CSRF/XSS
 - 📱 **PWA**: Funciona como aplicación móvil
 - 🐳 **Docker**: Despliegue fácil con contenedores
 - 📊 **Monitoreo**: Métricas Prometheus integradas

 - 🌍 **Multiidioma avanzado**: Selección dinámica de idioma en toda la app

 - 🛠️ **Panel de Administración**: Gestión y acceso restringido para administradores

## 🛠️ Panel de Administración

El sistema incluye un panel de administración básico accesible solo para usuarios autenticados con rol de administrador.

- **Ruta:** `/admin`
- **Protección:** Requiere JWT y rol de administrador
- **Template:** `admin.html`

Ejemplo de acceso:
```bash
curl -H "Authorization: Bearer <token_admin>" https://localhost:5000/admin
# Respuesta: Renderiza el panel si el usuario es admin
```

## 🚀 Inicio Rápido
## 🌍 Multiidioma avanzado

La aplicación soporta traducción dinámica de textos en español e inglés. Puedes agregar nuevos idiomas creando archivos JSON en `app/i18n/`.

Ejemplo para agregar francés:
1. Crea `app/i18n/fr.json` con las claves y traducciones.
2. Accede con `?lang=fr` en la URL o selecciona desde el frontend.

Todos los templates usan la función `translate` para mostrar textos según el idioma seleccionado.

### ⚡ Ejecución Inmediata

```bash
# 1. Clonar repositorio
git clone https://github.com/shaydev-create/Gemini-AI-Chatbot.git
cd Gemini-AI-Chatbot

# 2. Configurar API Key
cp .env.example .env
# Editar .env y agregar tu GEMINI_API_KEY

# 3. Ejecutar aplicación
python app/main.py

# 4. Abrir navegador en: https://localhost:5000
```

### 🐳 Con Docker (Recomendado para Producción)

```bash
# Ejecutar con Docker
docker-compose up -d

# Acceder a https://localhost:5000
```

## 🔧 Configuración

### 🔑 Variables de Entorno Requeridas

```env
# Archivo .env
GEMINI_API_KEY=tu_api_key_aqui
SECRET_KEY=tu_secret_key_seguro
FLASK_ENV=production
```

### 🔐 Protección de Credenciales

Para proteger tus credenciales y evitar exposición accidental en GitHub:

```bash
# Limpiar credenciales antes de hacer commit
python scripts/secure_env.py

# Ver guía completa de seguridad
cat docs/SEGURIDAD_CREDENCIALES.md
```

[📚 Ver guía completa de seguridad de credenciales](docs/SEGURIDAD_CREDENCIALES.md)

### 🎯 Obtener API Key de Gemini

1. **Ve a [Google AI Studio](https://aistudio.google.com/)**
2. **Crea una cuenta** o inicia sesión
3. **Genera una nueva API key**
4. **Copia la key** a tu archivo `.env`

## 🌐 Extensión de Chrome

### 📥 Instalación

1. **Descarga** o clona este repositorio
2. **Abre Chrome** y ve a `chrome://extensions/`
3. **Activa** "Modo de desarrollador" (esquina superior derecha)
4. **Clic** en "Cargar extensión sin empaquetar"
5. **Selecciona** la carpeta `chrome_extension/`
6. **¡Listo!** El icono 🚀 aparecerá en la barra de herramientas

### 🎯 Uso de la Extensión

- **Clic en el icono** 🚀 para abrir el popup
- **"Abrir Aplicación"** para acceder al chatbot completo
- **Funciona solo** cuando tu servidor local está ejecutándose

## 📁 Estructura del Proyecto

```
Gemini-AI-Chatbot/
├── 📱 app/                    # Aplicación principal Flask
│   ├── api/                   # Rutas API REST
│   ├── core/                  # Funcionalidades core
│   ├── services/              # Servicios (Gemini AI)
│   ├── static/                # CSS, JS, imágenes
│   ├── templates/             # Templates HTML
│   ├── utils/                 # Utilidades y helpers
│   └── main.py               # 🎯 PUNTO DE ENTRADA
├── 🔧 config/                 # Configuraciones
├── 🌐 chrome_extension/       # Extensión de Chrome
│   ├── manifest.json          # Configuración extensión
│   ├── background.js          # Service worker
│   ├── index.html            # Popup principal
│   └── icons/                # Iconos de la extensión
├── 🐳 deployment/             # Docker y despliegue
├── 📚 docs/                   # Documentación
│   ├── PRIVACY_POLICY.md     # 🛡️ Política de privacidad
│   └── SEGURIDAD_CREDENCIALES.md # 🔐 Guía de seguridad
├── 🧪 tests/                  # Tests automatizados
├── .env                       # Variables de entorno
├── requirements.txt           # Dependencias Python
└── README.md                 # Este archivo
```

## 🚀 Cómo Ejecutar

### 🖥️ Método 1: Ejecución Local (Más Rápido)

```bash
# Navegar al directorio
cd "C:\Users\shaya\OneDrive\Documents\Python+Visual Studio Code\Google Gemini"

# Ejecutar directamente
python app/main.py

# La aplicación estará disponible en:
# 🌐 https://localhost:5000
# 🌐 https://127.0.0.1:5000
```

### 📚 Ejemplos de Uso de la API

#### Autenticación
```bash
curl -X POST https://localhost:5000/api/auth/login -d '{"username": "user", "password": "pass"}' -H "Content-Type: application/json"
# Respuesta: {"access_token": "..."}
```

#### Chat
```bash
curl -X POST https://localhost:5000/api/chat -d '{"message": "Hola Gemini!"}' -H "Authorization: Bearer <token>" -H "Content-Type: application/json"
# Respuesta: {"reply": "¡Hola humano!"}
```

#### Subida de Archivos
```bash
curl -X POST https://localhost:5000/api/upload -F "file=@archivo.txt" -H "Authorization: Bearer <token>"
# Respuesta: {"status": "success", "filename": "archivo.txt"}
```

### 🐳 Método 2: Docker

```bash
# Desarrollo
docker-compose -f docker-compose.dev.yml up -d

# Producción
docker-compose up -d

# Ver logs
docker-compose logs -f app
```

## 🧪 Testing y Calidad

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Tests con cobertura
pytest --cov=app tests/

# Linting
flake8 app/
black app/
 
# Limpieza automática de archivos temporales y credenciales
python scripts/cleanup_temp_files.py
python scripts/secure_env.py

# Migraciones automáticas de base de datos
scripts/migrate_db.ps1
```

## 📊 Monitoreo y Salud

### 🔍 Health Check

```bash
# Verificar estado de la aplicación
curl https://localhost:5000/api/health

# Respuesta esperada:
# {"status": "healthy", "timestamp": "2025-01-17T..."}
```

### 📈 Métricas Prometheus

```bash
# Obtener métricas para monitoreo
curl https://localhost:5000/metrics
# Respuesta: formato Prometheus
# flask_request_count_total{method="GET",endpoint="/api/chat"} 42
# flask_request_latency_seconds_bucket{le="0.5",endpoint="/api/chat"} 40
```

### 📋 Logs

```bash
# Ver logs en tiempo real
tail -f logs/app.log

# Con Docker
docker-compose logs -f app
```

## 🔒 Seguridad y Privacidad

### 🛡️ Características de Seguridad

- ✅ **HTTPS** habilitado por defecto
- ✅ **Validación** de entrada estricta
- ✅ **Rate limiting** para prevenir abuso
- ✅ **Headers de seguridad** configurados
- ✅ **Sanitización** de datos de usuario
- ✅ **Protección de credenciales** con [guía de seguridad](docs/SEGURIDAD_CREDENCIALES.md)

### 🔐 Privacidad

- ❌ **NO recopilamos** datos personales
- ❌ **NO almacenamos** conversaciones
- ❌ **NO utilizamos** cookies de seguimiento
- ✅ **Procesamiento local** únicamente
- ✅ **Política de privacidad** completa: [docs/PRIVACY_POLICY.md](docs/PRIVACY_POLICY.md)

## 🌍 Despliegue en Producción

### 🚀 Heroku

```bash
# Configurar variables de entorno
heroku config:set GEMINI_API_KEY=tu_api_key
heroku config:set SECRET_KEY=tu_secret_key

# Desplegar
git push heroku main
```

### 🖥️ VPS/Servidor

```bash
# En tu servidor
git clone https://github.com/shaydev-create/Gemini-AI-Chatbot.git
cd Gemini-AI-Chatbot

# Con Docker + Nginx
docker-compose --profile nginx up -d
```

## 🤝 Contribuir

1. **Fork** el proyecto
2. **Crea** una rama (`git checkout -b feature/AmazingFeature`)
3. **Commit** tus cambios (`git commit -m 'Add AmazingFeature'`)
4. **Push** a la rama (`git push origin feature/AmazingFeature`)
5. **Abre** un Pull Request

## 📞 Soporte y Contacto

- 📧 **Email:** shayannelguapo10@gmail.com
- 🐛 **Issues:** [GitHub Issues](https://github.com/shaydev-create/Gemini-AI-Chatbot/issues)
- 🐙 **GitHub:** [shaydev-create](https://github.com/shaydev-create)
- 🏪 **Chrome Web Store:** Gemini AI Futuristic Chatbot

## 📄 Licencia

Este proyecto está bajo la **Licencia MIT**. Ver [LICENSE](LICENSE) para más detalles.

## 🎯 Roadmap

 - [x] 📈 Métricas Prometheus para monitoreo
 - [x] 🌍 Accesibilidad e internacionalización en frontend
 - [x] 🔄 Scripts automáticos de migración y limpieza
 - [ ] 📱 Aplicación móvil nativa
 - [ ] 🌍 Soporte multiidioma avanzado
 - [ ] 🎨 Temas personalizables
 - [ ] 📊 Dashboard de analytics
 - [ ] 🔌 API pública
 - [ ] 🤖 Más modelos de IA

---

**🚀 Gemini AI Futuristic Chatbot** - Desarrollado con ❤️ por [shaydev-create](https://github.com/shaydev-create)

## 🎯 Roadmap

- [ ] Migración a Vertex AI
- [ ] Soporte multiidioma
- [ ] Integración con bases de datos
- [ ] API REST completa
- [ ] Aplicación móvil nativa

---

⭐ **¡Dale una estrella si te gusta el proyecto!** ⭐
##  Configuraci�n de Vertex AI

Este proyecto est� configurado para usar Google Cloud Vertex AI como alternativa a la API directa de Gemini. Vertex AI ofrece mejor escalabilidad y control de costos.

### Configuraci�n del Proyecto
- **Proyecto ID**: gen-lang-client-0952676857
- **Regi�n**: us-central1
- **Modelo**: gemini-1.5-flash

### Pasos para configurar Vertex AI:

1. **Accede a tu proyecto de Google Cloud**:
   `
   https://console.cloud.google.com/welcome?cloudshell=true&project=gen-lang-client-0952676857
   `

2. **Sigue las instrucciones detalladas**:
   - Ve al archivo credentials/SETUP_INSTRUCTIONS.md
   - Ejecuta los comandos en Google Cloud Shell
   - Descarga el archivo de credenciales

3. **Verifica la configuraci�n**:
   `ash
   python test_vertex_ai.py
   `

### Variables de entorno configuradas:
`env
GOOGLE_CLOUD_PROJECT_ID=gen-lang-client-0952676857
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=./credentials/vertex-ai-key.json
VERTEX_AI_ENABLED=True
VERTEX_AI_MODEL=gemini-1.5-flash
VERTEX_AI_MAX_DAILY_COST=50.0
`

