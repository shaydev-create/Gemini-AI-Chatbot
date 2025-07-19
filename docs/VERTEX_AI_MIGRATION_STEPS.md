# 🚀 Guía de Migración a Vertex AI - Pasos Específicos

## 📋 CHECKLIST DE MIGRACIÓN

### ✅ Paso 1: Configuración Google Cloud (15 minutos)

1. **Crear proyecto en Google Cloud**
   - Ir a: https://console.cloud.google.com
   - Crear nuevo proyecto: "gemini-ai-chatbot-prod"
   - Anotar el PROJECT_ID

2. **Habilitar APIs necesarias**
   ```bash
   gcloud services enable aiplatform.googleapis.com
   gcloud services enable compute.googleapis.com
   ```

3. **Configurar billing**
   - Vincular tarjeta de crédito
   - Configurar alertas de billing ($10, $25, $50)

### ✅ Paso 2: Crear Service Account (10 minutos)

1. **Crear service account**
   - IAM & Admin > Service Accounts
   - Crear nueva cuenta: "vertex-ai-service"
   - Roles: "Vertex AI User", "AI Platform Developer"

2. **Descargar JSON key**
   - Crear nueva key (JSON)
   - Guardar como: `credentials/vertex-ai-key.json`
   - ⚠️ NUNCA subir a Git

### ✅ Paso 3: Configurar Variables de Entorno (5 minutos)

1. **Copiar template**
   ```bash
   cp .env.vertex .env.production
   ```

2. **Editar variables**
   ```bash
   GOOGLE_CLOUD_PROJECT_ID=tu-proyecto-real-id
   GOOGLE_APPLICATION_CREDENTIALS=./credentials/vertex-ai-key.json
   ```

### ✅ Paso 4: Instalar Dependencias (5 minutos)

```bash
pip install google-cloud-aiplatform
pip install vertexai
pip install google-auth
```

### ✅ Paso 5: Testing (30 minutos)

1. **Test básico**
   ```python
   from src.config.vertex_client import vertex_client
   
   # Test de conexión
   await vertex_client.initialize()
   
   # Test de respuesta
   response = await vertex_client.generate_response("Hola, ¿cómo estás?")
   print(response)
   ```

2. **Test de fallback**
   - Desconectar internet
   - Verificar que usa Gemini API

### ✅ Paso 6: Deploy Gradual (1 día)

1. **Deploy en staging**
   - Configurar variables de entorno
   - Test completo de funcionalidad

2. **Deploy en producción**
   - A/B testing: 10% Vertex AI
   - Monitorear errores y costos
   - Incrementar gradualmente

## 🔧 COMANDOS ÚTILES

### Verificar configuración
```bash
gcloud auth list
gcloud config list project
gcloud services list --enabled
```

### Monitorear costos
```bash
gcloud billing budgets list
gcloud logging read "resource.type=vertex_ai"
```

### Troubleshooting
```bash
# Verificar permisos
gcloud auth application-default login

# Test de API
gcloud ai models list --region=us-central1
```

## 📊 MONITOREO POST-MIGRACIÓN

### Métricas a vigilar (primeros 7 días)
- ✅ Tasa de éxito de requests
- ✅ Latencia promedio
- ✅ Costo diario
- ✅ Uso de fallback

### Alertas recomendadas
- 🚨 Costo diario > $10
- 🚨 Tasa de error > 5%
- 🚨 Latencia > 5 segundos

## 🎯 RESULTADOS ESPERADOS

### Mejoras inmediatas
- ⚡ Latencia: 2-3 segundos (vs 5-10 actual)
- 🔄 Confiabilidad: 99.9% uptime
- 📈 Límites: 1000 req/min (vs 15 actual)
- 💰 Costo: $15-50/mes (escalable)

### Beneficios a largo plazo
- 🚀 Escalabilidad automática
- 📊 Analytics detallados
- 🛡️ SLA garantizado
- 🔧 Soporte técnico

## ❓ PREGUNTAS FRECUENTES

**Q: ¿Qué pasa si se agota el presupuesto?**
A: Automáticamente cambia a Gemini API gratuita.

**Q: ¿Puedo cambiar de modelo dinámicamente?**
A: Sí, puedes usar 'fast', 'pro' o 'basic' según necesidad.

**Q: ¿Cómo monitoreo los costos?**
A: Dashboard en Google Cloud + alertas automáticas.

**Q: ¿Es reversible la migración?**
A: Sí, puedes volver a Gemini API en cualquier momento.
