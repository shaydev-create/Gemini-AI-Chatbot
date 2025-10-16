#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 SCRIPT DE MANTENIMIENTO - GEMINI AI CHATBOT

Script automatizado para tareas de mantenimiento del sistema:
- Limpieza de logs antiguos
- Limpieza de archivos temporales
- Limpieza de tokens expirados
- Optimización de base de datos
- Generación de reportes de uso
"""

import logging
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app import create_app
from app.models import ChatSession, TokenBlacklist, User, db

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/maintenance.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class MaintenanceManager:
    """Gestor de tareas de mantenimiento."""

    def __init__(self):
        self.app = create_app()
        self.stats = {
            "logs_cleaned": 0,
            "temp_files_cleaned": 0,
            "tokens_cleaned": 0,
            "sessions_archived": 0,
            "space_freed": 0,
        }

    def run_all_tasks(self):
        """Ejecutar todas las tareas de mantenimiento."""
        logger.info("🔧 Iniciando mantenimiento del sistema...")

        with self.app.app_context():
            self.clean_old_logs()
            self.clean_temp_files()
            self.clean_expired_tokens()
            self.archive_old_sessions()
            self.optimize_database()
            self.generate_usage_report()

        self.print_summary()
        logger.info("✅ Mantenimiento completado")

    def clean_old_logs(self):
        """Limpiar logs antiguos (más de 30 días)."""
        logger.info("🧹 Limpiando logs antiguos...")

        logs_dir = Path("logs")
        if not logs_dir.exists():
            return

        cutoff_date = datetime.now() - timedelta(days=30)

        for log_file in logs_dir.glob("*.log*"):
            if log_file.stat().st_mtime < cutoff_date.timestamp():
                size = log_file.stat().st_size
                log_file.unlink()
                self.stats["logs_cleaned"] += 1
                self.stats["space_freed"] += size
                logger.info(f"  📄 Eliminado: {log_file.name}")

    def clean_temp_files(self):
        """Limpiar archivos temporales."""
        logger.info("🧹 Limpiando archivos temporales...")

        temp_dirs = ["uploads/temp", "uploads/processing"]

        for temp_dir in temp_dirs:
            temp_path = Path(temp_dir)
            if not temp_path.exists():
                continue

            for temp_file in temp_path.iterdir():
                if temp_file.is_file():
                    # Eliminar archivos de más de 1 hora
                    if datetime.now().timestamp() - temp_file.stat().st_mtime > 3600:
                        size = temp_file.stat().st_size
                        temp_file.unlink()
                        self.stats["temp_files_cleaned"] += 1
                        self.stats["space_freed"] += size
                        logger.info(f"  🗑️ Eliminado: {temp_file.name}")

    def clean_expired_tokens(self):
        """Limpiar tokens expirados de la lista negra."""
        logger.info("🧹 Limpiando tokens expirados...")

        # Eliminar tokens de más de 7 días
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)

        expired_tokens = TokenBlacklist.query.filter(TokenBlacklist.revoked_at < cutoff_date).all()

        for token in expired_tokens:
            db.session.delete(token)
            self.stats["tokens_cleaned"] += 1

        db.session.commit()
        logger.info(f"  🔑 Tokens eliminados: {len(expired_tokens)}")

    def archive_old_sessions(self):
        """Archivar sesiones de chat antiguas."""
        logger.info("📦 Archivando sesiones antiguas...")

        # Archivar sesiones de más de 90 días
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=90)

        old_sessions = ChatSession.query.filter(ChatSession.created_at < cutoff_date, ChatSession.status != "archived").all()

        for session in old_sessions:
            session.status = "archived"
            self.stats["sessions_archived"] += 1

        db.session.commit()
        logger.info(f"  📚 Sesiones archivadas: {len(old_sessions)}")

    def optimize_database(self):
        """Optimizar base de datos."""
        logger.info("⚡ Optimizando base de datos...")

        try:
            # Ejecutar VACUUM para SQLite
            db.engine.execute("VACUUM")
            logger.info("  ✅ Base de datos optimizada")
        except Exception as e:
            logger.error(f"  ❌ Error optimizando BD: {e}")

    def generate_usage_report(self):
        """Generar reporte de uso del sistema."""
        logger.info("📊 Generando reporte de uso...")

        # Estadísticas de usuarios
        total_users = User.query.count()
        active_users = User.query.filter_by(status="active").count()
        verified_users = User.query.filter_by(email_verified=True).count()

        # Estadísticas de sesiones
        total_sessions = ChatSession.query.count()
        active_sessions = ChatSession.query.filter_by(status="active").count()

        # Generar reporte
        report = f"""
📊 REPORTE DE USO - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
{"=" * 60}

👥 USUARIOS:
   Total: {total_users}
   Activos: {active_users}
   Verificados: {verified_users}

💬 SESIONES:
   Total: {total_sessions}
   Activas: {active_sessions}

🧹 MANTENIMIENTO:
   Logs limpiados: {self.stats["logs_cleaned"]}
   Archivos temp limpiados: {self.stats["temp_files_cleaned"]}
   Tokens limpiados: {self.stats["tokens_cleaned"]}
   Sesiones archivadas: {self.stats["sessions_archived"]}
   Espacio liberado: {self.stats["space_freed"] / 1024 / 1024:.2f} MB

{"=" * 60}
        """

        # Guardar reporte
        reports_dir = Path("logs/reports")
        reports_dir.mkdir(exist_ok=True)

        report_file = reports_dir / f"usage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_file.write_text(report)

        logger.info(f"  📄 Reporte guardado: {report_file}")

    def print_summary(self):
        """Imprimir resumen del mantenimiento."""
        print("\n" + "=" * 60)
        print("🔧 RESUMEN DE MANTENIMIENTO")
        print("=" * 60)
        print(f"📄 Logs limpiados: {self.stats['logs_cleaned']}")
        print(f"🗑️ Archivos temp limpiados: {self.stats['temp_files_cleaned']}")
        print(f"🔑 Tokens limpiados: {self.stats['tokens_cleaned']}")
        print(f"📚 Sesiones archivadas: {self.stats['sessions_archived']}")
        print(f"💾 Espacio liberado: {self.stats['space_freed'] / 1024 / 1024:.2f} MB")
        print("=" * 60)


def main():
    """Función principal."""
    try:
        maintenance = MaintenanceManager()
        maintenance.run_all_tasks()
    except Exception as e:
        logger.error(f"❌ Error en mantenimiento: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
