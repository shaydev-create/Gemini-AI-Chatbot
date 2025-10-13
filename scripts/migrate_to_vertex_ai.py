#!/usr/bin/env python3
"""
Script de migración automática a Google Cloud Vertex AI
Migra desde Gemini API gratuita a Vertex AI con fallback
Actualizado para usar el nuevo cliente Vertex AI
"""

import logging
import os
import sys
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_project_root() -> Path:
    """Obtener la ruta raíz del proyecto.

    Returns:
        Path: Ruta al directorio raíz del proyecto
    """
    current_path = Path(__file__).parent

    # Buscar hacia arriba hasta encontrar requirements.txt o .git
    while current_path.parent != current_path:
        if (current_path / "requirements.txt").exists() or (
            current_path / ".git"
        ).exists():
            return current_path
        current_path = current_path.parent

    return Path(__file__).parent.parent


def check_requirements() -> bool:
    """Verificar requisitos previos.

    Returns:
        bool: True si todos los requisitos están satisfechos
    """
    logger.info("🔍 Verificando requisitos...")

    requirements = {
        "google-cloud-aiplatform": "google-cloud-aiplatform",
        "vertexai": "vertexai",
        "google-auth": "google-auth",
        "google-auth-oauthlib": "google-auth-oauthlib",
        "google-generativeai": "google-generativeai",
    }

    missing = []
    for package, pip_name in requirements.items():
        try:
            __import__(package.replace("-", "_"))
            logger.info(f"✅ {package}")
        except ImportError:
            logger.error(f"❌ {package}")
            missing.append(pip_name)

    if missing:
        logger.error("\n📦 Dependencias faltantes. Instalar con:")
        logger.error(f"pip install {' '.join(missing)}")
        return False

    logger.info("✅ Todos los requisitos están satisfechos")
    return True


def update_vertex_ai_integration() -> bool:
    """Actualizar integración con Vertex AI.

    Returns:
        bool: True si la actualización fue exitosa
    """
    logger.info("🔧 Actualizando integración con Vertex AI...")

    try:
        # Verificar que los archivos necesarios existen
        project_root = get_project_root()

        required_files = ["src/config/vertex_ai.py", "src/config/vertex_client.py"]

        for file_path in required_files:
            full_path = project_root / file_path
            if not full_path.exists():
                logger.error(f"❌ Archivo requerido no encontrado: {file_path}")
                return False
            logger.info(f"✅ {file_path} encontrado")

        logger.info("✅ Integración con Vertex AI verificada")
        return True

    except Exception as e:
        logger.error(f"❌ Error actualizando integración: {e}")
        return False


def create_vertex_ai_config():
    """Crear configuración para Vertex AI (legacy - mantenido por compatibilidad)"""
    logger.warning("⚠️ Esta función es legacy. Usar src/config/vertex_ai.py")

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

    with open("src/config/vertex_ai.py", "w", encoding="utf-8") as f:
        f.write(config_content)

    print("✅ Configuración Vertex AI creada: src/config/vertex_ai.py")


def create_vertex_ai_client():
    """Crear cliente para Vertex AI (legacy - mantenido por compatibilidad)"""
    logger.warning("⚠️ Esta función es legacy. Usar src/config/vertex_client.py")

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

    os.makedirs("src/config", exist_ok=True)
    with open("src/config/vertex_client.py", "w", encoding="utf-8") as f:
        f.write(client_content)

    print("✅ Cliente Vertex AI creado: src/config/vertex_client.py")


def create_env_template():
    """Crear template de variables de entorno"""

    env_content = """# Google Cloud Vertex AI Configuration
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
"""

    with open(".env.vertex", "w", encoding="utf-8") as f:
        f.write(env_content)

    print("✅ Template de variables creado: .env.vertex")


def create_migration_guide():
    """Crear guía de migración"""

    guide_content = """# 🚀 Guía de Migración a Vertex AI - Pasos Específicos

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
   from app.config.vertex_client import vertex_client

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
"""

    with open("docs/VERTEX_AI_MIGRATION_STEPS.md", "w", encoding="utf-8") as f:
        f.write(guide_content)

    print("✅ Guía de migración creada: docs/VERTEX_AI_MIGRATION_STEPS.md")


def test_vertex_ai_integration() -> bool:
    """Probar la integración con Vertex AI.

    Returns:
        bool: True si la integración funciona correctamente
    """
    logger.info("🧪 Probando integración con Vertex AI...")

    try:
        # Importar el nuevo cliente
        sys.path.insert(0, str(get_project_root()))
        # Intentar inicializar
        import asyncio

        from app.config.vertex_client import vertex_client

        async def test_client():
            success = await vertex_client.initialize()
            if success:
                logger.info("✅ Cliente Vertex AI inicializado")

                # Obtener estadísticas
                stats = vertex_client.get_usage_stats()
                logger.info(f"📊 Estado: {stats['status']}")

                return True
            else:
                logger.warning("⚠️ Vertex AI no disponible, fallback activo")
                return False

        result = asyncio.run(test_client())
        return result

    except Exception as e:
        logger.error(f"❌ Error probando integración: {e}")
        return False


def main():
    """Función principal del script de migración"""
    import argparse

    parser = argparse.ArgumentParser(description="Migración a Google Cloud Vertex AI")
    parser.add_argument(
        "--check", action="store_true", help="Solo verificar requisitos y configuración"
    )
    parser.add_argument(
        "--test", action="store_true", help="Probar integración con Vertex AI"
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Configurar archivos legacy (no recomendado)",
    )

    args = parser.parse_args()

    logger.info("🚀 Migración a Google Cloud Vertex AI")
    logger.info("=" * 40)

    try:
        # 1. Verificar requisitos
        if not check_requirements():
            logger.error("❌ Requisitos no satisfechos")
            sys.exit(1)

        # 2. Verificar integración actual
        if not update_vertex_ai_integration():
            logger.error("❌ Integración no disponible")
            sys.exit(1)

        # Ejecutar acciones según argumentos
        if args.check:
            logger.info("✅ Verificación completada")
            return

        if args.test:
            if test_vertex_ai_integration():
                logger.info("✅ Integración funcionando correctamente")
            else:
                logger.warning("⚠️ Integración con problemas")
            return

        if args.setup:
            logger.warning("⚠️ Configurando archivos legacy...")
            create_vertex_ai_config()
            create_vertex_ai_client()
            create_env_template()

        # Mostrar guía por defecto
        create_migration_guide()

        logger.info("\n✅ Proceso completado exitosamente!")
        logger.info("\n📋 Próximos pasos:")
        logger.info("1. Configurar variables de entorno (.env)")
        logger.info("2. Configurar Google Cloud credentials")
        logger.info("3. Ejecutar: python scripts/migrate_to_vertex_ai.py --test")
        logger.info("4. Usar vertex_client en tu aplicación")

    except Exception as e:
        logger.error(f"\n❌ Error durante la migración: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
