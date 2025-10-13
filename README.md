# Gemini AI Futuristic Chatbot - Versión 2025

Un chatbot de IA avanzado y seguro, potenciado por Google Gemini, con una interfaz web moderna, PWA y una extensión de Chrome.

[![Python Version](https://img.shields.io/badge/Python-3.13%2B-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-green.svg)](https://flask.palletsprojects.com/)
[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen.svg)](https://github.com/shaydev-create/Gemini-AI-Chatbot/actions)
[![Tests](https://img.shields.io/badge/Tests-100%25%20Passing-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/Coverage-82%25-green.svg)](reports/pytest_report.html)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](Dockerfile)
[![Security](https://img.shields.io/badge/Security-Hardened-red.svg)](SECURITY.md)
[![Vertex AI](https://img.shields.io/badge/Vertex%20AI-Ready-orange.svg)](docs/VERTEX_AI_MIGRATION_STEPS.md)

## 📋 Tabla de Contenidos

1.  [✨ Características Principales](#-características-principales)
2.  [🔧 Requisitos del Sistema](#-requisitos-del-sistema)
3.  [⚡ Inicio Rápido (Docker)](#-inicio-rápido-docker)
4.  [🚀 Desarrollo Local](#-desarrollo-local)
5.  [📂 Estructura del Proyecto](#-estructura-del-proyecto)
6.  [🔑 Configuración de API Keys](#-configuración-de-api-keys)
7.  [🧪 Pruebas](#-pruebas)
8.  [🐳 Docker](#-docker)
9.  [🤝 Contribuir](#-contribuir)
10. [📄 Licencia](#-licencia)

---

## ✨ Características Principales

- **🤖 Inteligencia Artificial Avanzada**: Integración nativa con **Google Gemini** y preparado para **Vertex AI** con sistema de fallback automático.
- **🌐 Interfaz Moderna y Accesible**: UI futurista y responsiva, con soporte PWA para instalación en escritorio/móvil y funcionamiento offline básico.
- **🔒 Seguridad Robusta**: Autenticación JWT, protección CSRF/XSS, cabeceras de seguridad, y rate limiting.
- **🐳 Dockerizado**: Entornos consistentes para desarrollo y producción con Docker Compose.
- **✅ Cobertura de Pruebas Sólida**: Más del 80% de cobertura de código para garantizar la estabilidad.
- **🌐 Extensión de Chrome**: Acceso rápido al chatbot directamente desde el navegador.
- **📊 Panel de Administración**: Métricas y estado del sistema en tiempo real (protegido por rol).
- **🌍 Multi-idioma**: Soporte para inglés y español, fácilmente extensible.

---

## 🔧 Requisitos del Sistema

- **Python**: 3.13 o superior.
- **Docker & Docker Compose**: Recomendado para un inicio rápido y sin complicaciones.
- **API Key de Google Gemini**: Necesaria para la funcionalidad del chatbot.

---

## ⚡ Inicio Rápido (Docker)

Este es el método recomendado para levantar el proyecto en menos de un minuto.

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/shaydev-create/Gemini-AI-Chatbot.git
    cd Gemini-AI-Chatbot
    ```

2.  **Configura tu API Key:**
    Crea un archivo `.env` en la raíz del proyecto y añade tu API key de Google Gemini.
    ```bash
    echo "GEMINI_API_KEY=tu_api_key_aqui" > .env
    ```

3.  **Levanta los contenedores:**
    ```bash
    docker-compose up -d
    ```

¡Listo! La aplicación estará disponible en `http://localhost:5000`.

---

## 🚀 Desarrollo Local

Si prefieres no usar Docker, sigue estos pasos:

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/shaydev-create/Gemini-AI-Chatbot.git
    cd Gemini-AI-Chatbot
    ```

2.  **Instala Poetry:**
    Si no tienes Poetry, instálalo siguiendo las [instrucciones oficiales](https://python-poetry.org/docs/#installation).

3.  **Configura el entorno y las dependencias:**
    Poetry creará un entorno virtual y instalará todo lo necesario.
    ```bash
    poetry install
    ```

4.  **Activa el entorno virtual de Poetry:**
    ```bash
    poetry shell
    ```

5.  **Configura el archivo `.env`:**
    Copia el archivo de ejemplo y añade tus credenciales.
    ```bash
    cp .env.example .env
    # Abre .env y edita las variables necesarias, como GEMINI_API_KEY.
    ```

6.  **Ejecuta la aplicación:**
    ```bash
    flask run
    ```
    La aplicación estará disponible en `http://localhost:5000`.

---

## 📂 Estructura del Proyecto

```
Gemini-AI-Chatbot/
├── app/                # Lógica principal de la aplicación Flask
│   ├── api/            # Endpoints de la API REST
│   ├── core/           # Lógica de negocio central (seguridad, caché)
│   ├── services/       # Integraciones con servicios externos (Gemini)
│   ├── static/         # Archivos estáticos (CSS, JS, imágenes)
│   └── templates/      # Plantillas HTML (Jinja2)
├── src/                # Módulos Python reutilizables y de bajo nivel
│   ├── config/         # Configuración de servicios (Vertex AI)
│   ├── models/         # Modelos de datos (SQLAlchemy)
│   └── auth.py         # Lógica de autenticación
├── chrome_extension/   # Código fuente de la extensión de Chrome
├── docs/               # Documentación adicional del proyecto
├── instance/           # Archivos de instancia (BD, logs, etc.), ignorado por Git
├── reports/            # Reportes de pruebas, cobertura y seguridad
├── scripts/            # Scripts de utilidad (limpieza, chequeos)
├── tests/              # Pruebas unitarias, de integración y E2E
├── .gitignore          # Archivos y carpetas ignorados por Git
├── app.py              # Punto de entrada principal de la aplicación
├── Dockerfile          # Define la imagen Docker de la aplicación
└── docker-compose.yml  # Orquesta los servicios para desarrollo
```

---

## 🔑 Configuración de API Keys

### Google Gemini API

1.  Ve a **[Google AI Studio](https://aistudio.google.com/)**.
2.  Inicia sesión y genera una nueva API key.
3.  Añade la clave a tu archivo `.env`:
    ```
    GEMINI_API_KEY=tu_clave_aqui
    ```

### Vertex AI (Opcional, para producción)

Para un entorno de producción con mayores límites y fiabilidad, se recomienda usar Vertex AI. La configuración es más extensa y está documentada en `docs/VERTEX_AI_MIGRATION_STEPS.md`.

---

## 🧪 Pruebas

El proyecto tiene una suite de pruebas robusta para garantizar la calidad del código.

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar pruebas y generar un reporte de cobertura
pytest --cov=src --cov=app --html=reports/pytest_report.html

# Ver el reporte de cobertura (abre el archivo en tu navegador)
reports/pytest_report.html
```
El proyecto está configurado con varias tareas de VS Code para ejecutar pruebas, linting y formateo de código.

---

## 🐳 Docker

-   **`docker-compose.yml`**: Configuración para el entorno de **desarrollo**. Incluye el servidor de Flask con recarga automática.
-   **`docker-compose.prod.yml`**: Configuración optimizada para **producción**. Utiliza Gunicorn como servidor WSGI para mayor rendimiento.
-   **`Dockerfile`**: Imagen base multi-etapa para mantener la imagen final ligera y segura.

**Comandos útiles:**
```bash
# Levantar entorno de desarrollo
docker-compose up -d

# Detener entorno
docker-compose down

# Levantar entorno de producción
docker-compose -f docker-compose.prod.yml up -d

# Reconstruir una imagen específica
docker-compose build app
```

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor, sigue estos pasos:

1.  Haz un **Fork** de este repositorio.
2.  Crea una nueva rama (`git checkout -b feature/nueva-funcionalidad`).
3.  Realiza tus cambios y haz commit (`git commit -m 'Añade nueva funcionalidad'`).
4.  Asegúrate de que todas las pruebas pasen.
5.  Envía tus cambios (`git push origin feature/nueva-funcionalidad`).
6.  Abre un **Pull Request**.

---

## 📄 Licencia

Este proyecto está bajo la **Licencia MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.
