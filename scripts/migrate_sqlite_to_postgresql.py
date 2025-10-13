#!/usr/bin/env python3
"""Script para migrar datos de SQLite a PostgreSQL."""

import logging
import os
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from urllib.parse import urlparse

import psycopg2

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
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
        if (current_path /
            'requirements.txt').exists() or (current_path /
                                             '.git').exists():
            return current_path
        current_path = current_path.parent

    return Path(__file__).parent.parent


def check_dependencies() -> bool:
    """Verificar que las dependencias necesarias estén instaladas.

    Returns:
        bool: True si todas las dependencias están disponibles
    """
    required_packages = ['psycopg2', 'sqlalchemy']
    missing_packages = []

    for package in required_packages:
        try:
            if package == 'psycopg2':
                __import__(package)
            elif package == 'sqlalchemy':
                __import__(package)
            logger.info(f"✅ {package} está disponible")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"❌ {package} no está instalado")

    if missing_packages:
        logger.error("\n🔧 Para instalar las dependencias faltantes, ejecuta:")
        if 'psycopg2' in missing_packages:
            logger.error("pip install psycopg2-binary")
        if 'sqlalchemy' in missing_packages:
            logger.error("pip install sqlalchemy")
        return False

    return True


def parse_database_url(url: str) -> Dict[str, str]:
    """Parsear URL de base de datos.

    Args:
        url: URL de la base de datos

    Returns:
        Dict con componentes de la URL
    """
    parsed = urlparse(url)

    return {
        'scheme': parsed.scheme,
        'host': parsed.hostname or 'localhost',
        'port': parsed.port or (
            5432 if parsed.scheme == 'postgresql' else None),
        'database': parsed.path.lstrip('/') if parsed.path else '',
        'username': parsed.username or '',
        'password': parsed.password or ''}


def get_sqlite_connection(db_path: str) -> sqlite3.Connection:
    """Obtener conexión a SQLite.

    Args:
        db_path: Ruta a la base de datos SQLite

    Returns:
        Conexión a SQLite
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(
            f"Base de datos SQLite no encontrada: {db_path}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Para acceso por nombre de columna
    return conn


def get_postgresql_connection(
        db_config: Dict[str, str]) -> psycopg2.extensions.connection:
    """Obtener conexión a PostgreSQL.

    Args:
        db_config: Configuración de la base de datos

    Returns:
        Conexión a PostgreSQL
    """
    try:
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database'],
            user=db_config['username'],
            password=db_config['password']
        )
        conn.autocommit = False
        return conn
    except psycopg2.Error as e:
        raise Exception(f"Error conectando a PostgreSQL: {e}")


def get_sqlite_tables(conn: sqlite3.Connection) -> List[str]:
    """Obtener lista de tablas en SQLite.

    Args:
        conn: Conexión a SQLite

    Returns:
        Lista de nombres de tablas
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)

    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return tables


def get_table_schema(conn: sqlite3.Connection,
                     table_name: str) -> List[Tuple[str, str]]:
    """Obtener esquema de una tabla SQLite.

    Args:
        conn: Conexión a SQLite
        table_name: Nombre de la tabla

    Returns:
        Lista de tuplas (nombre_columna, tipo_datos)
    """
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")

    schema = []
    for row in cursor.fetchall():
        col_name = row[1]
        col_type = row[2]
        schema.append((col_name, col_type))

    cursor.close()
    return schema


def sqlite_to_postgresql_type(sqlite_type: str) -> str:
    """Convertir tipo de datos SQLite a PostgreSQL.

    Args:
        sqlite_type: Tipo de datos SQLite

    Returns:
        Tipo de datos PostgreSQL equivalente
    """
    type_mapping = {
        'INTEGER': 'INTEGER',
        'TEXT': 'TEXT',
        'REAL': 'REAL',
        'BLOB': 'BYTEA',
        'NUMERIC': 'NUMERIC',
        'VARCHAR': 'VARCHAR',
        'CHAR': 'CHAR',
        'BOOLEAN': 'BOOLEAN',
        'DATETIME': 'TIMESTAMP',
        'DATE': 'DATE',
        'TIME': 'TIME'
    }

    # Normalizar tipo
    sqlite_type_upper = sqlite_type.upper()

    # Buscar coincidencia exacta
    if sqlite_type_upper in type_mapping:
        return type_mapping[sqlite_type_upper]

    # Buscar coincidencias parciales
    for sqlite_key, postgres_type in type_mapping.items():
        if sqlite_key in sqlite_type_upper:
            return postgres_type

    # Por defecto, usar TEXT
    logger.warning(f"⚠️ Tipo desconocido '{sqlite_type}', usando TEXT")
    return 'TEXT'


def create_postgresql_table(pg_conn: psycopg2.extensions.connection,
                            table_name: str, schema: List[Tuple[str, str]]) -> bool:
    """Crear tabla en PostgreSQL.

    Args:
        pg_conn: Conexión a PostgreSQL
        table_name: Nombre de la tabla
        schema: Esquema de la tabla

    Returns:
        bool: True si la tabla se creó exitosamente
    """
    try:
        cursor = pg_conn.cursor()

        # Construir SQL de creación
        columns = []
        for col_name, col_type in schema:
            pg_type = sqlite_to_postgresql_type(col_type)
            columns.append(f"{col_name} {pg_type}")

        create_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {', '.join(columns)}
            )
        """

        logger.info(f"📝 Creando tabla {table_name}...")
        cursor.execute(create_sql)
        pg_conn.commit()
        cursor.close()

        logger.info(f"✅ Tabla {table_name} creada")
        return True

    except psycopg2.Error as e:
        logger.error(f"❌ Error creando tabla {table_name}: {e}")
        pg_conn.rollback()
        return False


def migrate_table_data(
        sqlite_conn: sqlite3.Connection,
        pg_conn: psycopg2.extensions.connection,
        table_name: str) -> bool:
    """Migrar datos de una tabla de SQLite a PostgreSQL.

    Args:
        sqlite_conn: Conexión a SQLite
        pg_conn: Conexión a PostgreSQL
        table_name: Nombre de la tabla

    Returns:
        bool: True si la migración fue exitosa
    """
    try:
        # Obtener datos de SQLite
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute(f"SELECT * FROM {table_name}")

        rows = sqlite_cursor.fetchall()
        if not rows:
            logger.info(f"📭 Tabla {table_name} está vacía")
            sqlite_cursor.close()
            return True

        # Obtener nombres de columnas
        column_names = [description[0]
                        for description in sqlite_cursor.description]

        # Preparar inserción en PostgreSQL
        pg_cursor = pg_conn.cursor()

        # Construir SQL de inserción
        placeholders = ', '.join(['%s'] * len(column_names))
        insert_sql = f"""
            INSERT INTO {table_name} ({', '.join(column_names)})
            VALUES ({placeholders})
        """

        # Insertar datos en lotes
        batch_size = 1000
        total_rows = len(rows)

        logger.info(f"📊 Migrando {total_rows} filas de {table_name}...")

        for i in range(0, total_rows, batch_size):
            batch = rows[i:i + batch_size]

            # Convertir sqlite3.Row a tuplas
            batch_data = [tuple(row) for row in batch]

            pg_cursor.executemany(insert_sql, batch_data)

            progress = min(i + batch_size, total_rows)
            logger.info(f"  📈 {progress}/{total_rows} filas migradas")

        pg_conn.commit()

        sqlite_cursor.close()
        pg_cursor.close()

        logger.info(f"✅ Tabla {table_name} migrada exitosamente")
        return True

    except Exception as e:
        logger.error(f"❌ Error migrando tabla {table_name}: {e}")
        pg_conn.rollback()
        return False


def verify_migration(
        sqlite_conn: sqlite3.Connection,
        pg_conn: psycopg2.extensions.connection,
        table_name: str) -> bool:
    """Verificar que la migración fue exitosa.

    Args:
        sqlite_conn: Conexión a SQLite
        pg_conn: Conexión a PostgreSQL
        table_name: Nombre de la tabla

    Returns:
        bool: True si la verificación es exitosa
    """
    try:
        # Contar filas en SQLite
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        sqlite_count = sqlite_cursor.fetchone()[0]
        sqlite_cursor.close()

        # Contar filas en PostgreSQL
        pg_cursor = pg_conn.cursor()
        pg_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        pg_count = pg_cursor.fetchone()[0]
        pg_cursor.close()

        if sqlite_count == pg_count:
            logger.info(
                f"✅ Verificación exitosa para {table_name}: {sqlite_count} filas")
            return True
        else:
            logger.error(
                f"❌ Verificación fallida para {table_name}: SQLite={sqlite_count}, PostgreSQL={pg_count}")
            return False

    except Exception as e:
        logger.error(f"❌ Error verificando tabla {table_name}: {e}")
        return False


def create_backup(sqlite_path: str) -> str:
    """Crear backup de la base de datos SQLite.

    Args:
        sqlite_path: Ruta a la base de datos SQLite

    Returns:
        str: Ruta al archivo de backup
    """
    import shutil
    from datetime import datetime

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{sqlite_path}.backup_{timestamp}"

    shutil.copy2(sqlite_path, backup_path)
    logger.info(f"💾 Backup creado: {backup_path}")

    return backup_path


def main():
    """Función principal."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Migrar datos de SQLite a PostgreSQL'
    )
    parser.add_argument(
        '--sqlite-db',
        default='instance/database.db',
        help='Ruta a la base de datos SQLite (default: instance/database.db)'
    )
    parser.add_argument(
        '--postgresql-url',
        help='URL de PostgreSQL (ej: postgresql://user:pass@localhost/dbname)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Solo mostrar qué se haría, sin ejecutar'
    )
    parser.add_argument(
        '--backup',
        action='store_true',
        help='Crear backup de SQLite antes de migrar'
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verificar migración después de completar'
    )

    args = parser.parse_args()

    logger.info("🚀 Migración de SQLite a PostgreSQL")
    logger.info("=" * 40)

    try:
        # Verificar dependencias
        if not check_dependencies():
            sys.exit(1)

        # Obtener configuración
        project_root = get_project_root()
        sqlite_path = str(project_root / args.sqlite_db)

        # URL de PostgreSQL
        postgresql_url = args.postgresql_url or os.getenv('DATABASE_URL')
        if not postgresql_url or 'sqlite' in postgresql_url:
            logger.error("❌ URL de PostgreSQL no configurada")
            logger.error("💡 Usar --postgresql-url o configurar DATABASE_URL")
            sys.exit(1)

        # Parsear configuración de PostgreSQL
        pg_config = parse_database_url(postgresql_url)

        logger.info(f"📂 SQLite: {sqlite_path}")
        logger.info(
            f"🐘 PostgreSQL: {
                pg_config['host']}:{
                pg_config['port']}/{
                pg_config['database']}")

        if args.dry_run:
            logger.info("🔍 Modo dry-run activado")

        # Crear backup si se solicita
        if args.backup and not args.dry_run:
            create_backup(sqlite_path)

        # Conectar a bases de datos
        logger.info("🔌 Conectando a bases de datos...")

        sqlite_conn = get_sqlite_connection(sqlite_path)
        logger.info("✅ Conectado a SQLite")

        if not args.dry_run:
            pg_conn = get_postgresql_connection(pg_config)
            logger.info("✅ Conectado a PostgreSQL")

        # Obtener tablas
        tables = get_sqlite_tables(sqlite_conn)
        logger.info(f"📋 Tablas encontradas: {len(tables)}")

        for table in tables:
            logger.info(f"  📄 {table}")

        if args.dry_run:
            logger.info("\n✅ Dry-run completado")
            sqlite_conn.close()
            return

        # Migrar cada tabla
        migrated_tables = []
        failed_tables = []

        for table_name in tables:
            logger.info(f"\n🔄 Procesando tabla: {table_name}")

            # Obtener esquema
            schema = get_table_schema(sqlite_conn, table_name)
            logger.info(f"  📊 Columnas: {len(schema)}")

            # Crear tabla en PostgreSQL
            if create_postgresql_table(pg_conn, table_name, schema):
                # Migrar datos
                if migrate_table_data(sqlite_conn, pg_conn, table_name):
                    migrated_tables.append(table_name)
                else:
                    failed_tables.append(table_name)
            else:
                failed_tables.append(table_name)

        # Verificar migración si se solicita
        if args.verify and migrated_tables:
            logger.info("\n🔍 Verificando migración...")
            verification_failed = []

            for table_name in migrated_tables:
                if not verify_migration(sqlite_conn, pg_conn, table_name):
                    verification_failed.append(table_name)

            if verification_failed:
                logger.error(
                    f"❌ Verificación fallida para: {verification_failed}")
            else:
                logger.info("✅ Verificación exitosa para todas las tablas")

        # Cerrar conexiones
        sqlite_conn.close()
        pg_conn.close()

        # Resumen final
        logger.info("\n" + "=" * 40)
        logger.info("📊 RESUMEN DE MIGRACIÓN:")
        logger.info(f"✅ Tablas migradas: {len(migrated_tables)}")
        if migrated_tables:
            for table in migrated_tables:
                logger.info(f"  📄 {table}")

        if failed_tables:
            logger.error(f"❌ Tablas fallidas: {len(failed_tables)}")
            for table in failed_tables:
                logger.error(f"  📄 {table}")

        if failed_tables:
            logger.error("\n❌ Migración completada con errores")
            sys.exit(1)
        else:
            logger.info("\n🎉 Migración completada exitosamente")
            logger.info("\n📋 Próximos pasos:")
            logger.info("1. Actualizar DATABASE_URL en .env")
            logger.info("2. Reiniciar la aplicación")
            logger.info("3. Verificar funcionamiento")

    except Exception as e:
        logger.error(f"\n❌ Error durante la migración: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
