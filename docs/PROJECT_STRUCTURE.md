#  Estructura del Proyecto - Gemini AI Chatbot

##  Arquitectura General

```
# Estructura del Proyecto - Gemini AI Chatbot (v2)

## Arquitectura General con Poetry y Docker

```
Gemini-AI-Chatbot/
├── app/                     # Lógica principal de la aplicación Flask
│   ├── __init__.py          # Inicializa el paquete de la aplicación
│   ├── api/                 # Endpoints de la API RESTful
│   ├── auth/                # Autenticación y gestión de usuarios
│   ├── core/                # Lógica de negocio central (seguridad, caché)
│   ├── main/                # Rutas principales y manejo de errores
│   ├── models.py            # Modelos de datos (SQLAlchemy)
│   ├── services/            # Integraciones con servicios externos (Gemini, DB)
│   ├── static/              # Archivos estáticos (CSS, JS, imágenes, PWA)
│   └── templates/           # Plantillas HTML (Jinja2)
├── chrome_extension/        # Código fuente de la extensión de Chrome
├── docs/                    # Documentación del proyecto
├── instance/                # Archivos de instancia (BD, logs), ignorado por Git
├── reports/                 # Reportes de pruebas, cobertura y seguridad
├── scripts/                 # Scripts de utilidad (limpieza, chequeos)
├── tests/                   # Pruebas unitarias y de integración
├── .dockerignore            # Archivos ignorados por Docker
├── .env.example             # Plantilla para variables de entorno
├── .gitignore               # Archivos y carpetas ignorados por Git
├── app.py                   # Punto de entrada de la aplicación Flask
├── docker-compose.dev.yml   # Orquestación Docker para desarrollo
├── docker-compose.prod.yml  # Orquestación Docker para producción
├── docker-compose.yml       # Configuración base de Docker Compose
├── Dockerfile               # Define la imagen Docker multi-etapa
├── poetry.lock              # Lockfile de dependencias de Poetry
└── pyproject.toml           # Configuración del proyecto y dependencias (Poetry)
```

## Componentes Principales

### Aplicación Flask (`app/`)
- **`__init__.py`**: Crea y configura la instancia de la aplicación Flask (App Factory).
- **`api/`**: Endpoints REST para la comunicación con el frontend y la extensión.
- **`auth/`**: Manejo de registro, login, y sesiones de usuario con JWT.
- **`core/`**: Lógica de negocio, como el `SecurityManager` y la gestión de la caché.
- **`main/`**: Rutas principales de la aplicación web y manejo de errores globales.
- **`models.py`**: Define las tablas de la base de datos usando SQLAlchemy.
- **`services/`**: Abstracciones para interactuar con la API de Gemini y la base de datos.
- **`static/`**: Recursos web como CSS, JavaScript, imágenes, y los archivos para la PWA (`manifest.json`, `sw.js`).
- **`templates/`**: Plantillas HTML renderizadas por el servidor con Jinja2.

### Configuración y Dependencias
- **`pyproject.toml`**: Archivo central que define el proyecto, sus dependencias (producción y desarrollo), y la configuración de herramientas como `pytest`, `ruff`, y `mypy`. Reemplaza `requirements.txt` y `setup.py`.
- **`poetry.lock`**: Archivo autogenerado que asegura instalaciones determinísticas de las dependencias.
- **`.env.example`**: Plantilla que documenta todas las variables de entorno necesarias para correr la aplicación.

### Contenerización (`Dockerfile`, `docker-compose.*.yml`)
- **`Dockerfile`**: Utiliza una construcción multi-etapa para crear una imagen de producción ligera y segura, usando Poetry para instalar dependencias.
- **`docker-compose.yml`**: Define los servicios base (app, db, redis).
- **`docker-compose.dev.yml`**: Extiende la base para desarrollo, montando el código fuente para live-reloading.
- **`docker-compose.prod.yml`**: Extiende la base para producción, añadiendo Nginx como reverse proxy y usando Gunicorn como servidor WSGI.

### Testing (`tests/`)
- **`conftest.py`**: Fixtures y configuración global para `pytest`.
- El directorio contiene pruebas unitarias y de integración, organizadas por funcionalidad.

### Despliegue y CI/CD
- **`deployment/`**: Scripts y configuraciones para el despliegue (ej. `gunicorn.conf.py`).
- **`.github/workflows/`**: Pipelines de GitHub Actions para integración continua, pruebas y despliegue.

## Flujo de Datos

1.  **Usuario** interactúa con la Interfaz Web (PWA) o la Extensión de Chrome.
2.  **Frontend** (JS en `static/` o `chrome_extension/`) envía peticiones a la **API Flask** (`app/api/`).
3.  La **API** procesa la petición, usando `auth/` para verificar la identidad y `services/` para la lógica de negocio.
4.  **`services/`** se comunica con la API de **Google Gemini** y/o la base de datos (`models.py`).
5.  La respuesta se devuelve al frontend y se presenta al usuario.

## Tecnologías Utilizadas

- **Backend**: Flask, Python 3.11+
- **Gestor de Dependencias**: Poetry
- **Servidor WSGI**: Gunicorn con workers `gevent`
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **AI**: Google Gemini API
- **Base de datos**: PostgreSQL
- **Caché**: Redis
- **Contenerización**: Docker, Docker Compose
- **Proxy Inverso**: Nginx
- **Testing**: pytest
- **Calidad de Código**: Ruff, Black, MyPy

---

*Última actualización: Octubre 2025*
```

##  Componentes Principales

###  Aplicación Flask (`app/`)
- **main.py**: Punto de entrada principal
- **api/**: Endpoints REST y autenticación
- **core/**: Núcleo de la aplicación con caché y métricas
- **services/**: Lógica de negocio (Gemini AI, multimodal)
- **static/**: Recursos web (CSS, JS, imágenes)
- **templates/**: Plantillas HTML Jinja2

###  Configuración (`config/`)
- **settings.py**: Configuraciones generales
- **database.py**: Configuración de base de datos
- **ssl_config.py**: Configuración SSL/HTTPS

###  Seguridad (`src/`, `core/`)
- **auth.py**: Sistema de autenticación
- **security.py**: Funciones de seguridad
- **security_manager.py**: Coordinación de seguridad

###  Testing (`tests/`)
- **unit/**: Pruebas unitarias
- **integration/**: Pruebas de integración
- **e2e/**: Pruebas end-to-end

###  Despliegue (`deployment/`)
- **Dockerfile**: Imagen Docker optimizada
- **docker-compose.yml**: Orquestación con Nginx
- **deploy.sh**: Script de despliegue automatizado

###  Extensión Chrome (`chrome_extension/`)
- **manifest.json**: Configuración de la extensión
- **popup.html/js**: Interfaz de usuario
- **background.js**: Lógica de fondo

##  Flujo de Datos

1. **Usuario**  Interfaz web o extensión Chrome
2. **Frontend**  API Flask (`app/api/`)
3. **API**  Servicios (`app/services/`)
4. **Servicios**  Gemini AI / Vertex AI
5. **Respuesta**  Usuario (tiempo real)

##  Tecnologías Utilizadas

- **Backend**: Flask, Python 3.8+
- **Frontend**: HTML5, CSS3, JavaScript ES6+
- **AI**: Google Gemini API / Vertex AI
- **Base de datos**: SQLite (desarrollo), PostgreSQL (producción)
- **Caché**: Redis (opcional)
- **Contenedores**: Docker, Docker Compose
- **Proxy**: Nginx
- **Testing**: pytest, Selenium
- **CI/CD**: GitHub Actions

##  Escalabilidad

La arquitectura está diseñada para escalar:
- **Horizontal**: Múltiples instancias con load balancer
- **Vertical**: Optimización de recursos por contenedor
- **Microservicios**: Separación de servicios por funcionalidad
- **CDN**: Distribución de contenido estático

---

*Última actualización: Septiembre 2025*
