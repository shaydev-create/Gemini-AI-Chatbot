"""
Sistema de métricas para monitoreo de rendimiento.
"""

import time
import threading
from collections import defaultdict, deque
from typing import Dict, Any
from flask import Blueprint, Response


class MetricsManager:
    """Gestor de métricas de rendimiento."""

    def __init__(self, max_history: int = 1000):
        """
        Inicializar el gestor de métricas.

        Args:
            max_history: Máximo número de entradas en el historial
        """
        self.max_history = max_history
        self.lock = threading.Lock()

        # Contadores
        self.counters = defaultdict(int)

        # Tiempos de respuesta
        self.response_times = deque(maxlen=max_history)

        # Historial de requests
        self.request_history = deque(maxlen=max_history)

        # Tiempo de inicio
        self.start_time = time.time()

    def increment_counter(self, name: str, value: int = 1) -> None:
        """
        Incrementar un contador.

        Args:
            name: Nombre del contador
            value: Valor a incrementar
        """
        with self.lock:
            self.counters[name] += value

    def record_response_time(self, duration: float) -> None:
        """
        Registrar tiempo de respuesta.

        Args:
            duration: Duración en segundos
        """
        with self.lock:
            self.response_times.append(duration)

    def record_request(self, endpoint: str, method: str, status_code: int) -> None:
        """
        Registrar una request.

        Args:
            endpoint: Endpoint solicitado
            method: Método HTTP
            status_code: Código de estado
        """
        with self.lock:
            self.request_history.append(
                {
                    "timestamp": time.time(),
                    "endpoint": endpoint,
                    "method": method,
                    "status_code": status_code,
                }
            )

            # Incrementar contadores
            self.increment_counter("total_requests")
            self.increment_counter(f"requests_{method.lower()}")
            self.increment_counter(f"status_{status_code}")

    def get_metrics(self) -> Dict[str, Any]:
        """
        Obtener todas las métricas.

        Returns:
            Dict con métricas actuales
        """
        with self.lock:
            current_time = time.time()
            uptime = current_time - self.start_time

            # Calcular estadísticas de tiempo de respuesta
            response_stats = {}
            if self.response_times:
                times = list(self.response_times)
                response_stats = {
                    "avg": sum(times) / len(times),
                    "min": min(times),
                    "max": max(times),
                    "count": len(times),
                }

            # Requests por minuto (últimos 60 segundos)
            recent_requests = [
                req
                for req in self.request_history
                if current_time - req["timestamp"] <= 60
            ]

            return {
                "uptime_seconds": uptime,
                "counters": dict(self.counters),
                "response_times": response_stats,
                "requests_per_minute": len(recent_requests),
                "total_requests_history": len(self.request_history),
                "timestamp": current_time,
            }

    def reset_metrics(self) -> None:
        """Reiniciar todas las métricas."""
        with self.lock:
            self.counters.clear()
            self.response_times.clear()
            self.request_history.clear()
            self.start_time = time.time()


# Instancia global del gestor de métricas
metrics_manager = MetricsManager()

metrics_bp = Blueprint("metrics", __name__)


@metrics_bp.route("/metrics")
def prometheus_metrics():
    metrics = metrics_manager.get_metrics()
    output = []
    # Contadores
    for key, value in metrics["counters"].items():
        output.append(f"gemini_{key} {value}")
    # Requests por minuto
    output.append(
        f"gemini_requests_per_minute {
            metrics['requests_per_minute']}"
    )
    # Uptime
    output.append(f"gemini_uptime_seconds {metrics['uptime_seconds']}")
    # Tiempos de respuesta
    if metrics["response_times"]:
        output.append(
            f"gemini_response_time_avg {
                metrics['response_times']['avg']}"
        )
        output.append(
            f"gemini_response_time_min {
                metrics['response_times']['min']}"
        )
        output.append(
            f"gemini_response_time_max {
                metrics['response_times']['max']}"
        )
        output.append(
            f"gemini_response_time_count {
                metrics['response_times']['count']}"
        )
    return Response("\n".join(output), mimetype="text/plain")
