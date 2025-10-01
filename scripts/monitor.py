#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 SISTEMA DE MONITOREO - GEMINI AI CHATBOT

Sistema completo de monitoreo y métricas para la aplicación:
- Health checks avanzados
- Métricas de performance
- Alertas automáticas
- Dashboard de estadísticas
"""

from src.models import db, User, ChatSession
from app import create_app
import os
import sys
import time
import psutil
import requests
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any
from dataclasses import dataclass

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class HealthStatus:
    """Estado de salud de un componente."""
    name: str
    status: str
    response_time: float
    details: Dict[str, Any]
    timestamp: datetime


class SystemMonitor:
    """Monitor del sistema con métricas avanzadas."""

    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.app = create_app()
        self.alerts = []

    def check_application_health(self) -> HealthStatus:
        """Verificar salud de la aplicación."""
        start_time = time.time()

        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                data = response.json()
                return HealthStatus(
                    name="application",
                    status="healthy",
                    response_time=response_time,
                    details=data,
                    timestamp=datetime.now(timezone.utc)
                )
            else:
                return HealthStatus(
                    name="application",
                    status="unhealthy",
                    response_time=response_time,
                    details={"error": f"HTTP {response.status_code}"},
                    timestamp=datetime.now(timezone.utc)
                )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthStatus(
                name="application",
                status="error",
                response_time=response_time,
                details={"error": str(e)},
                timestamp=datetime.now(timezone.utc)
            )

    def check_database_health(self) -> HealthStatus:
        """Verificar salud de la base de datos."""
        start_time = time.time()

        try:
            with self.app.app_context():
                # Test simple query
                user_count = User.query.count()
                response_time = (time.time() - start_time) * 1000

                return HealthStatus(
                    name="database",
                    status="healthy",
                    response_time=response_time,
                    details={"user_count": user_count},
                    timestamp=datetime.now(timezone.utc)
                )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthStatus(
                name="database",
                status="error",
                response_time=response_time,
                details={"error": str(e)},
                timestamp=datetime.now(timezone.utc)
            )

    def check_system_resources(self) -> HealthStatus:
        """Verificar recursos del sistema."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # Determinar estado basado en uso de recursos
            status = "healthy"
            if cpu_percent > 80 or memory.percent > 85 or disk.percent > 90:
                status = "warning"
            if cpu_percent > 95 or memory.percent > 95 or disk.percent > 95:
                status = "critical"

            return HealthStatus(
                name="system_resources",
                status=status,
                response_time=0,
                details={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available": memory.available,
                    "disk_percent": disk.percent,
                    "disk_free": disk.free
                },
                timestamp=datetime.now(timezone.utc)
            )

        except Exception as e:
            return HealthStatus(
                name="system_resources",
                status="error",
                response_time=0,
                details={"error": str(e)},
                timestamp=datetime.now(timezone.utc)
            )

    def check_ssl_certificates(self) -> HealthStatus:
        """Verificar certificados SSL."""
        try:
            import ssl
            import socket
            from datetime import datetime

            # Verificar certificado local
            cert_path = "ssl/cert.pem"
            if os.path.exists(cert_path):
                with open(cert_path, 'r') as f:
                    cert_data = f.read()

                # Aquí se podría agregar validación más avanzada
                return HealthStatus(
                    name="ssl_certificates",
                    status="healthy",
                    response_time=0,
                    details={"certificate_exists": True},
                    timestamp=datetime.now(timezone.utc)
                )
            else:
                return HealthStatus(
                    name="ssl_certificates",
                    status="warning",
                    response_time=0,
                    details={"certificate_exists": False},
                    timestamp=datetime.now(timezone.utc)
                )

        except Exception as e:
            return HealthStatus(
                name="ssl_certificates",
                status="error",
                response_time=0,
                details={"error": str(e)},
                timestamp=datetime.now(timezone.utc)
            )

    def get_application_metrics(self) -> Dict[str, Any]:
        """Obtener métricas de la aplicación."""
        try:
            with self.app.app_context():
                metrics = {
                    "users": {
                        "total": User.query.count(),
                        "active": User.query.filter_by(
                            status='active').count(),
                        "verified": User.query.filter_by(
                            email_verified=True).count()},
                    "sessions": {
                        "total": ChatSession.query.count(),
                        "active": ChatSession.query.filter_by(
                            status='active').count()},
                    "system": {
                        "uptime": time.time() -
                        psutil.boot_time(),
                        "cpu_count": psutil.cpu_count(),
                        "memory_total": psutil.virtual_memory().total}}

                return metrics

        except Exception as e:
            logger.error(f"Error obteniendo métricas: {e}")
            return {}

    def run_health_checks(self) -> List[HealthStatus]:
        """Ejecutar todos los health checks."""
        checks = [
            self.check_application_health(),
            self.check_database_health(),
            self.check_system_resources(),
            self.check_ssl_certificates()
        ]

        return checks

    def generate_alert(self, check: HealthStatus):
        """Generar alerta si es necesario."""
        if check.status in ['warning', 'critical', 'error']:
            alert = {
                'timestamp': check.timestamp,
                'component': check.name,
                'status': check.status,
                'details': check.details,
                'response_time': check.response_time
            }

            self.alerts.append(alert)
            logger.warning(f"🚨 ALERTA: {check.name} - {check.status}")

            # Aquí se podría enviar notificación por email, Slack, etc.

    def print_status_report(self, checks: List[HealthStatus]):
        """Imprimir reporte de estado."""
        print("\n" + "=" * 60)
        print("📊 REPORTE DE ESTADO DEL SISTEMA")
        print("=" * 60)
        print(f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        for check in checks:
            status_emoji = {
                'healthy': '✅',
                'warning': '⚠️',
                'critical': '🔴',
                'error': '❌'
            }.get(check.status, '❓')

            print(f"{status_emoji} {check.name.upper()}: {check.status}")
            if check.response_time > 0:
                print(
                    f"   ⏱️ Tiempo de respuesta: {
                        check.response_time:.2f}ms")

            if check.details:
                for key, value in check.details.items():
                    if isinstance(value, (int, float)):
                        if 'percent' in key:
                            print(f"   📊 {key}: {value:.1f}%")
                        elif 'bytes' in key or 'available' in key or 'free' in key:
                            print(
                                f"   💾 {key}: {
                                    value /
                                    1024 /
                                    1024 /
                                    1024:.2f} GB")
                        else:
                            print(f"   📈 {key}: {value}")
                    else:
                        print(f"   ℹ️ {key}: {value}")
            print()

        # Mostrar métricas adicionales
        metrics = self.get_application_metrics()
        if metrics:
            print("📈 MÉTRICAS DE LA APLICACIÓN:")
            print(
                f"   👥 Usuarios totales: {
                    metrics.get(
                        'users',
                        {}).get(
                        'total',
                        0)}")
            print(
                f"   ✅ Usuarios activos: {
                    metrics.get(
                        'users',
                        {}).get(
                        'active',
                        0)}")
            print(
                f"   💬 Sesiones totales: {
                    metrics.get(
                        'sessions',
                        {}).get(
                        'total',
                        0)}")
            print(
                f"   🔄 Sesiones activas: {
                    metrics.get(
                        'sessions',
                        {}).get(
                        'active',
                        0)}")

        print("=" * 60)

    def monitor_continuously(self, interval: int = 300):
        """Monitoreo continuo del sistema."""
        logger.info(f"🔄 Iniciando monitoreo continuo (intervalo: {interval}s)")

        try:
            while True:
                checks = self.run_health_checks()

                # Generar alertas si es necesario
                for check in checks:
                    self.generate_alert(check)

                # Log del estado
                healthy_count = sum(1 for c in checks if c.status == 'healthy')
                total_count = len(checks)

                logger.info(
                    f"📊 Health checks: {healthy_count}/{total_count} healthy")

                # Esperar hasta el próximo check
                time.sleep(interval)

        except KeyboardInterrupt:
            logger.info("🛑 Monitoreo detenido por el usuario")
        except Exception as e:
            logger.error(f"❌ Error en monitoreo: {e}")


def main():
    """Función principal."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Sistema de monitoreo Gemini AI Chatbot')
    parser.add_argument(
        '--url',
        default='http://localhost:5000',
        help='URL base de la aplicación')
    parser.add_argument(
        '--continuous',
        action='store_true',
        help='Monitoreo continuo')
    parser.add_argument(
        '--interval',
        type=int,
        default=300,
        help='Intervalo en segundos para monitoreo continuo')

    args = parser.parse_args()

    monitor = SystemMonitor(args.url)

    if args.continuous:
        monitor.monitor_continuously(args.interval)
    else:
        checks = monitor.run_health_checks()
        monitor.print_status_report(checks)


if __name__ == '__main__':
    main()
