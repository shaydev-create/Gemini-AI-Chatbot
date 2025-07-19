# Gemini AI Chatbot

Un chatbot moderno y eficiente construido con Flask y Google Gemini AI, diseñado con una arquitectura modular y escalable.

## 🚀 Características

- **Interfaz moderna**: UI responsiva y atractiva con soporte PWA
- **Integración Gemini AI**: Respuestas inteligentes usando Google Gemini
- **Arquitectura modular**: Código organizado y mantenible
- **Sistema de caché**: Optimización de rendimiento con caché inteligente
- **Rate limiting**: Protección contra abuso de API
- **Métricas de rendimiento**: Monitoreo en tiempo real
- **Seguridad robusta**: Headers de seguridad y validaciones
- **Soporte SSL/HTTPS**: Configuración flexible para desarrollo y producción
- **Testing completo**: Tests unitarios, de integración y e2e
- **Docker ready**: Configuración para contenedores

## 📁 Estructura del Proyecto

```
gemini-chatbot/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Punto de entrada principal
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py           # Rutas API
│   ├── core/
│   │   ├── __init__.py
│   │   ├── application.py      # Factory de aplicación
│   │   ├── cache.py           # Sistema de caché
│   │   ├── decorators.py      # Decoradores (rate limiting)
│   │   └── metrics.py         # Métricas de rendimiento
│   ├── services/
│   │   ├── __init__.py
│   │   └── gemini_service.py  # Integración con Gemini AI
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── helpers.py         # Funciones auxiliares
│   │   └── validators.py      # Validadores
│   ├── static/               # Archivos estáticos (CSS, JS, imágenes)
│   └── templates/            # Templates HTML
├── config/
│   ├── __init__.py
│   ├── settings.py           # Configuraciones
│   └── database.py          # Configuración de base de datos
├── tests/
│   ├── unit/                # Tests unitarios
│   ├── integration/         # Tests de integración
│   └── e2e/                # Tests end-to-end
├── docker-compose.dev.yml   # Docker para desarrollo
├── requirements.txt         # Dependencias Python
├── .env.dev                # Variables de entorno - desarrollo
├── .env.prod               # Variables de entorno - producción
├── .env.test               # Variables de entorno - testing
└── app.py                  # Compatibilidad con estructura anterior
```

## 🛠️ Instalación

### Requisitos Previos

- Python 3.8+
- pip
- Git

### Instalación Local

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd gemini-chatbot
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   ```bash
   # Copiar archivo de configuración
   cp .env.dev .env
   
   # Editar .env con tus configuraciones
   # Especialmente GEMINI_API_KEY
   ```

5. **Ejecutar la aplicación**
   ```bash
   python app/main.py
   ```

### Instalación con Docker

1. **Desarrollo con Docker Compose**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

2. **Acceder a la aplicación**
   - Aplicación: http://localhost:5000
   - Adminer (DB): http://localhost:8080
   - Redis Commander: http://localhost:8081

## ⚙️ Configuración

### Variables de Entorno Principales

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Clave API de Google Gemini | `your_api_key_here` |
| `SECRET_KEY` | Clave secreta de Flask | `your_secret_key` |
| `DATABASE_URL` | URL de base de datos | `postgresql://user:pass@host:port/db` |
| `REDIS_URL` | URL de Redis | `redis://localhost:6379/0` |
| `USE_HTTPS` | Habilitar HTTPS | `true/false` |

### Configuración de Gemini AI

1. Obtener API key de [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Configurar en `.env`:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

## 🧪 Testing

### Ejecutar Tests

```bash
# Tests unitarios
python -m pytest tests/unit/ -v

# Tests de integración
python -m pytest tests/integration/ -v

# Tests e2e (requiere Selenium)
python -m pytest tests/e2e/ -v

# Todos los tests
python -m pytest tests/ -v

# Con coverage
python -m pytest tests/ --cov=app --cov-report=html
```

### Configuración de Tests E2E

Para tests end-to-end, instalar ChromeDriver:

```bash
# Windows (con Chocolatey)
choco install chromedriver

# Linux
sudo apt-get install chromium-chromedriver

# Mac (con Homebrew)
brew install chromedriver
```

## 📊 Monitoreo y Métricas

La aplicación incluye métricas de rendimiento accesibles en:

- **Health Check**: `/api/health`
- **Métricas**: `/api/metrics`

Métricas disponibles:
- Tiempo de actividad
- Contadores de requests
- Tiempos de respuesta
- Requests por minuto
- Estado de servicios externos

## 🔒 Seguridad

### Características de Seguridad

- **Rate Limiting**: Protección contra spam y abuso
- **Input Validation**: Validación y sanitización de entradas
- **Security Headers**: CSP, HSTS, X-Frame-Options
- **JWT Authentication**: Tokens seguros para autenticación
- **HTTPS Support**: Configuración SSL/TLS

### Configuración de Producción

Para producción, asegurar:

1. **Variables de entorno seguras**
   ```bash
   SECRET_KEY=<clave-aleatoria-segura>
   JWT_SECRET_KEY=<clave-jwt-segura>
   USE_HTTPS=true
   ```

2. **Base de datos segura**
   ```bash
   DATABASE_URL=postgresql://user:secure_password@host:port/db
   ```

3. **Configuración SSL**
   ```bash
   SSL_CERT_PATH=/path/to/cert.pem
   SSL_KEY_PATH=/path/to/key.pem
   ```

## 🚀 Despliegue

### Despliegue en Producción

1. **Configurar variables de entorno de producción**
   ```bash
   cp .env.prod .env
   # Editar con valores reales
   ```

2. **Configurar base de datos**
   ```bash
   python -c "from config.database import init_db; init_db()"
   ```

3. **Ejecutar con servidor WSGI**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 app.main:app
   ```

### Despliegue con Docker

```bash
# Construir imagen
docker build -t gemini-chatbot .

# Ejecutar contenedor
docker run -d -p 80:5000 --env-file .env.prod gemini-chatbot
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit cambios (`git commit -am 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crear Pull Request

### Estándares de Código

- Seguir PEP 8
- Documentar funciones y clases
- Escribir tests para nuevas características
- Mantener cobertura de tests > 80%

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🆘 Soporte

- **Issues**: [GitHub Issues](link-to-issues)
- **Documentación**: [Wiki del proyecto](link-to-wiki)
- **Email**: support@example.com

## 🔄 Changelog

### v2.0.0 (Actual)
- ✨ Arquitectura modular completa
- ✨ Sistema de caché mejorado
- ✨ Métricas de rendimiento
- ✨ Tests completos (unitarios, integración, e2e)
- ✨ Soporte Docker
- ✨ Configuración por entornos

### v1.0.0
- 🎉 Versión inicial
- 🤖 Integración básica con Gemini AI
- 🌐 Interfaz web básica

## 🙏 Agradecimientos

- Google por la API de Gemini AI
- Comunidad Flask por el excelente framework
- Contribuidores del proyecto

---

**¡Disfruta construyendo con Gemini AI! 🚀**