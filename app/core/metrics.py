"""
Sistema de métricas para monitoreo de rendimiento.
"""

import logging
import threading
import time
from collections import defaultdict, deque
from typing import Any, Deque, Dict, List

from flask import Blueprint, Response, current_app

logger=logging.getLogger(__name__)


class MetricsManager:
    """
    Gestor de métricas de rendimiento, thread-safe, para monitoreo de la aplicación.
    """

    def __init__(self, max_history: int = 1000) -> dict[str, Any]:
        """
        Inicializa el gestor de métricas.

        Args:
            max_history: Número máximo de entradas a mantener en historiales (ej. tiempos de respuesta).
        """
        self.max_history: int = max_history
        self._lock = threading.Lock()

        self.counters: Dict[str, int] = defaultdict(int)
        self.response_times: Deque[float] = deque(maxlen=max_history)
        self.request_history: Deque[Dict[str, Any]] = deque(maxlen=max_history)
        self.start_time: float = time.time()

        logger.info(
            "📈 MetricsManager inicializado con un historial máximo de %d entradas.",
            max_history,
        )

    def increment_counter(self, name: str, value: int = 1) -> dict[str, Any]:
        """Incrementa un contador específico."""
        with self._lock:
            self.counters[name] += value

    def record_response_time(self, duration: float) -> dict[str, Any]:
        """Registra la duración de una respuesta."""
        with self._lock:
            self.response_times.append(duration)

    def record_request(self, endpoint: str, method: str, status_code: int) -> dict[str, Any]:
        """
        Registra una solicitud entrante y actualiza los contadores relacionados.
        """
        with self._lock:
            timestamp=time.time()
            self.request_history.append(
                {
                    "timestamp": timestamp,
                    "endpoint": endpoint,
                    "method": method,
                    "status_code": status_code,
                }
            )
            self.increment_counter("total_requests")
            self.increment_counter(f"requests_method_{method.lower()}")
            self.increment_counter(f"requests_status_{status_code}")
            self.increment_counter(f"requests_endpoint_{endpoint.replace('.', '_')}")

    def get_metrics(self) -> Dict[str, Any]:
        """
        Obtiene un diccionario con todas las métricas actuales.
        """
        with self._lock:
            current_time=time.time()
            uptime=current_time - self.start_time

            response_stats: dict[str, Any] = {}
            if self.response_times:
                times=list(self.response_times)
                response_stats={
                    "avg_seconds": sum(times) / len(times),
                    "min_seconds": min(times),
                    "max_seconds": max(times),
                    "count": len(times),
                }

            recent_requests=[
                req
                for req in self.request_history
                if current_time - req["timestamp"] <= 60
            ]

            return {
                "uptime_seconds": uptime,
                "counters": dict(self.counters),
                "response_time_stats": response_stats,
                "requests_per_minute": len(recent_requests),
                "request_history_count": len(self.request_history),
                "timestamp": current_time,
            }

    def reset_metrics(self) -> None:
        """Reinicia todas las métricas a su estado inicial."""
        with self._lock:
            self.counters.clear()
            self.response_times.clear()
            self.request_history.clear()
            self.start_time = time.time()
        logger.warning("Todas las métricas han sido reseteadas.")


# Instancia global del gestor de métricas
metrics_manager=MetricsManager()

# Blueprint para el endpoint de métricas
metrics_bp=Blueprint("metrics", __name__)


def _format_prometheus_metric(
    name: str,
    value: Any,
    metric_type: str,
    help_text: str,
    labels: Dict[str, str] = None,
) -> str:
    """Formatea una métrica individual para la salida de Prometheus."""
    label_str: str = ""
    if labels:
        label_str: str = "{" + ",".join([f'{k}="{v}"' for k, v in labels.items()]) + "}"

    return f"# HELP {name} {help_text}\n# TYPE {name} {metric_type}\n{name}{label_str} {value}\n"


@metrics_bp.route("/metrics")
def prometheus_metrics() -> None:
    """
    Endpoint que expone las métricas en un formato compatible con Prometheus.
    """
    if current_app.config.get("TESTING", False):
        # Deshabilitar en modo de prueba para no interferir con los tests
        return Response(
            "Métricas deshabilitadas en modo de prueba.", mimetype="text/plain"
        )

    metrics=metrics_manager.get_metrics()
    output: List[str] = []

    # Uptime
    output.append(
        _format_prometheus_metric(
            "gemini_uptime_seconds",
            metrics["uptime_seconds"],
            "gauge",
            "Tiempo de actividad de la aplicación en segundos.",
        )
    )

    # Contadores generales
    for key, value in metrics["counters"].items():
        output.append(
            _format_prometheus_metric(
                f"gemini_{key}", value, "counter", f"Contador para {key}."
            )
        )

    # Estadísticas de tiempo de respuesta
    if "response_time_stats" in metrics and metrics["response_time_stats"]:
        stats=metrics["response_time_stats"]
        output.append(
            _format_prometheus_metric(
                "gemini_response_time_avg_seconds",
                stats["avg_seconds"],
                "gauge",
                "Tiempo de respuesta promedio.",
            )
        )
        output.append(
            _format_prometheus_metric(
                "gemini_response_time_max_seconds",
                stats["max_seconds"],
                "gauge",
                "Tiempo de respuesta máximo.",
            )
        )

    # Solicitudes por minuto
    output.append(
        _format_prometheus_metric(
            "gemini_requests_per_minute",
            metrics["requests_per_minute"],
            "gauge",
            "Número de solicitudes en los últimos 60 segundos.",
        )
    )

    return Response("\n".join(output), mimetype="text/plain; version=0.0.4")