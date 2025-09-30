# Gemini AI Futuristic Chatbot - Version 2025

Un chatbot inteligente potenciado por Google Gemini AI con interfaz web moderna y extension de Chrome.

[![Chrome Web Store](https://img.shields.io/badge/Chrome%20Web%20Store-Available-brightgreen)](https://chrome.google.com/webstore)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/shaydev-create/Gemini-AI-Chatbot)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Privacy Policy](https://img.shields.io/badge/Privacy-Policy-green)](docs/PRIVACY_POLICY.md)

## Caracteristicas

- **IA Avanzada**: Integracion con Google Gemini AI
- **Interfaz Web**: Diseno moderno, responsivo y accesible (ARIA, skip links, selector de idioma)
- **Extension Chrome**: Acceso rapido desde el navegador
- **Seguro**: HTTPS, autenticacion, validacion y proteccion CSRF/XSS
- **PWA**: Funciona como aplicacion movil
- **Docker**: Despliegue facil con contenedores
- **Monitoreo**: Metricas Prometheus integradas
- **Multiidioma avanzado**: Seleccion dinamica de idioma en toda la app
- **Panel de Administracion**: Gestion y acceso restringido para administradores

## Panel de Administracion

El sistema incluye un panel de administracion basico accesible solo para usuarios autenticados con rol de administrador.

- **Ruta:** `/admin`
- **Proteccion:** Requiere JWT y rol de administrador
- **Template:** `admin.html`

Ejemplo de acceso:
```bash
curl -H "Authorization: Bearer <token_admin>" https://localhost:5000/admin
# Respuesta: Renderiza el panel si el usuario es admin
```

## Multiidioma avanzado

La aplicacion soporta traduccion dinamica de textos en espanol e ingles. Puedes agregar nuevos idiomas creando archivos JSON en `app/i18n/`.

Ejemplo para agregar frances:

1. Crea `app/i18n/fr.json` con las claves y traducciones.
2. Accede con `?lang=fr` en la URL o selecciona desde el frontend.

Todos los templates usan la funcion `translate` para mostrar textos segun el idioma seleccionado.

## Inicio Rapido

### Ejecucion Inmediata

```bash
# Clona el repositorio
git clone https://github.com/shaydev-create/Gemini-AI-Chatbot.git
cd Gemini-AI-Chatbot

# Configura tu API key de Gemini
echo "GEMINI_API_KEY=tu_api_key_aqui" > .env

# Ejecuta con Docker (recomendado)
docker-compose up -d

# O ejecuta localmente
pip install -r requirements.txt
python app.py
```

Listo! Abre http://localhost:5000 en tu navegador.

### Requisitos del Sistema

- **Python**: 3.8+ (recomendado 3.11+)
- **Docker**: Opcional pero recomendado
- **Navegador**: Chrome, Firefox, Safari, Edge (ultimas versiones)
- **API Key**: Google Gemini AI (gratuita)

## Configuracion de API Key

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
python scripts/secure_env.py

# Verifica que .env no tenga credenciales reales
cat .env
```

Ver [guia completa de seguridad](docs/SEGURIDAD_CREDENCIALES.md).

## Extension de Chrome

### Instalacion

1. Descarga o clona este repositorio
2. Abre Chrome y ve a `chrome://extensions/`
3. Activa "Modo de desarrollador"
4. Haz clic en "Cargar extension sin empaquetar"
5. Selecciona la carpeta `chrome_extension/`

### Uso

1. Haz clic en el icono de Gemini AI en la barra de herramientas
2. Configura tu API key en la ventana emergente
3. Comienza a chatear!

## Docker

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

## PWA (Progressive Web App)

La aplicacion funciona como PWA:

- **Instalable**: Agrega a pantalla de inicio
- **Offline**: Funciona sin conexion (limitado)
- **Responsive**: Optimizada para moviles
- **Fast**: Carga rapida con Service Worker

## Desarrollo

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
cp .env.example .env
# Edita .env con tus credenciales

# Ejecuta la aplicacion
python app.py
```

### Estructura del Proyecto

```
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
```

### Scripts Utiles

```bash
# Verificar dependencias
python scripts/check_dependencies.py

# Limpiar credenciales
python scripts/secure_env.py

# Configurar API keys
python scripts/setup_api_keys.py

# Verificar preparacion para lanzamiento
python scripts/launch_readiness_check.py
```

## Pruebas

```bash
# Ejecutar todas las pruebas
python -m pytest tests/

# Pruebas con cobertura
python -m pytest tests/ --cov=app

# Pruebas especificas
python -m pytest tests/test_gemini_service.py
```

## Monitoreo

La aplicacion incluye metricas de Prometheus:

- **Endpoint**: `/metrics`
- **Metricas**: Requests, latencia, errores
- **Dashboard**: Compatible con Grafana

## Seguridad

- **HTTPS**: Forzado en produccion
- **CSRF**: Proteccion contra ataques CSRF
- **XSS**: Sanitizacion de entrada
- **Rate Limiting**: Limites de velocidad
- **JWT**: Autenticacion segura
- **Validacion**: Entrada validada

Ver [documentacion de seguridad](docs/SECURITY.md).

## Internacionalizacion

Idiomas soportados:
- **Espanol** (es)
- **Ingles** (en)

Para agregar un nuevo idioma:
1. Crea `app/i18n/{codigo_idioma}.json`
2. Traduce todas las claves
3. Agrega el idioma al selector

## Documentacion

- [Guia de Usuario](docs/USER_GUIDE.md)
- [Documentacion de API](docs/API_DOCUMENTATION.md)
- [Guia de Contribucion](docs/CONTRIBUTING.md)
- [Estructura del Proyecto](docs/PROJECT_STRUCTURE.md)
- [Seguridad de Credenciales](docs/SEGURIDAD_CREDENCIALES.md)

## Contribuir

Las contribuciones son bienvenidas!

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

Ver [guia de contribucion](docs/CONTRIBUTING.md).

## Licencia

Este proyecto esta bajo la Licencia MIT. Ver [LICENSE](LICENSE) para mas detalles.

## Agradecimientos

- [Google Gemini AI](https://ai.google.dev/) por la API de IA
- [Flask](https://flask.palletsprojects.com/) por el framework web
- [Bootstrap](https://getbootstrap.com/) por los componentes UI
- Comunidad open source por las librerias utilizadas

## Soporte

- **Issues**: [GitHub Issues](https://github.com/shaydev-create/Gemini-AI-Chatbot/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/shaydev-create/Gemini-AI-Chatbot/discussions)
- **Email**: [Contacto](mailto:support@example.com)

## Changelog

### v2.0.0 (2025-01-XX)
- Nueva interfaz futuristica
- Soporte multiidioma
- Panel de administracion
- Seguridad mejorada
- PWA completa

### v1.0.0 (2024-XX-XX)
- Lanzamiento inicial
- Integracion Gemini AI
- Extension Chrome
- Soporte Docker

---

Si te gusta este proyecto, dale una estrella en GitHub!

