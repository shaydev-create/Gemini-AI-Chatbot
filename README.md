# 🚀 Gemini AI Chatbot - Versión 2025

Un chatbot inteligente potenciado por Google Gemini AI con interfaz web moderna y extensión de Chrome.

## ✨ Características

- 🤖 **IA Avanzada**: Integración con Google Gemini AI
- 🌐 **Interfaz Web**: Diseño moderno y responsivo
- 🔌 **Extensión Chrome**: Acceso rápido desde el navegador
- 🔒 **Seguro**: HTTPS, autenticación y validación
- 📱 **PWA**: Funciona como aplicación móvil
- 🐳 **Docker**: Despliegue fácil con contenedores

## 🚀 Inicio Rápido

### Opción 1: Docker (Recomendado)
```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/gemini-ai-chatbot.git
cd gemini-ai-chatbot

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu GEMINI_API_KEY

# Ejecutar con Docker
docker-compose up -d

# Acceder a http://localhost:5000
```

### Opción 2: Instalación Local
```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/gemini-ai-chatbot.git
cd gemini-ai-chatbot

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu GEMINI_API_KEY

# Ejecutar aplicación
python app/main.py
```

## 🔧 Configuración

### Variables de Entorno Requeridas
```env
GEMINI_API_KEY=tu_api_key_aqui
SECRET_KEY=tu_secret_key_seguro
FLASK_ENV=production
```

### Obtener API Key de Gemini
1. Ve a [Google AI Studio](https://aistudio.google.com/)
2. Crea una cuenta o inicia sesión
3. Genera una nueva API key
4. Copia la key a tu archivo `.env`

## 📁 Estructura del Proyecto

```
gemini-ai-chatbot/
├── 📱 app/                    # Aplicación principal
│   ├── api/                   # Rutas API
│   ├── core/                  # Funcionalidades core
│   ├── services/              # Servicios (Gemini AI)
│   ├── static/                # Archivos estáticos
│   ├── templates/             # Templates HTML
│   ├── utils/                 # Utilidades
│   └── main.py               # Punto de entrada
├── 🔧 config/                 # Configuraciones
├── 🌐 chrome_extension/       # Extensión de Chrome
├── 🐳 deployment/             # Docker y despliegue
├── 📚 docs/                   # Documentación
├── 🧪 tests/                  # Tests automatizados
├── .env                       # Variables de entorno
├── requirements.txt           # Dependencias Python
└── wsgi.py                   # WSGI para producción
```

## 🐳 Docker

### Desarrollo
```bash
# Ejecutar en modo desarrollo
docker-compose -f docker-compose.dev.yml up -d

# Ver logs
docker-compose logs -f app

# Detener servicios
docker-compose down
```

### Producción
```bash
# Ejecutar en modo producción
docker-compose up -d

# Con Nginx (recomendado)
docker-compose --profile nginx up -d
```

## 🌐 Extensión de Chrome

1. Abre Chrome y ve a `chrome://extensions/`
2. Activa "Modo de desarrollador"
3. Clic en "Cargar extensión sin empaquetar"
4. Selecciona la carpeta `chrome_extension/`
5. ¡Listo! El icono aparecerá en la barra de herramientas

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Tests específicos
pytest tests/unit/ -v
pytest tests/integration/ -v

# Con cobertura
pytest --cov=app tests/
```

## 📊 Monitoreo

### Health Check
```bash
curl http://localhost:5000/api/health
```

### Logs
```bash
# Ver logs en tiempo real
docker-compose logs -f app

# Logs específicos
tail -f logs/app_errors.log
```

## 🚀 Despliegue

### Vercel (Recomendado para Frontend)
```bash
# 1. Instalar Vercel CLI
npm i -g vercel

# 2. Login en Vercel
vercel login

# 3. Deployment automático
python deploy_vercel.py

# O manual:
vercel --prod
```

#### Configuración de Variables de Entorno en Vercel:
1. Ve a [Vercel Dashboard](https://vercel.com/dashboard)
2. Selecciona tu proyecto `gemini-ai-chatbot`
3. Ve a **Settings > Environment Variables**
4. Agrega estas variables:
   - `SECRET_KEY`: Tu clave secreta
   - `GOOGLE_API_KEY`: Tu API key de Gemini
   - `FLASK_ENV`: `production`
   - `FLASK_DEBUG`: `False`

### Heroku
```bash
# Instalar Heroku CLI
# Configurar variables de entorno en Heroku
heroku config:set GEMINI_API_KEY=tu_api_key

# Desplegar
git push heroku main
```

### VPS/Servidor
```bash
# Clonar en servidor
git clone https://github.com/tu-usuario/gemini-ai-chatbot.git

# Configurar con Docker
docker-compose --profile nginx up -d

# Configurar dominio y SSL
```

## 🔒 Seguridad

- ✅ HTTPS habilitado por defecto
- ✅ Validación de entrada
- ✅ Rate limiting
- ✅ Headers de seguridad
- ✅ Sanitización de datos

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🆘 Soporte

- 📧 Email: soporte@gemini-chatbot.com
- 🐛 Issues: [GitHub Issues](https://github.com/tu-usuario/gemini-ai-chatbot/issues)
- 📖 Docs: [Documentación Completa](./docs/)

## 🎯 Roadmap

- [ ] Migración a Vertex AI
- [ ] Soporte multiidioma
- [ ] Integración con bases de datos
- [ ] API REST completa
- [ ] Aplicación móvil nativa

---

⭐ **¡Dale una estrella si te gusta el proyecto!** ⭐