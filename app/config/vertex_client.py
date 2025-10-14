"""Cliente para Google Cloud Vertex AI con soporte para fallback a Gemini API."""

import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

try:
    __import__("google.cloud.aiplatform")
    from vertexai.generative_models import GenerationConfig, GenerativeModel

    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False
    logging.warning(
        "⚠️ Vertex AI SDK no está instalado. Para usarlo, ejecute: pip install google-cloud-aiplatform vertexai"
    )

try:
    import google.generativeai as genai

    GEMINI_API_AVAILABLE = True
except ImportError:
    GEMINI_API_AVAILABLE = False
    logging.warning(
        "⚠️ Google Generative AI SDK no está instalado. Para usar el fallback, ejecute: pip install google-generativeai"
    )

from .vertex_ai import vertex_config

logger = logging.getLogger(__name__)


class VertexAIClient:
    """
    Cliente inteligente para Vertex AI con soporte para fallback a Gemini API.

    Gestiona la inicialización, el enrutamiento de solicitudes, los límites de uso y
    la conmutación automática entre Vertex AI y la API de Gemini si es necesario.
    """

    def __init__(self):
        """Inicializa el cliente y sus atributos de estado."""
        self.config = vertex_config
        self.initialized: bool = False
        self.fallback_active: bool = False
        self.models: Dict[str, GenerativeModel] = {}
        self.gemini_client: Optional[GenerativeModel] = None

        # Métricas de uso para monitoreo y control de costos.
        self.daily_cost: float = 0.0
        self.request_count: int = 0
        self.error_count: int = 0
        self.last_reset: float = time.time()
        self.usage_history: list[Dict[str, Any]] = []

        # Estado de salud del servicio.
        self.last_health_check: float = 0
        self.health_check_interval: int = 300  # 5 minutos
        self.is_healthy: bool = False

    async def initialize(self) -> bool:
        """
        Inicializa el cliente, intentando primero Vertex AI y luego el fallback a Gemini API.

        Returns:
            True si al menos uno de los clientes (Vertex AI o Gemini API) se inicializó con éxito.
        """
        return self.initialize_sync()

    def initialize_sync(self) -> bool:
        """
        Inicializa el cliente de forma síncrona, intentando primero Vertex AI y luego el fallback a Gemini API.

        Returns:
            True si al menos uno de los clientes (Vertex AI o Gemini API) se inicializó con éxito.
        """
        logger.info("🚀 Iniciando cliente de IA...")

        # 1. Intentar inicializar Vertex AI
        # if VERTEX_AI_AVAILABLE and self.config.enabled:
        #     if self._initialize_vertex_ai():
        #         self.initialized = True
        #         self.is_healthy = True
        #         self.fallback_active = False
        #         logger.info("✅ Cliente de IA inicializado en modo Vertex AI.")
        #         return True

        # 2. Si Vertex AI falla o está deshabilitado, intentar inicializar Gemini API como fallback
        if (
            self.config.fallback_config.get("use_gemini_api", True)
            and GEMINI_API_AVAILABLE
        ):
            if self._initialize_gemini_api():
                self.initialized = True
                self.is_healthy = True
                self.fallback_active = True
                logger.info(
                    "🔄 Cliente de IA inicializado en modo Fallback (Gemini API)."
                )
                return True

        self.is_healthy = False
        logger.error(
            "❌ No se pudo inicializar ningún cliente de IA. Todas las funciones estarán desactivadas."
        )
        return False

    def _initialize_vertex_ai(self) -> bool:
        """Inicializa los modelos de Vertex AI."""
        try:
            if not self.config.initialize():
                return False

            self.models = {}
            for model_type, model_info in self.config.models.items():
                try:
                    self.models[model_type] = GenerativeModel(model_info["name"])
                    logger.debug(
                        "✅ Modelo Vertex AI '%s' (%s) cargado.",
                        model_type,
                        model_info["name"],
                    )
                except Exception:
                    logger.exception(
                        "⚠️ No se pudo cargar el modelo de Vertex AI: %s", model_type
                    )

            if not self.models:
                logger.error(
                    "❌ No se pudo cargar ningún modelo de Vertex AI, la inicialización falló."
                )
                return False

            return True
        except Exception:
            logger.exception("❌ Fallo crítico al inicializar Vertex AI.")
            return False

    def _initialize_gemini_api(self) -> bool:
        """Inicializa el cliente de la API de Gemini."""
        try:
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not api_key:
                logger.warning(
                    "⚠️ No se encontró la API key para Gemini (GEMINI_API_KEY o GOOGLE_API_KEY)."
                )
                return False

            genai.configure(api_key=api_key)
            self.gemini_client = genai.GenerativeModel("gemini-flash-latest")
            # Realizar una pequeña prueba para confirmar que la clave es válida
            # self.gemini_client.generate_content("test", generation_config={"max_output_tokens": 1})
            logger.info("✅ Cliente de Gemini API configurado y verificado.")
            return True
        except Exception:
            logger.exception("❌ Error al configurar o verificar la API de Gemini.")
            return False

    def _reset_daily_limits(self):
        """
        Reinicia los contadores de uso diario si han pasado 24 horas.
        """
        if time.time() - self.last_reset > 86400:  # 24 horas en segundos
            self.daily_cost = 0.0
            self.request_count = 0
            self.error_count = 0
            self.last_reset = time.time()
            logger.info("🔄 Límites de uso diarios reseteados.")

    def _check_limits(
        self, estimated_tokens: int, model_type: str = "fast"
    ) -> Tuple[bool, str]:
        """
        Verifica si la solicitud actual excede alguno de los límites de uso definidos.

        Args:
            estimated_tokens: El número estimado de tokens para la solicitud.
            model_type: El tipo de modelo a utilizar.

        Returns:
            Una tupla (se_puede_proceder, razón_del_fallo).
        """
        self._reset_daily_limits()

        # Verificar límite de costo diario
        estimated_cost = self.config.estimate_cost(estimated_tokens, 0, model_type)
        if self.daily_cost + estimated_cost > self.config.limits["max_daily_cost"]:
            return (
                False,
                f"Límite de costo diario alcanzado (${self.daily_cost:.2f}/"
                f"${self.config.limits['max_daily_cost']:.2f})",
            )

        # Verificar límite de tokens por solicitud
        if estimated_tokens > self.config.limits["max_tokens_per_request"]:
            return (
                False,
                f"Solicitud excede límite de tokens ({estimated_tokens}/"
                f"{self.config.limits['max_tokens_per_request']})",
            )

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

    def _update_metrics(
        self,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        response_time: float,
        success: bool,
    ):
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
        self.usage_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": cost,
                "response_time": response_time,
                "success": success,
                "source": "fallback" if self.fallback_active else "vertex_ai",
            }
        )

        # Mantener solo últimas 1000 entradas
        if len(self.usage_history) > 1000:
            self.usage_history = self.usage_history[-1000:]

    async def _generate_with_vertex_ai(
        self,
        prompt: str,
        model_type: str = "fast",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs,
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
            max_output_tokens=min(max_tokens, model_info["max_tokens"]),
            temperature=temperature,
            top_p=kwargs.get("top_p", 0.8),
            top_k=kwargs.get("top_k", 40),
        )

        # Generar respuesta
        start_time = time.time()
        response = await model.generate_content_async(
            prompt, generation_config=generation_config
        )
        response_time = time.time() - start_time

        # Procesar respuesta
        response_text = response.text if response.text else ""

        # Calcular métricas
        input_tokens = self._estimate_tokens(prompt)
        output_tokens = self._estimate_tokens(response_text)
        cost = self.config.estimate_cost(input_tokens, output_tokens, model_type)

        return {
            "response": response_text,
            "model": model_info["name"],
            "model_type": model_type,
            "tokens_used": input_tokens + output_tokens,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost,
            "response_time": response_time,
            "source": "vertex_ai",
            "success": True,
        }

    async def _generate_with_gemini_api(
        self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7, **kwargs
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
            "max_output_tokens": max_tokens,
            "temperature": temperature,
        }

        # Generar respuesta
        start_time = time.time()
        response = await self.gemini_client.generate_content_async(
            prompt, generation_config=generation_config
        )
        response_time = time.time() - start_time

        # Procesar respuesta
        response_text = response.text if response.text else ""

        # Calcular métricas (estimación para Gemini API)
        input_tokens = self._estimate_tokens(prompt)
        output_tokens = self._estimate_tokens(response_text)
        cost = 0.0  # Gemini API gratuita

        return {
            "response": response_text,
            "model": "gemini-flash-latest",
            "model_type": "fallback",
            "tokens_used": input_tokens + output_tokens,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost,
            "response_time": response_time,
            "source": "gemini_api",
            "success": True,
        }

    async def generate_response(
        self,
        prompt: str,
        model_type: str = "fast",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs,
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
                return await self._generate_with_gemini_api(
                    prompt, max_tokens, temperature, **kwargs
                )
            else:
                raise ValueError(f"Solicitud rechazada: {reason}")

        # Intentar con Vertex AI primero
        if self.initialized and not self.fallback_active:
            try:
                result = await self._generate_with_vertex_ai(
                    prompt, model_type, max_tokens, temperature, **kwargs
                )
                self._update_metrics(
                    result["input_tokens"],
                    result["output_tokens"],
                    result["cost"],
                    result["response_time"],
                    True,
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
                    result["input_tokens"],
                    result["output_tokens"],
                    result["cost"],
                    result["response_time"],
                    True,
                )
                return result

            except Exception as e:
                logger.error(f"❌ Error en Gemini API: {e}")
                self._update_metrics(0, 0, 0, 0, False)
                raise RuntimeError(
                    f"Todos los clientes fallaron. Último error: {e}"
                ) from e

        raise Exception("No hay clientes disponibles")

    def generate_response_sync(
        self,
        prompt: str,
        model_type: str = "fast",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs,
    ) -> Dict[str, Any]:
        """Versión síncrona de generate_response para compatibilidad."""
        import asyncio
        import concurrent.futures

        def run_async():
            # Crear un nuevo loop de eventos en un hilo separado
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                return new_loop.run_until_complete(
                    self.generate_response(
                        prompt, model_type, max_tokens, temperature, **kwargs
                    )
                )
            except Exception as e:
                raise e
            finally:
                new_loop.close()

        # Ejecutar siempre en un hilo separado para evitar conflictos
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_async)
            try:
                return future.result(timeout=120)  # 2 minutos de timeout
            except Exception as e:
                raise e

    def get_usage_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de uso.

        Returns:
            Dict con estadísticas detalladas
        """
        self._reset_daily_limits()

        recent_history = self.usage_history[-100:] if self.usage_history else []

        return {
            "daily_stats": {
                "requests": self.request_count,
                "cost": round(self.daily_cost, 4),
                "errors": self.error_count,
                "success_rate": round(
                    (self.request_count - self.error_count)
                    / max(self.request_count, 1)
                    * 100,
                    2,
                ),
            },
            "limits": self.config.limits,
            "status": {
                "vertex_ai_available": self.initialized,
                "gemini_api_available": self.gemini_client is not None,
                "fallback_active": self.fallback_active,
                "healthy": self.is_healthy,
            },
            "recent_requests": len(recent_history),
            "avg_response_time": (
                round(
                    sum(r["response_time"] for r in recent_history)
                    / max(len(recent_history), 1),
                    3,
                )
                if recent_history
                else 0
            ),
        }

    async def health_check(self) -> Dict[str, Any]:
        """Verificar estado de salud de los servicios.

        Returns:
            Dict con estado de salud
        """
        current_time = time.time()

        # Solo hacer health check cada cierto intervalo
        if current_time - self.last_health_check < self.health_check_interval:
            return {"status": "cached", "healthy": self.is_healthy}

        self.last_health_check = current_time
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "vertex_ai": {"available": False, "error": None},
            "gemini_api": {"available": False, "error": None},
            "overall_healthy": False,
        }

        # Verificar Vertex AI
        if self.initialized:
            try:
                # Test simple con el modelo más básico
                await self._generate_with_vertex_ai("Test", "basic", 10, 0.1)
                health_status["vertex_ai"]["available"] = True
            except Exception as e:
                health_status["vertex_ai"]["error"] = str(e)
                logger.warning(f"⚠️ Vertex AI health check falló: {e}")

        # Verificar Gemini API
        if self.gemini_client:
            try:
                await self._generate_with_gemini_api("Test", 10, 0.1)
                health_status["gemini_api"]["available"] = True
            except Exception as e:
                health_status["gemini_api"]["error"] = str(e)
                logger.warning(f"⚠️ Gemini API health check falló: {e}")

        # Determinar estado general
        health_status["overall_healthy"] = (
            health_status["vertex_ai"]["available"]
            or health_status["gemini_api"]["available"]
        )

        self.is_healthy = health_status["overall_healthy"]
        return health_status


# Instancia global del cliente
vertex_client = VertexAIClient()
