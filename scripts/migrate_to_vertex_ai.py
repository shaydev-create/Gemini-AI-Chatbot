#!/usr/bin/env python3
"""
Script de migración automática a Google Cloud Vertex AI
Migra desde Gemini API gratuita a Vertex AI con fallback
"""

import os
import json
import subprocess
import sys
from pathlib import Path

def check_requirements():
    """Verificar requisitos previos"""
    print("🔍 Verificando requisitos...")
    
    requirements = {
        'google-cloud-aiplatform': 'pip install google-cloud-aiplatform',
        'google-auth': 'pip install google-auth',
        'google-auth-oauthlib': 'pip install google-auth-oauthlib'
    }
    
    missing = []
    for package, install_cmd in requirements.items():
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - {install_cmd}")
            missing.append(install_cmd)
    
    if missing:
        print("\n📦 Instalando dependencias faltantes...")
        for cmd in missing:
            subprocess.run(cmd.split(), check=True)
        print("✅ Dependencias instaladas")

def create_vertex_ai_config():
    """Crear configuración para Vertex AI"""
    
    config_content = '''"""
Configuración para Google Cloud Vertex AI
"""

import os
from google.cloud import aiplatform
from google.auth import default

class VertexAIConfig:
    def __init__(self):
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID', 'tu-proyecto-id')
        self.location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
        self.credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
        # Modelos disponibles
        self.models = {
            'fast': 'gemini-1.5-flash',
            'pro': 'gemini-1.5-pro', 
            'basic': 'gemini-1.0-pro'
        }
        
        # Configuración de costos (USD por 1M tokens)
        self.costs = {
            'gemini-1.5-flash': 0.50,
            'gemini-1.5-pro': 3.50,
            'gemini-1.0-pro': 0.25
        }
        
        # Límites de uso
        self.limits = {
            'requests_per_minute': 1000,
            'tokens_per_request': 32000,
            'max_daily_cost': 50.0  # USD
        }
    
    def initialize(self):
        """Inicializar Vertex AI"""
        try:
            if self.credentials_path and os.path.exists(self.credentials_path):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credentials_path
            
            aiplatform.init(
                project=self.project_id,
                location=self.location
            )
            return True
        except Exception as e:
            print(f"Error inicializando Vertex AI: {e}")
            return False
    
    def get_model_endpoint(self, model_type='fast'):
        """Obtener endpoint del modelo"""
        model_name = self.models.get(model_type, self.models['fast'])
        return f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/{model_name}"

# Configuración global
vertex_config = VertexAIConfig()
'''
    
    with open('src/config/vertex_ai.py', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("✅ Configuración Vertex AI creada: src/config/vertex_ai.py")

def create_vertex_ai_client():
    """Crear cliente para Vertex AI"""
    
    client_content = '''"""
Cliente para Google Cloud Vertex AI
Maneja requests con fallback automático
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Union
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel
import vertexai

from .vertex_ai import vertex_config
from .gemini_client import GeminiClient  # Fallback

class VertexAIClient:
    def __init__(self):
        self.config = vertex_config
        self.fallback_client = GeminiClient()  # Cliente Gemini original
        self.initialized = False
        self.daily_cost = 0.0
        self.request_count = 0
        self.last_reset = time.time()
        
    async def initialize(self):
        """Inicializar cliente Vertex AI"""
        try:
            # Inicializar Vertex AI
            vertexai.init(
                project=self.config.project_id,
                location=self.config.location
            )
            
            # Crear modelos
            self.models = {
                'fast': GenerativeModel(self.config.models['fast']),
                'pro': GenerativeModel(self.config.models['pro']),
                'basic': GenerativeModel(self.config.models['basic'])
            }
            
            self.initialized = True
            print("✅ Vertex AI inicializado correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error inicializando Vertex AI: {e}")
            print("🔄 Usando Gemini API como fallback")
            return False
    
    def _reset_daily_limits(self):
        """Resetear límites diarios"""
        current_time = time.time()
        if current_time - self.last_reset > 86400:  # 24 horas
            self.daily_cost = 0.0
            self.request_count = 0
            self.last_reset = current_time
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Calcular costo del request"""
        total_tokens = input_tokens + output_tokens
        cost_per_million = self.config.costs.get(model, 0.50)
        return (total_tokens / 1_000_000) * cost_per_million
    
    def _check_limits(self, estimated_tokens: int) -> bool:
        """Verificar límites de uso"""
        self._reset_daily_limits()
        
        # Verificar límite de costo diario
        estimated_cost = (estimated_tokens / 1_000_000) * 0.50  # Estimación conservadora
        if self.daily_cost + estimated_cost > self.config.limits['max_daily_cost']:
            return False
        
        return True
    
    async def generate_response(
        self,
        prompt: str,
        model_type: str = 'fast',
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict:
        """Generar respuesta con Vertex AI"""
        
        if not self.initialized:
            await self.initialize()
        
        # Si Vertex AI no está disponible, usar fallback
        if not self.initialized:
            return await self.fallback_client.generate_response(
                prompt, max_tokens=max_tokens, temperature=temperature, **kwargs
            )
        
        # Verificar límites
        estimated_tokens = len(prompt.split()) * 1.3 + max_tokens
        if not self._check_limits(estimated_tokens):
            print("⚠️ Límite diario alcanzado, usando fallback")
            return await self.fallback_client.generate_response(
                prompt, max_tokens=max_tokens, temperature=temperature, **kwargs
            )
        
        try:
            # Seleccionar modelo
            model = self.models.get(model_type, self.models['fast'])
            
            # Configurar generación
            generation_config = {
                'max_output_tokens': max_tokens,
                'temperature': temperature,
                'top_p': kwargs.get('top_p', 0.8),
                'top_k': kwargs.get('top_k', 40)
            }
            
            # Generar respuesta
            start_time = time.time()
            response = await model.generate_content_async(
                prompt,
                generation_config=generation_config
            )
            
            # Procesar respuesta
            response_time = time.time() - start_time
            response_text = response.text
            
            # Calcular métricas
            input_tokens = len(prompt.split()) * 1.3  # Estimación
            output_tokens = len(response_text.split()) * 1.3
            cost = self._calculate_cost(input_tokens, output_tokens, self.config.models[model_type])
            
            # Actualizar contadores
            self.daily_cost += cost
            self.request_count += 1
            
            return {
                'response': response_text,
                'model': self.config.models[model_type],
                'tokens_used': int(input_tokens + output_tokens),
                'cost': cost,
                'response_time': response_time,
                'source': 'vertex_ai'
            }
            
        except Exception as e:
            print(f"❌ Error en Vertex AI: {e}")
            print("🔄 Usando fallback...")
            return await self.fallback_client.generate_response(
                prompt, max_tokens=max_tokens, temperature=temperature, **kwargs
            )
    
    async def generate_stream_response(self, prompt: str, **kwargs):
        """Generar respuesta en streaming"""
        # Implementar streaming si es necesario
        response = await self.generate_response(prompt, **kwargs)
        yield response['response']
    
    def get_usage_stats(self) -> Dict:
        """Obtener estadísticas de uso"""
        self._reset_daily_limits()
        
        return {
            'daily_requests': self.request_count,
            'daily_cost': round(self.daily_cost, 4),
            'cost_limit': self.config.limits['max_daily_cost'],
            'cost_remaining': round(self.config.limits['max_daily_cost'] - self.daily_cost, 4),
            'percentage_used': round((self.daily_cost / self.config.limits['max_daily_cost']) * 100, 2)
        }

# Cliente global
vertex_client = VertexAIClient()
'''
    
    os.makedirs('src/config', exist_ok=True)
    with open('src/config/vertex_client.py', 'w', encoding='utf-8') as f:
        f.write(client_content)
    
    print("✅ Cliente Vertex AI creado: src/config/vertex_client.py")

def create_env_template():
    """Crear template de variables de entorno"""
    
    env_content = '''# Google Cloud Vertex AI Configuration
GOOGLE_CLOUD_PROJECT_ID=tu-proyecto-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json

# Vertex AI Settings
VERTEX_AI_ENABLED=true
VERTEX_AI_DEFAULT_MODEL=fast
VERTEX_AI_MAX_DAILY_COST=50.0

# Fallback Configuration
ENABLE_FALLBACK=true
FALLBACK_ORDER=vertex_ai,gemini_api,openai

# Monitoring
ENABLE_USAGE_TRACKING=true
COST_ALERT_THRESHOLD=80
'''
    
    with open('.env.vertex', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ Template de variables creado: .env.vertex")

def create_migration_guide():
    """Crear guía de migración"""
    
    guide_content = '''# 🚀 Guía de Migración a Vertex AI - Pasos Específicos

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
'''
    
    with open('docs/VERTEX_AI_MIGRATION_STEPS.md', 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("✅ Guía de migración creada: docs/VERTEX_AI_MIGRATION_STEPS.md")

def main():
    """Ejecutar migración completa"""
    
    print("🚀 INICIANDO MIGRACIÓN A VERTEX AI")
    print("=" * 50)
    
    try:
        # 1. Verificar requisitos
        check_requirements()
        
        # 2. Crear configuración
        create_vertex_ai_config()
        
        # 3. Crear cliente
        create_vertex_ai_client()
        
        # 4. Crear template de variables
        create_env_template()
        
        # 5. Crear guía
        create_migration_guide()
        
        print("\n" + "=" * 50)
        print("✅ MIGRACIÓN PREPARADA EXITOSAMENTE")
        print("\n📋 PRÓXIMOS PASOS:")
        print("1. 🌐 Crear proyecto en Google Cloud")
        print("2. 🔑 Configurar service account")
        print("3. 📝 Editar .env.vertex con tus datos")
        print("4. 🧪 Ejecutar tests")
        print("5. 🚀 Deploy a producción")
        
        print("\n📚 DOCUMENTACIÓN:")
        print("• Guía detallada: docs/VERTEX_AI_MIGRATION_STEPS.md")
        print("• Configuración: src/config/vertex_ai.py")
        print("• Cliente: src/config/vertex_client.py")
        print("• Variables: .env.vertex")
        
        print("\n💰 COSTO ESTIMADO:")
        print("• Setup: $0 (Google Cloud gratis)")
        print("• Mensual: $15-50 USD (según uso)")
        print("• ROI: Inmediato (mejor UX + escalabilidad)")
        
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        print("🔧 Revisa los logs y vuelve a intentar")

if __name__ == "__main__":
    main()