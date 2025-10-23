#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎛️ GEMINI AI CHATBOT - MANAGER
=============================

Centro de control para gestionar el proyecto Gemini AI Chatbot.
Maneja Docker, persistencia de datos, logs y mantenimiento.

USO:
    python manage.py start      # ✅ Inicia todos los servicios
    python manage.py stop       # ⏹️ Para todos los servicios
    python manage.py restart    # 🔄 Reinicia manteniendo datos
    python manage.py status     # 📊 Estado de servicios
    python manage.py logs       # 📋 Ver logs en tiempo real
    python manage.py clean      # 🧹 Limpieza segura
    python manage.py backup     # 💾 Crear backup de datos
    python manage.py health     # 🏥 Verificar salud del sistema
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class Colors:
    """Colores para output en terminal."""

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    END = "\033[0m"


class GeminiManager:
    """Gestor principal del proyecto Gemini AI Chatbot."""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.compose_files = ["docker-compose.yml", "docker-compose.dev.yml"]
        self.services = ["gemini-app", "gemini-db", "gemini-cache"]

    def _print(self, message: str, color: str = Colors.WHITE, emoji: str = ""):
        """Imprime mensaje con formato."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{color}{emoji} [{timestamp}] {message}{Colors.END}")

    def _success(self, message: str):
        """Mensaje de éxito."""
        self._print(message, Colors.GREEN, "✅")

    def _error(self, message: str):
        """Mensaje de error."""
        self._print(message, Colors.RED, "❌")

    def _info(self, message: str):
        """Mensaje informativo."""
        self._print(message, Colors.BLUE, "ℹ️")

    def _warning(self, message: str):
        """Mensaje de advertencia."""
        self._print(message, Colors.YELLOW, "⚠️")

    def _run_docker_compose(self, command: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Ejecuta comando docker-compose."""
        base_cmd = ["docker-compose"]
        for compose_file in self.compose_files:
            base_cmd.extend(["-f", compose_file])

        full_cmd = base_cmd + command

        try:
            result = subprocess.run(full_cmd, cwd=self.project_root, capture_output=True, text=True, check=check)
            return result
        except subprocess.CalledProcessError as e:
            self._error(f"Error ejecutando comando: {' '.join(full_cmd)}")
            self._error(f"Salida: {e.stdout}")
            self._error(f"Error: {e.stderr}")
            raise

    def _check_docker_available(self) -> bool:
        """Verifica si Docker está disponible."""
        try:
            subprocess.run(["docker", "--version"], capture_output=True, check=True)
            subprocess.run(["docker-compose", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _get_container_status(self) -> Dict[str, Dict]:
        """Obtiene el estado de todos los contenedores."""
        try:
            result = subprocess.run(["docker", "ps", "-a", "--format", "json"], capture_output=True, text=True, check=True)

            containers = {}
            for line in result.stdout.strip().split("\n"):
                if line:
                    container = json.loads(line)
                    name = container.get("Names", "").replace("/", "")
                    if name in self.services:
                        containers[name] = {
                            "status": container.get("State", "unknown"),
                            "ports": container.get("Ports", ""),
                            "created": container.get("CreatedAt", ""),
                            "image": container.get("Image", ""),
                        }
            return containers
        except Exception as e:
            self._error(f"Error obteniendo estado de contenedores: {e}")
            return {}

    def start(self):
        """🚀 Inicia todos los servicios."""
        self._info("Iniciando Gemini AI Chatbot...")

        # Verificar Docker
        if not self._check_docker_available():
            self._error("Docker no está disponible. Instala Docker Desktop.")
            return False

        # Verificar archivos .env
        env_file = self.project_root / ".env"
        if not env_file.exists():
            self._warning("Archivo .env no encontrado. Creando desde .env.example...")
            example_file = self.project_root / ".env.example"
            if example_file.exists():
                import shutil

                shutil.copy(example_file, env_file)
                self._warning("⚠️ Recuerda configurar tu GEMINI_API_KEY en .env")

        try:
            # Iniciar servicios
            self._info("Construyendo e iniciando contenedores...")
            self._run_docker_compose(["up", "--build", "-d"])

            # Esperar a que los servicios estén listos
            self._info("Esperando a que los servicios estén listos...")
            time.sleep(10)

            # Verificar estado
            status = self._get_container_status()
            all_running = True

            for service in self.services:
                if service in status:
                    if "running" in status[service]["status"].lower():
                        self._success(f"{service}: Ejecutándose")
                    else:
                        self._error(f"{service}: {status[service]['status']}")
                        all_running = False
                else:
                    self._error(f"{service}: No encontrado")
                    all_running = False

            if all_running:
                self._success("🎉 Todos los servicios iniciados correctamente!")
                self._info("📱 Aplicación disponible en: http://localhost:5000")
                self._info("🗄️ Base de datos: localhost:5432")
                self._info("🔄 Cache Redis: localhost:6379")
            else:
                self._warning("Algunos servicios tienen problemas. Usa 'python manage.py logs' para más detalles.")

            return all_running

        except Exception as e:
            self._error(f"Error iniciando servicios: {e}")
            return False

    def stop(self):
        """⏹️ Para todos los servicios correctamente."""
        self._info("Parando Gemini AI Chatbot...")

        try:
            self._run_docker_compose(["down"])
            self._success("Servicios detenidos correctamente")
            return True
        except Exception as e:
            self._error(f"Error parando servicios: {e}")
            return False

    def restart(self):
        """🔄 Reinicia servicios manteniendo datos."""
        self._info("Reiniciando Gemini AI Chatbot...")

        try:
            self._run_docker_compose(["restart"])
            time.sleep(5)
            self._success("Servicios reiniciados correctamente")
            return True
        except Exception as e:
            self._error(f"Error reiniciando servicios: {e}")
            return False

    def status(self):
        """📊 Muestra el estado detallado de todos los servicios."""
        self._info("Estado de Gemini AI Chatbot")
        print("=" * 60)

        # Verificar Docker
        if not self._check_docker_available():
            self._error("Docker no está disponible")
            return

        # Estado de contenedores
        containers = self._get_container_status()

        if not containers:
            self._warning("No hay contenedores ejecutándose")
            return

        for service in self.services:
            if service in containers:
                info = containers[service]
                status_color = Colors.GREEN if "running" in info["status"].lower() else Colors.RED
                print(f"{Colors.BOLD}{service}:{Colors.END}")
                print(f"  Estado: {status_color}{info['status']}{Colors.END}")
                print(f"  Imagen: {info['image']}")
                print(f"  Puertos: {info['ports']}")
                print(f"  Creado: {info['created']}")
                print()
            else:
                print(f"{Colors.BOLD}{service}:{Colors.END}")
                print(f"  Estado: {Colors.RED}No encontrado{Colors.END}")
                print()

        # URLs útiles
        print(f"{Colors.BOLD}URLs útiles:{Colors.END}")
        print("  🌐 Aplicación: http://localhost:5000")
        print("  🗄️ PostgreSQL: localhost:5432")
        print("  🔄 Redis: localhost:6379")

    def logs(self, service: Optional[str] = None, follow: bool = True):
        """📋 Muestra logs de los servicios."""
        if service and service not in self.services:
            self._error(f"Servicio '{service}' no válido. Opciones: {', '.join(self.services)}")
            return

        try:
            cmd = ["logs"]
            if follow:
                cmd.append("-f")
            if service:
                cmd.append(service.replace("gemini-", ""))  # docker-compose usa nombres cortos
            else:
                self._info("Mostrando logs de todos los servicios (Ctrl+C para salir)")

            # Ejecutar sin capturar output para mostrar en tiempo real
            full_cmd = ["docker-compose"]
            for compose_file in self.compose_files:
                full_cmd.extend(["-f", compose_file])
            full_cmd.extend(cmd)

            subprocess.run(full_cmd, cwd=self.project_root)

        except KeyboardInterrupt:
            self._info("Logs interrumpidos por usuario")
        except Exception as e:
            self._error(f"Error mostrando logs: {e}")

    def clean(self, level: str = "soft"):
        """🧹 Limpieza del sistema."""
        if level not in ["soft", "hard", "nuclear"]:
            self._error("Nivel de limpieza no válido. Opciones: soft, hard, nuclear")
            return

        self._info(f"Iniciando limpieza nivel '{level}'...")

        if level == "soft":
            # Limpieza suave - solo cache de build
            try:
                subprocess.run(["docker", "builder", "prune", "-f"], check=True)
                self._success("Cache de build limpiado")
            except Exception as e:
                self._error(f"Error en limpieza suave: {e}")

        elif level == "hard":
            # Limpieza fuerte - imágenes no usadas
            try:
                subprocess.run(["docker", "image", "prune", "-f"], check=True)
                subprocess.run(["docker", "builder", "prune", "-f"], check=True)
                self._success("Imágenes no usadas y cache limpiados")
            except Exception as e:
                self._error(f"Error en limpieza fuerte: {e}")

        elif level == "nuclear":
            # Limpieza nuclear - TODO excepto volúmenes importantes
            response = input("⚠️ Esto eliminará TODAS las imágenes y contenedores. ¿Continuar? (y/N): ")
            if response.lower() == "y":
                try:
                    self.stop()
                    subprocess.run(["docker", "system", "prune", "-a", "-f"], check=True)
                    self._success("Limpieza nuclear completada")
                    self._warning("Será necesario reconstruir las imágenes en el próximo start")
                except Exception as e:
                    self._error(f"Error en limpieza nuclear: {e}")
            else:
                self._info("Limpieza nuclear cancelada")

    def backup(self):
        """💾 Crear backup de datos importantes."""
        backup_dir = self.project_root / "backups"
        backup_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"gemini_backup_{timestamp}"

        try:
            # Backup de volúmenes Docker
            self._info("Creando backup de datos...")

            # Crear directorio de backup específico
            current_backup = backup_dir / backup_name
            current_backup.mkdir(exist_ok=True)

            # Backup de PostgreSQL
            pg_backup = current_backup / "postgres_data.sql"
            subprocess.run(
                ["docker", "exec", "gemini-db", "pg_dump", "-U", "gemini_user", "gemini_chatbot"],
                stdout=open(pg_backup, "w"),
                check=True,
            )

            # Backup de configuración
            config_files = [".env", "docker-compose.yml", "docker-compose.dev.yml"]
            for config_file in config_files:
                source = self.project_root / config_file
                if source.exists():
                    import shutil

                    shutil.copy(source, current_backup / config_file)

            self._success(f"Backup creado: {backup_name}")
            return backup_name

        except Exception as e:
            self._error(f"Error creando backup: {e}")
            return None

    def health(self):
        """🏥 Verificación completa de salud del sistema."""
        self._info("Verificando salud del sistema...")
        print("=" * 50)

        checks = []

        # Verificar Docker
        docker_ok = self._check_docker_available()
        checks.append(("Docker disponible", docker_ok))

        # Verificar archivos de configuración
        env_exists = (self.project_root / ".env").exists()
        checks.append(("Archivo .env existe", env_exists))

        compose_exists = all((self.project_root / f).exists() for f in self.compose_files)
        checks.append(("Archivos docker-compose existen", compose_exists))

        # Verificar contenedores
        if docker_ok:
            containers = self._get_container_status()
            containers_running = len([c for c in containers.values() if "running" in c["status"].lower()])
            checks.append(("Contenedores ejecutándose", containers_running == len(self.services)))

        # Verificar conectividad
        if docker_ok and containers_running > 0:
            try:
                import requests

                response = requests.get("http://localhost:5000", timeout=5)
                app_responding = response.status_code == 200
            except Exception:
                app_responding = False
            checks.append(("Aplicación responde", app_responding))

        # Mostrar resultados
        all_good = True
        for check_name, status in checks:
            status_icon = "✅" if status else "❌"
            status_text = "OK" if status else "FALLO"
            color = Colors.GREEN if status else Colors.RED
            print(f"  {status_icon} {check_name}: {color}{status_text}{Colors.END}")
            if not status:
                all_good = False

        print()
        if all_good:
            self._success("🎉 Sistema completamente saludable!")
        else:
            self._warning("⚠️ Algunos problemas detectados. Revisa los fallos anteriores.")

        return all_good


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description="Gestor del proyecto Gemini AI Chatbot")

    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Comandos básicos
    subparsers.add_parser("start", help="Iniciar todos los servicios")
    subparsers.add_parser("stop", help="Parar todos los servicios")
    subparsers.add_parser("restart", help="Reiniciar servicios")
    subparsers.add_parser("status", help="Mostrar estado de servicios")
    subparsers.add_parser("health", help="Verificar salud del sistema")
    subparsers.add_parser("backup", help="Crear backup de datos")

    # Comando logs con opciones
    logs_parser = subparsers.add_parser("logs", help="Mostrar logs")
    logs_parser.add_argument("--service", choices=["gemini-app", "gemini-db", "gemini-cache"], help="Servicio específico")
    logs_parser.add_argument("--no-follow", action="store_true", help="No seguir logs en tiempo real")

    # Comando clean con opciones
    clean_parser = subparsers.add_parser("clean", help="Limpiar sistema")
    clean_parser.add_argument("--level", choices=["soft", "hard", "nuclear"], default="soft", help="Nivel de limpieza")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    manager = GeminiManager()

    try:
        if args.command == "start":
            manager.start()
        elif args.command == "stop":
            manager.stop()
        elif args.command == "restart":
            manager.restart()
        elif args.command == "status":
            manager.status()
        elif args.command == "health":
            manager.health()
        elif args.command == "backup":
            manager.backup()
        elif args.command == "logs":
            manager.logs(service=getattr(args, "service", None), follow=not getattr(args, "no_follow", False))
        elif args.command == "clean":
            manager.clean(level=args.level)

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️ Operación cancelada por usuario{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {e}{Colors.END}")
        sys.exit(1)


if __name__ == "__main__":
    main()
