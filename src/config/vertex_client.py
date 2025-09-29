"""Cliente para Google Cloud Vertex AI con fallback automático."""

import asyncio
import json
import time
import logging
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta

try:
    from google.cloud import aiplatform
    from vertexai.generative_models import GenerativeModel, GenerationConfig
    import vertexai
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False
    logging.warning("⚠️ Vertex AI no disponible - instalar: pip install google-cloud-aiplatform vertexai")

try:
    import google.generativeai as genai
    GEMINI_API_AVAILABLE = True
except ImportError:
    GEMINI_API_AVAILABLE = False
    logging.warning("⚠️ Gemini API no disponible - instalar: pip install google-generativeai")

from .vertex_ai import vertex_config

logger = logging.getLogger(__name__)

class VertexAIClient:
    """Cliente inteligente para Vertex AI con fallback automático."""
    
    def __init__(self):
        self.config = vertex_config
        self.initialized = False
        self.fallback_active = False
        self.models = {}
        self.gemini_client = None
        
        # Métricas de uso
        self.daily_cost = 0.0
        self.request_count = 0
        self.error_count = 0
        self.last_reset = time.time()
        self.usage_history = []
        
        # Estado de conexión
        self.last_health_check = 0
        self.health_check_interval = 300  # 5 minutos
        self.is_healthy = False
    
    async def initialize(self) -> bool:
        """Inicializar cliente Vertex AI con fallback.
        
        Returns:
            bool: True si al menos un cliente está disponible
        """
        vertex_success = False
        gemini_success = False
        
        # Intentar inicializar Vertex AI
        if VERTEX_AI_AVAILABLE and self.config.enabled:
            try:
                if self.config.initialize():
                    # Inicializar Vertex AI
                    vertexai.init(
                        project=self.config.project_id,
                        location=self.config.location
                    )
                    
                    # Crear modelos
                    self.models = {}
                    for model_type, model_info in self.config.models.items():
                        try:
                            self.models[model_type] = GenerativeModel(model_info['name'])
                            logger.debug(f"✅ Modelo {model_type} ({model_info['name']}) cargado")
                        except Exception as e:
                            logger.warning(f"⚠️ Error cargando modelo {model_type}: {e}")
                    
                    if self.models:
                        self.initialized = True
                        vertex_success = True
                        logger.info("✅ Vertex AI inicializado correctamente")
                    else:
                        logger.error("❌ No se pudieron cargar modelos de Vertex AI")
                        
            except Exception as e:
                logger.error(f"❌ Error inicializando Vertex AI: {e}")
        
        # Configurar fallback a Gemini API
        if GEMINI_API_AVAILABLE:
            try:
                import os
                api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
                if api_key:
                    genai.configure(api_key=api_key)
                    self.gemini_client = genai.GenerativeModel('gemini-pro')
                    gemini_success = True
                    logger.info("✅ Gemini API configurado como fallback")
                else:
                    logger.warning("⚠️ No se encontró API key para Gemini")
            except Exception as e:
                logger.error(f"❌ Error configurando Gemini API: {e}")
        
        # Determinar estado final
        if vertex_success:
            self.fallback_active = False
            self.is_healthy = True
        elif gemini_success:
            self.fallback_active = True
            self.is_healthy = True
            logger.info("🔄 Usando Gemini API como fallback principal")
        else:
            self.is_healthy = False
            logger.error("❌ No se pudo inicializar ningún cliente de IA")
        
        return self.is_healthy
    
    def _reset_daily_limits(self):
        """Resetear límites diarios."""
        current_time = time.time()
        if current_time - self.last_reset > 86400:  # 24 horas
            self.daily_cost = 0.0
            self.request_count = 0
            self.error_count = 0
            self.last_reset = current_time
            logger.info("🔄 Límites diarios reseteados")
    
    def _check_limits(self, estimated_tokens: int, model_type: str = 'fast') -> tuple[bool, str]:
        """Verificar límites de uso.
        
        Args:
            estimated_tokens: Tokens estimados para la solicitud
            model_type: Tipo de modelo
            
        Returns:
            tuple: (can_proceed, reason)
        """
        self._reset_daily_limits()
        
        # Verificar límite de costo diario
        estimated_cost = self.config.estimate_cost(estimated_tokens, 0, model_type)
        if self.daily_cost + estimated_cost > self.config.limits['max_daily_cost']:
            return False, f"Límite de costo diario alcanzado (${self.daily_cost:.2f}/${self.config.limits['max_daily_cost']:.2f})"
        
        # Verificar límite de tokens por solicitud
        if estimated_tokens > self.config.limits['max_tokens_per_request']:
            return False, f"Solicitud excede límite de tokens ({estimated_tokens}/{self.config.limits['max_tokens_per_request']})"
        
        return True, "OK"
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimar número de tokens en un texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            int: Número estimado de tokens
        """
        # Estimación simple: ~1.3 tokens por palabra
        words = len(text.split())
        return int(words * 1.3)
    
    def _update_metrics(self, input_tokens: int, output_tokens: int, cost: float, response_time: float, success: bool):
        """Actualizar métricas de uso.
        
        Args:
            input_tokens: Tokens de entrada
            output_tokens: Tokens de salida
            cost: Costo de la solicitud
            response_time: Tiempo de respuesta
            success: Si la solicitud fue exitosa
        """
        self.request_count += 1
        self.daily_cost += cost
        
        if not success:
            self.error_count += 1
        
        # Guardar en historial
        self.usage_history.append({
            'timestamp': datetime.now().isoformat(),
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost': cost,
            'response_time': response_time,
            'success': success,
            'source': 'fallback' if self.fallback_active else 'vertex_ai'
        })
        
        # Mantener solo últimas 1000 entradas
        if len(self.usage_history) > 1000:
            self.usage_history = self.usage_history[-1000:]
    
    async def _generate_with_vertex_ai(
        self,
        prompt: str,
        model_type: str = 'fast',
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """Generar respuesta con Vertex AI.
        
        Args:
            prompt: Texto de entrada
            model_type: Tipo de modelo
            max_tokens: Máximo de tokens de salida
            temperature: Temperatura de generación
            **kwargs: Parámetros adicionales
            
        Returns:
            Dict con la respuesta y metadatos
        """
        if not self.initialized or model_type not in self.models:
            raise Exception(f"Modelo {model_type} no disponible")
        
        model = self.models[model_type]
        model_info = self.config.get_model_info(model_type)
        
        # Configurar generación
        generation_config = GenerationConfig(
            max_output_tokens=min(max_tokens, model_info['max_tokens']),
            temperature=temperature,
            top_p=kwargs.get('top_p', 0.8),
            top_k=kwargs.get('top_k', 40)
        )
        
        # Generar respuesta
        start_time = time.time()
        response = await model.generate_content_async(
            prompt,
            generation_config=generation_config
        )
        response_time = time.time() - start_time
        
        # Procesar respuesta
        response_text = response.text if response.text else ""
        
        # Calcular métricas
        input_tokens = self._estimate_tokens(prompt)
        output_tokens = self._estimate_tokens(response_text)
        cost = self.config.estimate_cost(input_tokens, output_tokens, model_type)
        
        return {
            'response': response_text,
            'model': model_info['name'],
            'model_type': model_type,
            'tokens_used': input_tokens + output_tokens,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost': cost,
            'response_time': response_time,
            'source': 'vertex_ai',
            'success': True
        }
    
    async def _generate_with_gemini_api(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """Generar respuesta con Gemini API (fallback).
        
        Args:
            prompt: Texto de entrada
            max_tokens: Máximo de tokens de salida
            temperature: Temperatura de generación
            **kwargs: Parámetros adicionales
            
        Returns:
            Dict con la respuesta y metadatos
        """
        if not self.gemini_client:
            raise Exception("Gemini API no disponible")
        
        # Configurar generación
        generation_config = {
            'max_output_tokens': max_tokens,
            'temperature': temperature,
        }
        
        # Generar respuesta
        start_time = time.time()
        response = await self.gemini_client.generate_content_async(
            prompt,
            generation_config=generation_config
        )
        response_time = time.time() - start_time
        
        # Procesar respuesta
        response_text = response.text if response.text else ""
        
        # Calcular métricas (estimación para Gemini API)
        input_tokens = self._estimate_tokens(prompt)
        output_tokens = self._estimate_tokens(response_text)
        cost = 0.0  # Gemini API gratuita
        
        return {
            'response': response_text,
            'model': 'gemini-pro',
            'model_type': 'fallback',
            'tokens_used': input_tokens + output_tokens,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost': cost,
            'response_time': response_time,
            'source': 'gemini_api',
            'success': True
        }
    
    async def generate_response(
        self,
        prompt: str,
        model_type: str = 'fast',
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """Generar respuesta con fallback automático.
        
        Args:
            prompt: Texto de entrada
            model_type: Tipo de modelo ('fast', 'pro', 'basic')
            max_tokens: Máximo de tokens de salida
            temperature: Temperatura de generación (0.0-1.0)
            **kwargs: Parámetros adicionales
            
        Returns:
            Dict con la respuesta y metadatos
        """
        if not self.is_healthy:
            await self.initialize()
        
        if not self.is_healthy:
            raise Exception("No hay clientes de IA disponibles")
        
        # Estimar tokens y verificar límites
        estimated_tokens = self._estimate_tokens(prompt) + max_tokens
        can_proceed, reason = self._check_limits(estimated_tokens, model_type)
        
        if not can_proceed:
            logger.warning(f"⚠️ Solicitud rechazada: {reason}")
            # Si es por límites de costo, intentar con fallback
            if "costo" in reason.lower() and not self.fallback_active:
                logger.info("🔄 Intentando con Gemini API por límites de costo")
                return await self._generate_with_gemini_api(prompt, max_tokens, temperature, **kwargs)
            else:
                raise Exception(f"Solicitud rechazada: {reason}")
        
        # Intentar con Vertex AI primero
        if self.initialized and not self.fallback_active:
            try:
                result = await self._generate_with_vertex_ai(
                    prompt, model_type, max_tokens, temperature, **kwargs
                )
                self._update_metrics(
                    result['input_tokens'],
                    result['output_tokens'],
                    result['cost'],
                    result['response_time'],
                    True
                )
                return result
                
            except Exception as e:
                logger.error(f"❌ Error en Vertex AI: {e}")
                logger.info("🔄 Cambiando a Gemini API")
                self.fallback_active = True
        
        # Usar Gemini API como fallback
        if self.gemini_client:
            try:
                result = await self._generate_with_gemini_api(
                    prompt, max_tokens, temperature, **kwargs
                )
                self._update_metrics(
                    result['input_tokens'],
                    result['output_tokens'],
                    result['cost'],
                    result['response_time'],
                    True
                )
                return result
                
            except Exception as e:
                logger.error(f"❌ Error en Gemini API: {e}")
                self._update_metrics(0, 0, 0, 0, False)
                raise Exception(f"Todos los clientes fallaron. Último error: {e}")
        
        raise Exception("No hay clientes disponibles")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de uso.
        
        Returns:
            Dict con estadísticas detalladas
        """
        self._reset_daily_limits()
        
        recent_history = self.usage_history[-100:] if self.usage_history else []
        
        return {
            'daily_stats': {
                'requests': self.request_count,
                'cost': round(self.daily_cost, 4),
                'errors': self.error_count,
                'success_rate': round((self.request_count - self.error_count) / max(self.request_count, 1) * 100, 2)
            },
            'limits': self.config.limits,
            'status': {
                'vertex_ai_available': self.initialized,
                'gemini_api_available': self.gemini_client is not None,
                'fallback_active': self.fallback_active,
                'healthy': self.is_healthy
            },
            'recent_requests': len(recent_history),
            'avg_response_time': round(
                sum(r['response_time'] for r in recent_history) / max(len(recent_history), 1), 3
            ) if recent_history else 0
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Verificar estado de salud de los servicios.
        
        Returns:
            Dict con estado de salud
        """
        current_time = time.time()
        
        # Solo hacer health check cada cierto intervalo
        if current_time - self.last_health_check < self.health_check_interval:
            return {'status': 'cached', 'healthy': self.is_healthy}
        
        self.last_health_check = current_time
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'vertex_ai': {'available': False, 'error': None},
            'gemini_api': {'available': False, 'error': None},
            'overall_healthy': False
        }
        
        # Verificar Vertex AI
        if self.initialized:
            try:
                # Test simple con el modelo más básico
                test_result = await self._generate_with_vertex_ai(
                    "Test", 'basic', 10, 0.1
                )
                health_status['vertex_ai']['available'] = True
            except Exception as e:
                health_status['vertex_ai']['error'] = str(e)
                logger.warning(f"⚠️ Vertex AI health check falló: {e}")
        
        # Verificar Gemini API
        if self.gemini_client:
            try:
                test_result = await self._generate_with_gemini_api(
                    "Test", 10, 0.1
                )
                health_status['gemini_api']['available'] = True
            except Exception as e:
                health_status['gemini_api']['error'] = str(e)
                logger.warning(f"⚠️ Gemini API health check falló: {e}")
        
        # Determinar estado general
        health_status['overall_healthy'] = (
            health_status['vertex_ai']['available'] or 
            health_status['gemini_api']['available']
        )
        
        self.is_healthy = health_status['overall_healthy']
        return health_status

# Instancia global del cliente
vertex_client = VertexAIClient()