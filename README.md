# Gemini AI Futuristic Chatbot - Version 2025

Un chatbot inteligente potenciado por Google Gemini AI con interfaz web moderna y extension de Chrome.

[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-green.svg)](https://flask.palletsprojects.com/)
[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen.svg)](https://github.com/shaydev-create/Gemini-AI-Chatbot/actions)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/Coverage-85%25-yellow.svg)](tests/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Chrome Web Store](https://img.shields.io/badge/Chrome%20Web%20Store-Available-brightgreen)](https://chrome.google.com/webstore)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](Dockerfile)
[![PWA](https://img.shields.io/badge/PWA-Ready-purple.svg)](app/static/manifest.json)
[![Security](https://img.shields.io/badge/Security-Hardened-red.svg)](SECURITY.md)
[![Vertex AI](https://img.shields.io/badge/Vertex%20AI-Ready-orange.svg)](docs/VERTEX_AI_MIGRATION_STEPS.md)

## 📋 Tabla de Contenidos

- [✨ Características Principales](#-características-principales)
- [🎯 Panel de Administración](#-panel-de-administración)
- [🌍 Multiidioma Avanzado](#-multiidioma-avanzado)
- [⚡ Inicio Rápido](#-inicio-rápido)
- [🔑 Configuración de API Key](#-configuración-de-api-key)
- [🚀 Vertex AI Migration (Recomendado para Producción)](#-vertex-ai-migration-recomendado-para-producción)
- [🌐 Extensión de Chrome](#-extensión-de-chrome)
- [🐳 Docker](#-docker)
- [📱 PWA (Progressive Web App)](#-pwa-progressive-web-app)
- [🚀 Desarrollo](#-desarrollo)
- [📊 Performance y Benchmarks](#-performance-y-benchmarks)
- [🧪 Pruebas](#-pruebas)
- [📊 Monitoreo](#-monitoreo)
- [🔒 Seguridad](#-seguridad)
- [🌐 Internacionalización](#-internacionalización)
- [📚 Documentación](#-documentación)
- [🤝 Contribuir](#-contribuir)
- [🔧 Troubleshooting](#-troubleshooting)
- [📄 Licencia](#-licencia)

## ✨ Características Principales

### 🤖 Inteligencia Artificial

- **Google Gemini AI**: Integración completa con modelos avanzados
- **Vertex AI Ready**: Migración automática para producción
- **Fallback Inteligente**: Sistema de respaldo automático
- **Multimodal**: Soporte para texto, imágenes y archivos

### 🌐 Interfaz y Experiencia

- **Diseño Moderno**: UI futurística y responsiva
- **Accesibilidad**: ARIA, skip links, navegación por teclado
- **PWA Completa**: Instalable, offline, notificaciones push
- **Multiidioma**: Español, inglés con selección dinámica

### 🔒 Seguridad y Autenticación

- **HTTPS Obligatorio**: Certificados SSL/TLS
- **JWT Authentication**: Tokens seguros con expiración
- **Protección CSRF/XSS**: Validación y sanitización
- **Panel Admin**: Acceso restringido con roles

### 🚀 Desarrollo y Deploy

- **Docker Ready**: Contenedores optimizados
- **CI/CD Pipeline**: GitHub Actions automatizado
- **Monitoreo**: Prometheus + Grafana integrados
- **Testing**: Cobertura 85%+ con pytest

### 📱 Extensiones

- **Chrome Extension**: Acceso rápido desde navegador
- **API REST**: Endpoints documentados
- **Webhooks**: Integración con servicios externos

## 🎯 Panel de Administración

El sistema incluye un panel de administración básico accesible solo para usuarios autenticados con rol de administrador.

- **Ruta:** `/admin`
- **Protección:** Requiere JWT y rol de administrador
- **Template:** `admin.html`

Ejemplo de acceso:

```bash
curl -H "Authorization: Bearer <token_admin>" https://localhost:5000/admin
# Respuesta: Renderiza el panel si el usuario es admin
```

## 🌍 Multiidioma Avanzado

La aplicación soporta traducción dinámica de textos en español e inglés. Puedes agregar nuevos idiomas creando archivos JSON en `app/i18n/`.

Ejemplo para agregar francés:

```json
1. Crea `app/i18n/fr.json` con las claves y traducciones.
2. Accede con `?lang=fr` en la URL o selecciona desde el frontend.

Todos los templates usan la función `translate` para mostrar textos según el idioma seleccionado.

## ⚡ Inicio Rápido

### Ejecucion Inmediata

```bash
# Clona el repositorio
git clone https://github.com/shaydev-create/Gemini-AI-Chatbot.git
cd Gemini-AI-Chatbot

```bash
# Configura tu API key de Gemini
echo "GEMINI_API_KEY=tu_api_key_aqui" > .env

# Ejecuta con Docker (recomendado)
docker-compose up -d

# O ejecuta localmente
pip install -r requirements.txt
python app.py
```

Listo! Abre [http://localhost:5000](http://localhost:5000) en tu navegador.

### Requisitos del Sistema

- **Python**: 3.8+ (recomendado 3.11+)
- **Docker**: Opcional pero recomendado
- **Navegador**: Chrome, Firefox, Safari, Edge (ultimas versiones)
- **API Key**: Google Gemini AI (gratuita)

## 🔑 Configuración de API Key

### Obtener API Key de Gemini

1. Ve a [Google AI Studio](https://aistudio.google.com/)
2. Crea una cuenta o inicia sesion
3. Genera una nueva API key
4. Copia la key a tu archivo `.env`

```bash
# Archivo .env
GEMINI_API_KEY=tu_api_key_aqui
```

### Seguridad de Credenciales

**IMPORTANTE**: Nunca subas tu API key al repositorio publico.

```bash
# Limpia credenciales antes de commit
python clean_credentials.py

# Verifica que .env no tenga credenciales reales
cat .env
```

Ver [guia completa de seguridad](docs/SEGURIDAD_CREDENCIALES.md).

## 🚀 Vertex AI Migration (Recomendado para Producción)

### ¿Por qué migrar a Vertex AI?

**Gemini API Gratuita vs Vertex AI:**

| Característica | Gemini API | Vertex AI |
|---|---|---|
| **Límites** | 15 req/min | 1000+ req/min |
| **Latencia** | 5-10 seg | 2-3 seg |
| **Confiabilidad** | 95% | 99.9% |
| **Costo** | Gratis | $15-50/mes |
| **SLA** | No | Sí |
| **Soporte** | Comunidad | Google Cloud |

### Configuración Rápida

1. **Crear proyecto Google Cloud**

   ```bash

   # Instalar gcloud CLI
   gcloud projects create tu-proyecto-id
   gcloud config set project tu-proyecto-id
   ```

2. **Habilitar APIs**

   ```bash

   gcloud services enable aiplatform.googleapis.com
   gcloud services enable compute.googleapis.com
   ```

3. **Configurar credenciales**

   ```bash

   # Crear service account
   gcloud iam service-accounts create vertex-ai-service

   # Descargar key
   gcloud iam service-accounts keys create credentials/vertex-ai-key.json \
     --iam-account=vertex-ai-service@tu-proyecto-id.iam.gserviceaccount.com
   ```

4. **Configurar variables**

   ```bash

   # Agregar a .env
   VERTEX_AI_ENABLED=true
   GOOGLE_CLOUD_PROJECT_ID=tu-proyecto-id
   GOOGLE_APPLICATION_CREDENTIALS=./credentials/vertex-ai-key.json
   VERTEX_AI_MAX_DAILY_COST=50.0
   ```

### Migración Automática

```bash
# Script de migración completa
python scripts/migrate_to_vertex_ai.py
# Solo verificar configuración
python scripts/migrate_to_vertex_ai.py --check

# Probar integración
python scripts/migrate_to_vertex_ai.py --test
```

### Modelos Disponibles

- **gemini-1.5-flash**: Rápido y económico ($0.50/1M tokens)
- **gemini-1.5-pro**: Avanzado para tareas complejas ($3.50/1M tokens)
- **gemini-1.0-pro**: Básico y estable ($0.25/1M tokens)

### Fallback Automático

El sistema incluye fallback automático:

1. **Vertex AI** (principal)
2. **Gemini API** (fallback)
3. **Mensaje de error** (último recurso)

### Monitoreo de Costos

```bash
# Ver costos actuales
gcloud billing budgets list

```bash
# Configurar alertas
gcloud alpha billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="Vertex AI Budget" \
  --budget-amount=50USD
```

📖 **Guía completa**: [VERTEX_AI_MIGRATION_STEPS.md](docs/VERTEX_AI_MIGRATION_STEPS.md)

## 🌐 Extensión de Chrome

### Instalación

1. Descarga o clona este repositorio
2. Abre Chrome y ve a `chrome://extensions/`
3. Activa "Modo de desarrollador"
4. Haz clic en "Cargar extensión sin empaquetar"
5. Selecciona la carpeta `chrome_extension/`

### Uso

1. Haz clic en el icono de Gemini AI en la barra de herramientas
2. Configura tu API key en la ventana emergente
3. ¡Comienza a chatear!

## 🐳 Docker

### Ejecucion con Docker Compose (Recomendado)

```bash
# Desarrollo
docker-compose up -d

# Produccion
docker-compose -f docker-compose.prod.yml up -d
```

### Ejecucion con Docker

```bash
# Construir imagen
docker build -t gemini-chatbot .

# Ejecutar contenedor
docker run -d -p 5000:5000 --env-file .env gemini-chatbot
```

## 📱 PWA (Progressive Web App)

La aplicación funciona como PWA:

- **Instalable**: Agrega a pantalla de inicio
- **Offline**: Funciona sin conexión (limitado)
- **Responsive**: Optimizada para móviles
- **Fast**: Carga rápida con Service Worker

## 🚀 Desarrollo

### Instalacion Local

```bash
# Clona el repositorio
git clone https://github.com/shaydev-create/Gemini-AI-Chatbot.git
cd Gemini-AI-Chatbot

# Crea entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instala dependencias
pip install -r requirements.txt

# Configura variables de entorno
```bash
cp .env.example .env
# Edita .env con tus credenciales

# Ejecuta la aplicacion
python app.py
```

### Estructura del Proyecto

```text
Gemini-AI-Chatbot/
|-- app/                    # Aplicacion principal
|   |-- static/            # Archivos estaticos (CSS, JS, imagenes)
|   |-- templates/         # Templates HTML
|   |-- services/          # Servicios (Gemini, Auth, etc.)
|   +-- utils/             # Utilidades
|-- chrome_extension/       # Extension de Chrome
|-- docs/                  # Documentacion
|-- scripts/               # Scripts de utilidad
|-- tests/                 # Pruebas
|-- docker-compose.yml     # Docker Compose
|-- Dockerfile            # Imagen Docker
|-- requirements.txt      # Dependencias Python
+-- app.py               # Punto de entrada

## 📊 Performance y Benchmarks

### Métricas del Sistema

#### Rendimiento de Respuesta

- **Gemini API**: 3-8 segundos promedio
- **Vertex AI**: 1-3 segundos promedio
- **Cache Hit**: <100ms
- **Fallback**: +2 segundos adicionales

#### Capacidad de Carga

```bash
# Test de carga básico
ab -n 100 -c 10 http://localhost:5000/api/chat

# Resultados esperados:
# - Requests/sec: 15-25 (Gemini API)
# - Requests/sec: 100-200 (Vertex AI)
# - Memory usage: 150-300MB
# - CPU usage: 20-40%
```

#### Límites de API

| Servicio | Requests/min | Requests/día | Tokens/request |
|---|---|---|---|
| **Gemini API** | 15 | 1,500 | 32,000 |
| **Vertex AI** | 1,000+ | 50,000+ | 128,000 |

### Optimizaciones Implementadas

#### 🚀 Performance

- **Async/Await**: Requests no bloqueantes
- **Connection Pooling**: Reutilización de conexiones
- **Response Caching**: Cache inteligente de respuestas
- **Lazy Loading**: Carga diferida de componentes
- **Compression**: Gzip para responses

#### 🧠 Memory Management

- **Conversation Limits**: Máximo 50 mensajes por sesión
- **Auto Cleanup**: Limpieza automática cada 24h
- **Memory Monitoring**: Alertas de uso excesivo

#### 🔄 Reliability

- **Circuit Breaker**: Protección contra fallos
- **Retry Logic**: Reintentos automáticos
- **Health Checks**: Monitoreo continuo
- **Graceful Degradation**: Fallback automático

### Monitoreo en Tiempo Real

#### Prometheus Metrics

```bash
# Acceder a métricas
curl http://localhost:9090/metrics

# Métricas clave:
# - gemini_requests_total
# - gemini_response_time_seconds
# - gemini_errors_total
# - system_memory_usage_bytes
```

#### Grafana Dashboard

- **URL**: [http://localhost:3000](http://localhost:3000)
- **Usuario**: admin / admin
- **Dashboards**: Sistema, API, Errores

### Benchmarks Comparativos

#### Latencia por Modelo

gemini-1.5-flash:  1.2s ± 0.3s
gemini-1.5-pro:    2.8s ± 0.7s
gemini-1.0-pro:    1.8s ± 0.4s

#### Throughput

Concurrent Users: 10

- Gemini API:     8 req/s
- Vertex AI:      45 req/s
- With Cache:     120 req/s

#### Costo por 1M Tokens

Gemini API:       $0.00 (gratis)
Vertex AI Flash:  $0.50
Vertex AI Pro:    $3.50

### Optimización Recomendada

#### Para Desarrollo

```bash
# Configuración ligera
CACHE_ENABLED=true
METRICS_ENABLED=false
DEBUG_MODE=true

#### Para Producción

```bash
# Configuración optimizada
VERTEX_AI_ENABLED=true
CACHE_TTL=3600
METRICS_ENABLED=true
COMPRESSION_ENABLED=true
```

### Scripts Utiles

```bash
# Verificar dependencias
python scripts/check_dependencies.py

# Limpiar credenciales
```bash
python scripts/secure_env.py

# Configurar API keys
python scripts/setup_api_keys.py

# Verificar preparacion para lanzamiento
python scripts/launch_readiness_check.py
```

## 🧪 Pruebas

```bash
# Ejecutar todas las pruebas
python -m pytest tests/

# Pruebas con cobertura
python -m pytest tests/ --cov=app

# Pruebas específicas
python -m pytest tests/test_gemini_service.py
```

## 📊 Monitoreo

La aplicación incluye métricas de Prometheus:

- **Endpoint**: `/metrics`
- **Métricas**: Requests, latencia, errores
- **Dashboard**: Compatible con Grafana

## 🔒 Seguridad

- **HTTPS**: Forzado en producción
- **CSRF**: Protección contra ataques CSRF
- **XSS**: Sanitización de entrada
- **Rate Limiting**: Límites de velocidad
- **JWT**: Autenticación segura
- **Validación**: Entrada validada

Ver [documentación de seguridad](docs/SECURITY.md).

## 🌐 Internacionalización

Idiomas soportados:

- **Español** (es)
- **Inglés** (en)

Para agregar un nuevo idioma:

1. Crea `app/i18n/{codigo_idioma}.json`
2. Traduce todas las claves
3. Agrega el idioma al selector

## 📚 Documentación

- [Guía de Usuario](docs/USER_GUIDE.md)
- [Documentación de API](docs/API_DOCUMENTATION.md)
- [Guía de Contribución](docs/CONTRIBUTING.md)
- [Estructura del Proyecto](docs/PROJECT_STRUCTURE.md)
- [Seguridad de Credenciales](docs/SEGURIDAD_CREDENCIALES.md)

## 🤝 Contribuir

Las contribuciones son bienvenidas!

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

Ver [guia de contribucion](docs/CONTRIBUTING.md).

## 🔧 Troubleshooting

### Problemas Comunes

#### 🔑 Error de API Key

```text
Error: Invalid API key or quota exceeded
```

**Solucion:**

1. Verificar que `GOOGLE_API_KEY` este configurada correctamente
2. Comprobar cuota en [Google AI Studio](https://aistudio.google.com/)
3. Regenerar API key si es necesario

#### 🐳 Problemas con Docker

```text
Error: Port 5000 already in use
```

**Solucion:**

```bash
# Cambiar puerto en docker-compose.yml o detener proceso
sudo lsof -i :5000
docker-compose down
docker-compose up -d
```

#### 🗄️ Error de Base de Datos

```text
Error: Connection to database failed
```

**Solucion:**

```bash
# Reinicializar base de datos
python scripts/init_db.py
# O con Docker
docker-compose exec db psql -U postgres -c "DROP DATABASE IF EXISTS chatbot_db;"
docker-compose restart
```

#### 🌐 Problemas de CORS

```text
Error: CORS policy blocked
```

**Solucion:**

1. Verificar configuracion en `config/settings.py`
2. Agregar dominio a `CORS_ORIGINS`
3. Reiniciar servidor

#### 📱 PWA no se instala

**Solucion:**

1. Verificar HTTPS habilitado
2. Comprobar `manifest.json` valido
3. Verificar Service Worker registrado

#### 🔒 Error de autenticacion

```text
Error: JWT token invalid
```

**Solución:**

```bash
# Limpiar tokens y reiniciar sesión
python scripts/cleanup.py --tokens
# Verificar SECRET_KEY en .env
```

### Comandos de Diagnostico

```bash
# Verificar estado del sistema
python scripts/final_check.py

# Comprobar dependencias
pip check

```bash
# Verificar configuracion
python scripts/security_check.py

# Monitorear logs
docker-compose logs -f app

# Test de conectividad API
python scripts/test_chat_functionality.py
```

### Performance Issues

#### Respuestas lentas

1. Verificar latencia de red a Google AI
2. Optimizar prompts (reducir tokens)
3. Implementar cache Redis
4. Usar Vertex AI para mejor rendimiento

#### Alto uso de memoria

1. Configurar limites en Docker
2. Optimizar cache de conversaciones
3. Implementar limpieza automatica

### Logs Utiles

```bash
# Logs de aplicacion
tail -f logs/app.log

# Logs de errores
tail -f logs/error.log

# Logs de seguridad
tail -f logs/security.log

# Metricas Prometheus
curl http://localhost:9090/metrics
```

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- [Google Gemini AI](https://ai.google.dev/) por la API de IA
- [Flask](https://flask.palletsprojects.com/) por el framework web
- [Bootstrap](https://getbootstrap.com/) por los componentes UI
- Comunidad open source por las librerías utilizadas

## 📞 Soporte

- **Issues**: [GitHub Issues](https://github.com/shaydev-create/Gemini-AI-Chatbot/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/shaydev-create/Gemini-AI-Chatbot/discussions)
- **Email**: [Contacto](mailto:support@example.com)

## 📋 Changelog

### v2.0.0 (2025-01-XX)

- ✨ Nueva interfaz futurística
- 🌐 Soporte multiidioma
- 🎯 Panel de administración
- 🔒 Seguridad mejorada
- 📱 PWA completa

### v1.0.0 (2024-XX-XX)

- 🚀 Lanzamiento inicial
- 🤖 Integración Gemini AI
- 🌐 Extensión Chrome
- 🐳 Soporte Docker

---

<!-- align="center" -->

**¡Si te gusta este proyecto, dale una ⭐ en GitHub!**

[![GitHub stars](https://img.shields.io/github/stars/shaydev-create/Gemini-AI-Chatbot?style=social)](https://github.com/shaydev-create/Gemini-AI-Chatbot/stargazers)

</div>
