# Documentación API - Gemini AI Chatbot

## 🌐 Endpoints Principales

### Base URL
- **Desarrollo**: `https://localhost:5000`
- **Producción**: `https://tu-dominio.com`

## 📡 API Endpoints

### 1. Página Principal
```http
GET /
```

**Descripción**: Página principal de la aplicación web

**Respuesta**:
```html
<!DOCTYPE html>
<html>
<!-- Página principal del chatbot -->
</html>
```

### 2. Chat con Gemini AI
```http
POST /api/chat
```

**Descripción**: Envía un mensaje al modelo Gemini AI y recibe una respuesta

**Headers**:
```http
Content-Type: application/json
```

**Body**:
```json
{
  "message": "Hola, ¿cómo estás?",
  "conversation_id": "uuid-opcional",
  "model": "gemini-pro"
}
```

**Respuesta Exitosa (200)**:
```json
{
  "success": true,
  "response": "¡Hola! Estoy muy bien, gracias por preguntar. ¿En qué puedo ayudarte hoy?",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "model_used": "gemini-pro",
  "timestamp": "2025-01-20T10:30:00Z",
  "tokens_used": 25,
  "response_time_ms": 1250
}
```

**Respuesta de Error (400)**:
```json
{
  "success": false,
  "error": "Mensaje requerido",
  "error_code": "MISSING_MESSAGE",
  "timestamp": "2025-01-20T10:30:00Z"
}
```

### 3. Estado del Sistema
```http
GET /api/health
```

**Descripción**: Verifica el estado del sistema y servicios

**Respuesta**:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-20T10:30:00Z",
  "version": "1.0.2",
  "services": {
    "gemini_api": "connected",
    "database": "connected",
    "cache": "active"
  },
  "uptime_seconds": 3600,
  "memory_usage_mb": 128.5
}
```

### 4. Métricas del Sistema
```http
GET /api/metrics
```

**Descripción**: Obtiene métricas de rendimiento del sistema

**Respuesta**:
```json
{
  "requests_total": 1250,
  "requests_per_minute": 45,
  "average_response_time_ms": 850,
  "cache_hit_rate": 0.75,
  "active_conversations": 23,
  "error_rate": 0.02,
  "gemini_api_calls": 980,
  "timestamp": "2025-01-20T10:30:00Z"
}
```

### 5. Historial de Conversación
```http
GET /api/conversation/{conversation_id}
```

**Descripción**: Obtiene el historial de una conversación específica

**Parámetros**:
- `conversation_id`: UUID de la conversación

**Respuesta**:
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-01-20T10:00:00Z",
  "updated_at": "2025-01-20T10:30:00Z",
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "Hola",
      "timestamp": "2025-01-20T10:00:00Z"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "¡Hola! ¿En qué puedo ayudarte?",
      "timestamp": "2025-01-20T10:00:05Z",
      "model": "gemini-pro",
      "tokens": 15
    }
  ],
  "total_messages": 2,
  "total_tokens": 35
}
```

### 6. Limpiar Conversación
```http
DELETE /api/conversation/{conversation_id}
```

**Descripción**: Elimina una conversación específica

**Respuesta**:
```json
{
  "success": true,
  "message": "Conversación eliminada exitosamente",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 7. Configuración del Usuario
```http
GET /api/config
POST /api/config
```

**GET - Obtener Configuración**:
```json
{
  "model": "gemini-pro",
  "temperature": 0.7,
  "max_tokens": 1000,
  "language": "es",
  "theme": "dark",
  "auto_save": true
}
```

**POST - Actualizar Configuración**:
```json
{
  "model": "gemini-pro",
  "temperature": 0.8,
  "max_tokens": 1500,
  "language": "en",
  "theme": "light"
}
```

## 🔐 Autenticación

### JWT Token (Opcional)
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### API Key (Desarrollo)
```http
X-API-Key: tu-api-key-de-desarrollo
```

## 📊 Rate Limiting

- **Límite**: 60 requests por minuto por IP
- **Headers de Respuesta**:
  ```http
  X-RateLimit-Limit: 60
  X-RateLimit-Remaining: 45
  X-RateLimit-Reset: 1642680000
  ```

## 🚨 Códigos de Error

| Código | Descripción | Solución |
|--------|-------------|----------|
| 400 | Bad Request | Verificar formato del request |
| 401 | Unauthorized | Verificar autenticación |
| 403 | Forbidden | Verificar permisos |
| 404 | Not Found | Verificar endpoint |
| 429 | Too Many Requests | Respetar rate limiting |
| 500 | Internal Server Error | Contactar soporte |
| 503 | Service Unavailable | Servicio temporalmente no disponible |

## 📝 Ejemplos de Uso

### JavaScript (Fetch)
```javascript
// Enviar mensaje al chatbot
async function sendMessage(message) {
  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message,
        model: 'gemini-pro'
      })
    });
    
    const data = await response.json();
    
    if (data.success) {
      console.log('Respuesta:', data.response);
      return data;
    } else {
      console.error('Error:', data.error);
    }
  } catch (error) {
    console.error('Error de red:', error);
  }
}

// Usar la función
sendMessage('¿Cuál es la capital de Francia?');
```

### Python (requests)
```python
import requests
import json

def send_message(message, base_url='https://localhost:5000'):
    """Envía un mensaje al chatbot Gemini AI"""
    
    url = f"{base_url}/api/chat"
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'message': message,
        'model': 'gemini-pro'
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, verify=False)
        response.raise_for_status()
        
        result = response.json()
        if result['success']:
            print(f"Respuesta: {result['response']}")
            return result
        else:
            print(f"Error: {result['error']}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")

# Usar la función
send_message("Explícame qué es la inteligencia artificial")
```

### cURL
```bash
# Enviar mensaje
curl -X POST https://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hola, ¿cómo funciona Gemini AI?",
    "model": "gemini-pro"
  }' \
  -k

# Verificar estado del sistema
curl -X GET https://localhost:5000/api/health -k

# Obtener métricas
curl -X GET https://localhost:5000/api/metrics -k
```

## 🔧 Configuración del Cliente

### WebSocket (Futuro)
```javascript
// Conexión en tiempo real (próximamente)
const ws = new WebSocket('wss://localhost:5000/ws');

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Mensaje en tiempo real:', data);
};
```

### Server-Sent Events
```javascript
// Eventos del servidor
const eventSource = new EventSource('/api/events');

eventSource.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Evento:', data);
};
```

## 📚 Modelos Disponibles

| Modelo | Descripción | Tokens Max | Uso Recomendado |
|--------|-------------|------------|-----------------|
| gemini-pro | Modelo principal | 30,720 | Conversaciones generales |
| gemini-pro-vision | Con capacidades de visión | 16,384 | Análisis de imágenes |
| gemini-ultra | Modelo más avanzado | 30,720 | Tareas complejas |

## 🛡️ Seguridad

### HTTPS
- Todos los endpoints requieren HTTPS en producción
- Certificados SSL/TLS válidos

### Validación de Entrada
- Sanitización automática de inputs
- Validación de tipos de datos
- Límites de longitud de mensaje

### Logging
- Todos los requests son loggeados
- No se almacenan datos sensibles
- Rotación automática de logs

## 📞 Soporte

- **Documentación**: [docs/](../docs/)
- **Issues**: [GitHub Issues](https://github.com/shaydev-create/Gemini-AI-Chatbot/issues)
- **Email**: api-support@gemini-ai.com

---

Esta documentación cubre todos los endpoints y funcionalidades principales de la API de Gemini AI Chatbot. 🚀