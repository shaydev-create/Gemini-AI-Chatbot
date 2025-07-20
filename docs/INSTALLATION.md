# Guía de Instalación - Gemini AI Chatbot

## 🚀 Instalación Rápida

### Prerrequisitos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git (opcional, para clonar el repositorio)

### Instalación Paso a Paso

#### 1. Clonar el Repositorio
```bash
git clone https://github.com/shaydev-create/Gemini-AI-Chatbot.git
cd Gemini-AI-Chatbot
```

#### 2. Crear Entorno Virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

#### 4. Configurar API Key
```bash
# Ejecutar el configurador automático
python scripts/setup_api_key.py
```

O configurar manualmente:
```bash
# Crear archivo .env
echo "GOOGLE_API_KEY=tu_api_key_aqui" > .env
```

#### 5. Ejecutar la Aplicación
```bash
# Opción 1: Archivo principal
python app/main.py

# Opción 2: Archivo de compatibilidad
python app.py
```

## 🔧 Configuración Avanzada

### Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto:

```env
# API Configuration
GOOGLE_API_KEY=tu_google_api_key

# Server Configuration
HOST=0.0.0.0
PORT=5000
USE_HTTPS=True
FLASK_DEBUG=False

# Security
SECRET_KEY=tu_clave_secreta_super_segura
JWT_SECRET_KEY=tu_jwt_secret_key

# Database
DATABASE_URL=sqlite:///gemini_chatbot.db

# Logging
LOG_LEVEL=INFO
```

### Configuración SSL/HTTPS
El sistema genera automáticamente certificados SSL para desarrollo:

```bash
# Los certificados se crean automáticamente en:
# ssl/server.crt
# ssl/server.key
```

### Base de Datos
La aplicación usa SQLite por defecto. Para producción, configura PostgreSQL:

```env
DATABASE_URL=postgresql://usuario:password@localhost/gemini_chatbot
```

## 🐳 Instalación con Docker

### Docker Compose (Recomendado)
```bash
# Desarrollo
docker-compose -f docker-compose.dev.yml up

# Producción
docker-compose up
```

### Docker Manual
```bash
# Construir imagen
docker build -t gemini-ai-chatbot .

# Ejecutar contenedor
docker run -p 5000:5000 -e GOOGLE_API_KEY=tu_api_key gemini-ai-chatbot
```

## 🌐 Despliegue en Producción

### Heroku
```bash
# Instalar Heroku CLI
# Configurar variables de entorno en Heroku Dashboard

heroku create tu-app-name
heroku config:set GOOGLE_API_KEY=tu_api_key
git push heroku main
```

### Netlify (Solo Frontend)
1. Conecta tu repositorio GitHub
2. Configura las variables de entorno
3. Despliega automáticamente

### VPS/Servidor Dedicado
```bash
# Usar gunicorn para producción
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app.main:app
```

## 🔍 Verificación de Instalación

### Ejecutar Tests
```bash
python -m pytest tests/
```

### Verificar Configuración
```bash
python scripts/launch_readiness_check.py
```

### Acceder a la Aplicación
- **HTTP**: http://localhost:5000
- **HTTPS**: https://localhost:5000

## 🛠️ Solución de Problemas

### Error: "No module named 'google.generativeai'"
```bash
pip install google-generativeai
```

### Error: "API Key not found"
```bash
# Verificar archivo .env
cat .env

# Reconfigurar API key
python scripts/setup_api_key.py
```

### Error de Certificados SSL
```bash
# Regenerar certificados
python -c "from config.ssl_config import SSLConfig; SSLConfig().create_ssl_certificates(force_recreate=True)"
```

### Puerto en Uso
```bash
# Cambiar puerto en .env
echo "PORT=8000" >> .env
```

## 📱 Extensión de Chrome

### Instalación Manual
1. Abre Chrome y ve a `chrome://extensions/`
2. Activa "Modo de desarrollador"
3. Haz clic en "Cargar extensión sin empaquetar"
4. Selecciona la carpeta `chrome_extension/`

### Desde Chrome Web Store
1. Busca "Gemini AI Futuristic Chatbot"
2. Haz clic en "Agregar a Chrome"
3. Confirma la instalación

## 🔐 Configuración de Seguridad

### HTTPS en Producción
```bash
# Usar certificados reales (Let's Encrypt)
certbot --nginx -d tu-dominio.com
```

### Firewall
```bash
# Permitir solo puertos necesarios
ufw allow 80
ufw allow 443
ufw enable
```

### Variables de Entorno Seguras
- Nunca commits archivos `.env`
- Usa servicios como HashiCorp Vault en producción
- Rota las API keys regularmente

## 📞 Soporte

- **Documentación**: [docs/](../docs/)
- **Issues**: [GitHub Issues](https://github.com/shaydev-create/Gemini-AI-Chatbot/issues)
- **Email**: support@gemini-ai.com

---

¡Listo! Tu instalación de Gemini AI Chatbot debería estar funcionando correctamente. 🎉