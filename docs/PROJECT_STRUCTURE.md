#  Estructura del Proyecto - Gemini AI Chatbot

##  Arquitectura General

```
Gemini-AI-Chatbot/
  app.py                     # Aplicación principal Flask
  requirements.txt           # Dependencias Python
  requirements-dev.txt       # Dependencias de desarrollo
  requirements-minimal.txt   # Dependencias mínimas
  pytest.ini               # Configuración de tests
  pyproject.toml            # Configuración del proyecto
  .gitignore                # Archivos ignorados por Git
  .env.example              # Ejemplo de variables de entorno
  setup.py                  # Configuración de instalación

  app/                       # Aplicación Flask principal
     __init__.py
     main.py               # Punto de entrada principal
     api/                  # Endpoints de API
        __init__.py
        auth.py           # Autenticación API
        admin.py          # Rutas de administración
        routes.py         # Rutas principales
     core/                 # Núcleo de la aplicación
        __init__.py
        application.py    # Configuración de la app
        cache.py          # Sistema de caché
        decorators.py     # Decoradores personalizados
        metrics.py        # Métricas y monitoreo
        middleware.py     # Middleware personalizado
     services/             # Servicios de negocio
        __init__.py
        gemini_service.py # Servicio de Gemini AI
        multimodal_service.py # Servicio multimodal
        conversation_memory.py # Memoria de conversaciones
     static/               # Archivos estáticos
        css/              # Hojas de estilo
        js/               # JavaScript
        images/           # Imágenes
        icons/            # Iconos
        manifest.json     # Manifiesto PWA
        sw.js             # Service Worker
        favicon.ico       # Favicon
     templates/            # Plantillas HTML
        chat.html         # Interfaz de chat
        index.html        # Página principal
        admin.html        # Panel de administración
        auth/             # Plantillas de autenticación
        errors/           # Páginas de error
        privacy_policy.html # Política de privacidad
        terms_of_service.html # Términos de servicio
     utils/                # Utilidades
        __init__.py
        helpers.py        # Funciones auxiliares
        i18n.py           # Internacionalización
        validators.py     # Validadores
     i18n/                 # Archivos de idiomas
         en.json          # Inglés
         es.json          # Español

  src/                       # Código fuente adicional
     __init__.py
     auth.py               # Sistema de autenticación
     models.py            # Modelos de base de datos
     security.py          # Funciones de seguridad

  core/                      # Coordinación de seguridad
     __init__.py
     security_manager.py  # Gestor de seguridad

  config/                    # Configuraciones
     __init__.py
     database.py          # Configuración de BD
     settings.py          # Configuraciones generales
     ssl_config.py        # Configuración SSL

  data/                      # Datos de la aplicación
     __init__.py

  scripts/                   # Scripts de utilidad
     README.md
     __init__.py
     check_exposed_credentials.py # Verificar credenciales
     cleanup.py            # Limpieza del proyecto
     create_chrome_icons.py # Crear iconos de Chrome
     final_check.py        # Verificación final
     init_db.py            # Inicializar base de datos
     launch_readiness_check.py # Verificar preparación
     maintenance.py        # Mantenimiento
     migrate_to_vertex_ai.py # Migración a Vertex AI
     monitor.py            # Monitoreo del sistema
     package_chrome_extension.py # Empaquetar extensión
     prepare_chrome_store.py # Preparar Chrome Store
     secure_env.py         # Asegurar variables de entorno
     security_check.py     # Verificación de seguridad
     setup_api_keys.py     # Configurar API keys
     test_chat_functionality.py # Probar funcionalidad

  tests/                     # Pruebas automatizadas
     README.md
     __init__.py
     conftest.py           # Configuración de pytest
     test_basic.py         # Pruebas básicas
     test_main.py          # Pruebas principales
     test_routes.py        # Pruebas de rutas
     test_version.py       # Pruebas de versión
     unit/                 # Pruebas unitarias
        __init__.py
        test_application.py # Pruebas de aplicación
        test_basic.py     # Pruebas básicas unitarias
        test_gemini_service.py # Pruebas de Gemini
        test_security.py  # Pruebas de seguridad
        test_utils.py     # Pruebas de utilidades
     integration/          # Pruebas de integración
        __init__.py
        test_api.py       # Pruebas de API
        test_integration.py # Pruebas de integración
     e2e/                  # Pruebas end-to-end
         README.md
         __init__.py
         package.json      # Dependencias Node.js
         package-lock.json # Lock de dependencias
         test_e2e.py       # Pruebas E2E

  chrome_extension/          # Extensión de Chrome
     manifest.json         # Manifiesto de la extensión
     background.js         # Script de fondo
     content.js            # Script de contenido
     popup.html            # Popup de la extensión
     popup.js              # JavaScript del popup
     index.html            # Página principal
     privacy_policy.html   # Política de privacidad
     icons/                # Iconos de la extensión
         icon_16.png       # Icono 16x16
         icon_48.png       # Icono 48x48
         icon_128.png      # Icono 128x128

  deployment/                # Archivos de despliegue
     Dockerfile            # Imagen Docker
     docker-compose.yml    # Orquestación Docker
     deploy.sh             # Script de despliegue
     gunicorn.conf.py      # Configuración Gunicorn

  docker/                    # Configuraciones Docker
     nginx.conf            # Configuración Nginx

  monitoring/                # Monitoreo
     prometheus.yml        # Configuración Prometheus

  docs/                      # Documentación
     index.md              # Índice de documentación
     _config.yml           # Configuración Jekyll
     LICENSE               # Licencia del proyecto
     API_DOCUMENTATION.md  # Documentación de API
     API_MIGRATION_SPECIFIC.md # Migración de API
     CHROME_STORE_PRIVACY_SETUP.md # Configuración Chrome
     CONTRIBUTING.md       # Guía de contribución
     DEPENDENCIAS_MAGIC.md # Dependencias mágicas
     MANTENIMIENTO_CODIGO.md # Mantenimiento de código
     PRIVACY_POLICY.md     # Política de privacidad
     PROJECT_STRUCTURE.md  # Este archivo
     PYTHON_3_13_COMPATIBILIDAD.md # Compatibilidad Python
     SEGURIDAD_CREDENCIALES.md # Seguridad de credenciales
     SYSTEM_ANALYSIS.md    # Análisis del sistema
     SYSTEM_DOCUMENTATION.md # Documentación completa
     USER_GUIDE.md         # Guía de usuario
     VERTEX_AI_MIGRATION_STEPS.md # Migración Vertex AI

  .github/                   # Configuración GitHub
     workflows/            # GitHub Actions
         ci-cd.yml         # CI/CD Pipeline
         github-pages.yml  # GitHub Pages

  docker-compose.dev.yml    # Docker para desarrollo
  docker-compose.prod.yml   # Docker para producción
  chrome_extension.crx       # Extensión empaquetada
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
