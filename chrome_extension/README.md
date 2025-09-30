# 🚀 Gemini AI Futuristic Chatbot - Chrome Extension

## 📋 Descripción

Extensión de Chrome que proporciona acceso directo a Google Gemini AI con una interfaz moderna y futurista. Funciona de forma completamente independiente sin necesidad de servidores locales.

## ✨ Características

- 🤖 **Chat con IA**: Conversaciones naturales con Google Gemini
- 🔒 **Privacidad Total**: No recopilamos ni almacenamos datos personales
- ⚡ **Respuestas Rápidas**: Conexión directa con la API de Google
- 🎨 **Interfaz Moderna**: Diseño futurista con gradientes y animaciones
- 🔑 **Configuración Simple**: Solo necesitas tu API Key de Google

## 🛠️ Instalación para Desarrollo

1. **Clonar o descargar** este repositorio
2. **Abrir Chrome** y navegar a `chrome://extensions/`
3. **Activar el modo desarrollador** (toggle en la esquina superior derecha)
4. **Hacer clic en "Cargar extensión sin empaquetar"**
5. **Seleccionar** la carpeta `chrome_extension`

## 🔑 Configuración

1. **Obtener API Key**:
   - Visita [Google AI Studio](https://aistudio.google.com/)
   - Crea una nueva API Key gratuita
   - Copia la API Key

2. **Configurar la Extensión**:
   - Haz clic en el icono 🚀 de la extensión
   - Pega tu API Key en el campo correspondiente
   - Haz clic en "Guardar y Continuar"

## 🧪 Pruebas

### Pruebas Manuales

1. **Instalación**:
   - [ ] La extensión se instala sin errores
   - [ ] Se muestra la página de bienvenida
   - [ ] El icono aparece en la barra de herramientas

2. **Configuración**:
   - [ ] Se puede ingresar la API Key
   - [ ] La API Key se guarda correctamente
   - [ ] Se muestra la interfaz de chat después de configurar

3. **Funcionalidad de Chat**:
   - [ ] Se pueden enviar mensajes
   - [ ] Se reciben respuestas de Gemini AI
   - [ ] Los mensajes se muestran correctamente
   - [ ] El botón de limpiar conversación funciona

4. **Interfaz**:
   - [ ] El diseño es responsive
   - [ ] Los colores y gradientes se muestran correctamente
   - [ ] Las animaciones funcionan suavemente

## 📁 Estructura de Archivos

```text
chrome_extension/
├── manifest.json          # Configuración de la extensión
├── popup.html             # Interfaz principal del popup
├── popup.js               # Lógica del chat y API
├── background.js          # Service worker
├── welcome.html           # Página de bienvenida
├── privacy_policy.html    # Política de privacidad
├── index.html             # Página de información (legacy)
├── icons/                 # Iconos de la extensión
│   ├── icon_16.png
│   ├── icon_48.png
│   └── icon_128.png
└── README.md              # Este archivo
```

## 🔒 Seguridad y Privacidad

- ✅ **Manifest V3**: Cumple con las últimas especificaciones de seguridad
- ✅ **Permisos Mínimos**: Solo solicita permisos esenciales
- ✅ **Sin Tracking**: No utiliza cookies ni sistemas de seguimiento
- ✅ **Almacenamiento Local**: Solo la API Key se guarda en Chrome Storage
- ✅ **Comunicación Segura**: Todas las conexiones usan HTTPS

## 📋 Checklist para Chrome Web Store

### Requisitos Técnicos

- [x] Manifest V3 implementado
- [x] Permisos justificados y mínimos
- [x] CSP (Content Security Policy) configurado
- [x] Sin código malicioso o sospechoso
- [x] Funcionalidad independiente (sin servidores externos)

### Requisitos de Contenido

- [x] Política de privacidad completa y actualizada
- [x] Descripción clara de la funcionalidad
- [x] Iconos en todas las resoluciones requeridas
- [x] Página de bienvenida para nuevos usuarios

### Pruebas de Calidad

- [x] Funcionalidad principal probada
- [x] Interfaz responsive y accesible
- [x] Manejo de errores implementado
- [x] Experiencia de usuario optimizada

## 🚀 Preparación para Submisión

1. **Verificar que todos los archivos están presentes**
2. **Probar la extensión en modo desarrollador**
3. **Empaquetar la extensión** (Chrome generará el .crx)
4. **Subir a Chrome Web Store Developer Dashboard**

## 📞 Soporte

Para reportar problemas o sugerencias, por favor contacta al desarrollador.

---

**Versión**: 1.0.3  
**Última actualización**: Enero 2025  
**Compatibilidad**: Chrome 88+
