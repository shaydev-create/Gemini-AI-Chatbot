# API Documentation - Gemini AI Chatbot + Chrome Built-in AI APIs

## 🧠 Chrome Built-in AI APIs - Core Features

### **Base URL**
- **Desarrollo**: `http://localhost:3000`
- **Chrome Extension**: Conecta automáticamente a localhost:3000
- **Docker**: `http://localhost:8000`

---

## 🚀 Chrome Built-in AI APIs

### **✨ 1. Prompt API**
```javascript
// Función: generateText()
// Ubicación: chrome-ai-manager.js línea ~50
async function generateText() {
    const session = await ai.assistant.create();
    const result = await session.prompt(userInput);
    return result;
}
```
- **Descripción**: Generación de texto avanzada con IA
- **Uso**: Crear contenido, responder preguntas complejas
- **Input**: Texto libre del usuario
- **Output**: Respuesta generada por IA

### **🔍 2. Writer API**
```javascript
// Función: correctText()
// Ubicación: chat.html línea ~4998
async function correctText() {
    const writer = await ai.writer.create();
    const result = await writer.write(text, {
        tone: 'formal',
        format: 'plain-text'
    });
    return result;
}
```
- **Descripción**: Corrección y mejora de textos
- **Parámetros**: `tone`, `format`, `length`
- **Uso**: Mejorar gramática, estilo y claridad

### **🌐 3. Translator API**
```javascript
// Función: translateText()
// Ubicación: chat.html línea ~5068
async function translateText() {
    const translator = await ai.translator.create({
        sourceLanguage: 'es',
        targetLanguage: 'en'
    });
    const result = await translator.translate(text);
    return result;
}
```
- **Descripción**: Traducción entre idiomas
- **Idiomas**: es, en, fr, de, it, pt, ja, ko, zh
- **Uso**: Traducción instantánea y precisa

### **📄 4. Summarizer API**
```javascript
// Función: summarizeText()
// Ubicación: chat.html línea ~5159
async function summarizeText() {
    const summarizer = await ai.summarizer.create({
        type: 'key-points',
        format: 'markdown',
        length: 'medium'
    });
    const result = await summarizer.summarize(text);
    return result;
}
```
- **Tipos**: `key-points`, `tl;dr`, `teaser`, `headline`
- **Formatos**: `plain-text`, `markdown`
- **Longitudes**: `short`, `medium`, `long`

### **🖊️ 5. Rewriter API**
```javascript
// Función: rewriteText()
// Ubicación: chat.html línea ~5237
async function rewriteText() {
    const rewriter = await ai.rewriter.create({
        tone: 'casual',
        format: 'plain-text',
        length: 'as-is'
    });
    const result = await rewriter.rewrite(text);
    return result;
}
```
- **Tonos**: `formal`, `casual`, `enthusiastic`, `informational`
- **Uso**: Cambiar estilo y tono del contenido

### **📖 6. Proofreader API**
```javascript
// Función: proofreadText()
// Ubicación: chat.html línea ~5316
async function proofreadText() {
    const proofreader = await ai.proofreader.create();
    const result = await proofreader.proofread(text);
    return result;
}
```
- **Descripción**: Revisión ortográfica y gramatical
- **Uso**: Detectar y corregir errores

---

## 🌐 Flask API Endpoints (Backend)

### **Base URLs**
- **Desarrollo Local**: `http://localhost:3000/api`
- **Docker**: `http://localhost:8000/api`

### **Rutas Principales**

#### **📍 GET /**
- **Descripción**: Página principal futurística
- **Respuesta**: `index.html` con PWA y meta tags

#### **📍 GET /chat**
- **Descripción**: Interfaz de chat completa con Chrome AI APIs
- **Respuesta**: `chat.html` (5877 líneas de funcionalidad)
- **Incluye**: Todas las 6 Chrome AI APIs integradas

#### **📍 GET /chrome-ai-setup**
- **Descripción**: Página de configuración Chrome AI
- **Respuesta**: `chrome_ai_setup.html`
- **Uso**: Configurar y verificar APIs

#### **📍 GET /privacy_policy**
- **Descripción**: Política de privacidad (inglés)
- **Respuesta**: `privacy_policy_en.html`
- **Uso**: Cumplimiento Chrome Web Store

---

## 🔧 Chrome Extension Integration

### **Manifest Configuration**
```json
{
  "permissions": ["storage", "activeTab", "tabs", "offscreen"],
  "host_permissions": ["https://generativelanguage.googleapis.com/*"],
  "privacy_policy": "http://localhost:3000/privacy_policy"
}
```

### **Extension Flow**
1. **popup.js**: Detecta localhost:3000
2. **chrome.tabs.create()**: Abre aplicación completa  
3. **Acceso completo**: Todas las APIs disponibles

---

## 🛠️ API Availability Checking

### **Chrome AI Availability**
```javascript
// Verificar disponibilidad de APIs
const checkAvailability = async () => {
    const capabilities = await ai.assistant.capabilities();
    if (capabilities.available === 'readily') {
        // API lista para usar
        return true;
    }
    return false;
};
```

### **Error Handling**
- **API no disponible**: Fallback a Google Gemini
- **Rate limiting**: Manejo automático de límites
- **Offline**: Funcionalidad degradada elegante

### Autenticación

#### `POST /auth/register`
- **Descripción**: Registra un nuevo usuario.
- **Body**: `{"username": "test", "email": "test@example.com", "password": "password123"}`
- **Respuesta (201)**: `{"message": "User created successfully"}`

#### `POST /auth/login`
- **Descripción**: Inicia sesión y obtiene un token JWT.
- **Body**: `{"email": "test@example.com", "password": "password123"}`
- **Respuesta (200)**: `{"access_token": "...", "refresh_token": "..."}`

#### `POST /auth/refresh`
- **Descripción**: Refresca un token de acceso expirado.
- **Headers**: `Authorization: Bearer <refresh_token>`
- **Respuesta (200)**: `{"access_token": "..."}`

#### `POST /auth/logout`
- **Descripción**: Cierra la sesión del usuario (invalida el token).
- **Headers**: `Authorization: Bearer <access_token>`
- **Respuesta (200)**: `{"message": "Successfully logged out"}`

### Chat

#### `POST /chat/`
- **Descripción**: Envía un mensaje al chatbot y recibe una respuesta. Requiere autenticación.
- **Headers**: `Authorization: Bearer <access_token>`
- **Body**: `{"message": "Hola, ¿cómo estás?", "conversation_id": "uuid-opcional"}`
- **Respuesta (200)**:
  ```json
  {
    "response": "¡Hola! Estoy bien, ¿en qué puedo ayudarte?",
    "conversation_id": "...",
    "timestamp": "..."
  }
  ```

### Administración (Requiere rol de 'admin')

#### `GET /admin/health`
- **Descripción**: Verifica el estado del sistema y sus servicios (base de datos, Redis, API de Gemini).
- **Headers**: `Authorization: Bearer <access_token>`
- **Respuesta (200)**:
  ```json
  {
    "status": "healthy",
    "services": {
      "database": "connected",
      "redis": "connected",
      "gemini_api": "ok"
    }
  }
  ```

#### `GET /admin/metrics`
- **Descripción**: Obtiene métricas de rendimiento del sistema.
- **Headers**: `Authorization: Bearer <access_token>`
- **Respuesta (200)**:
  ```json
  {
    "active_users": 15,
    "total_requests": 1024,
    "error_rate": "2.5%",
    "avg_response_time_ms": 120
  }
  ```

## 🔐 Autenticación

- **Esquema**: JWT (JSON Web Tokens).
- **Flujo**:
  1. El cliente envía `email` y `password` a `/auth/login`.
  2. El servidor valida las credenciales y devuelve un `access_token` (corta duración) y un `refresh_token` (larga duración).
  3. El cliente envía el `access_token` en el header `Authorization: Bearer <token>` para acceder a rutas protegidas.
  4. Si el `access_token` expira, el cliente usa el `refresh_token` en `/auth/refresh` para obtener un nuevo `access_token`.

## 🚨 Códigos de Error Comunes

| Código | Descripción |
|--------|-------------|
| 400 | Bad Request (ej. datos de entrada inválidos) |
| 401 | Unauthorized (ej. token no provisto o inválido) |
| 403 | Forbidden (ej. usuario no tiene permisos de administrador) |
| 404 | Not Found (ej. endpoint no existe) |
| 429 | Too Many Requests (límite de peticiones excedido) |
| 500 | Internal Server Error (error inesperado en el servidor) |

## 📝 Ejemplos de Uso

### JavaScript (Fetch API)
```javascript
async function sendMessage(message, token) {
  const response = await fetch('/api/chat/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ message })
  });
  const data = await response.json();
  console.log(data.response);
}
```

### Python (requests)
```python
import requests

def get_health_status(token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get('http://localhost:8000/api/admin/health', headers=headers)
    print(response.json())
```

### cURL
```bash
# Iniciar sesión
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "adminpassword"}'

# Enviar un mensaje (reemplaza <TOKEN> con el access_token obtenido)
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"message": "Explícame la computación cuántica"}'
```