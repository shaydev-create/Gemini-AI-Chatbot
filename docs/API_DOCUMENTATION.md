# Documentación API - Gemini AI Chatbot

## 🌐 Endpoints Principales

### Base URL
- **Desarrollo (Docker)**: `http://localhost:8000/api`
- **Desarrollo (Local)**: `http://localhost:5000/api`
- **Producción**: `https://tu-dominio.com/api`

## 📡 API Endpoints

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