"""Tests unitarios para PostgreSQL."""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from config.database import (
    get_database_url,
    init_db,
    reset_db,
    check_db_connection,
    migrate_to_postgresql
)


class TestDatabaseConfiguration:
    """Tests para la configuración de base de datos."""

    def test_get_database_url_sqlite_default(self):
        """Test URL de SQLite por defecto."""
        with patch.dict(os.environ, {}, clear=True):
            url = get_database_url()
            assert url.startswith('sqlite:///')
            assert 'gemini_chatbot.db' in url

    def test_get_database_url_from_env(self):
        """Test URL desde variable de entorno."""
        test_url = "postgresql://user:pass@localhost:5432/testdb"
        with patch.dict(os.environ, {'DATABASE_URL': test_url}):
            url = get_database_url()
            assert url == test_url

    def test_get_database_url_postgresql_components(self):
        """Test URL de PostgreSQL desde componentes."""
        env_vars = {
            'POSTGRES_HOST': 'localhost',
            'POSTGRES_PORT': '5432',
            'POSTGRES_DB': 'testdb',
            'POSTGRES_USER': 'testuser',
            'POSTGRES_PASSWORD': 'testpass',
            'POSTGRES_ENABLED': 'true'
        }

        with patch.dict(os.environ, env_vars):
            url = get_database_url()
            expected = "postgresql://testuser:testpass@localhost:5432/testdb"
            assert url == expected

    def test_get_database_url_postgresql_disabled(self):
        """Test fallback a SQLite cuando PostgreSQL está deshabilitado."""
        env_vars = {
            'POSTGRES_HOST': 'localhost',
            'POSTGRES_PORT': '5432',
            'POSTGRES_DB': 'testdb',
            'POSTGRES_USER': 'testuser',
            'POSTGRES_PASSWORD': 'testpass',
            'POSTGRES_ENABLED': 'false'
        }

        with patch.dict(os.environ, env_vars):
            url = get_database_url()
            assert url.startswith('sqlite:///')


class TestDatabaseConnection:
    """Tests para conexión de base de datos."""

    @patch('config.database.create_engine')
    def test_check_db_connection_success(self, mock_create_engine):
        """Test conexión exitosa a la base de datos."""
        # Mock engine y connection
        mock_engine = Mock()
        mock_connection = Mock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        result = check_db_connection(
            "postgresql://user:pass@localhost:5432/db")

        assert result is True
        mock_create_engine.assert_called_once()
        mock_engine.connect.assert_called_once()

    @patch('config.database.create_engine')
    def test_check_db_connection_failure(self, mock_create_engine):
        """Test fallo de conexión a la base de datos."""
        mock_create_engine.side_effect = OperationalError(
            "Connection failed", None, None)

        result = check_db_connection(
            "postgresql://user:pass@localhost:5432/db")

        assert result is False

    @patch('config.database.create_engine')
    def test_check_db_connection_sqlalchemy_error(self, mock_create_engine):
        """Test error de SQLAlchemy en conexión."""
        mock_create_engine.side_effect = SQLAlchemyError("SQLAlchemy error")

        result = check_db_connection(
            "postgresql://user:pass@localhost:5432/db")

        assert result is False


class TestDatabaseInitialization:
    """Tests para inicialización de base de datos."""

    @patch('config.database.get_database_url')
    @patch('config.database.create_engine')
    @patch('config.database.Base.metadata.create_all')
    def test_init_db_success(
            self,
            mock_create_all,
            mock_create_engine,
            mock_get_url):
        """Test inicialización exitosa de la base de datos."""
        mock_get_url.return_value = "sqlite:///test.db"
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine

        result = init_db()

        assert result is True
        mock_create_all.assert_called_once_with(mock_engine)

    @patch('config.database.get_database_url')
    @patch('config.database.create_engine')
    def test_init_db_failure(self, mock_create_engine, mock_get_url):
        """Test fallo en inicialización de la base de datos."""
        mock_get_url.return_value = "sqlite:///test.db"
        mock_create_engine.side_effect = Exception("Database error")

        result = init_db()

        assert result is False

    @patch('config.database.get_database_url')
    @patch('config.database.create_engine')
    @patch('config.database.Base.metadata.drop_all')
    @patch('config.database.Base.metadata.create_all')
    def test_reset_db_success(
            self,
            mock_create_all,
            mock_drop_all,
            mock_create_engine,
            mock_get_url):
        """Test reset exitoso de la base de datos."""
        mock_get_url.return_value = "sqlite:///test.db"
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine

        result = reset_db()

        assert result is True
        mock_drop_all.assert_called_once_with(mock_engine)
        mock_create_all.assert_called_once_with(mock_engine)


class TestPostgreSQLMigration:
    """Tests para migración a PostgreSQL."""

    @patch('config.database.check_db_connection')
    def test_migrate_to_postgresql_success(self, mock_check_connection):
        """Test migración exitosa a PostgreSQL."""
        mock_check_connection.return_value = True

        result = migrate_to_postgresql(
            "postgresql://user:pass@localhost:5432/db",
            "sqlite:///old.db"
        )

        # Por ahora solo verifica la conexión
        assert result is True
        mock_check_connection.assert_called_once()

    @patch('config.database.check_db_connection')
    def test_migrate_to_postgresql_connection_failure(
            self, mock_check_connection):
        """Test fallo de conexión en migración a PostgreSQL."""
        mock_check_connection.return_value = False

        result = migrate_to_postgresql(
            "postgresql://user:pass@localhost:5432/db",
            "sqlite:///old.db"
        )

        assert result is False


@pytest.mark.integration
class TestPostgreSQLIntegration:
    """Tests de integración para PostgreSQL."""

    @pytest.fixture
    def postgresql_url(self):
        """Fixture para URL de PostgreSQL de prueba."""
        host = os.getenv('POSTGRES_TEST_HOST', 'localhost')
        port = os.getenv('POSTGRES_TEST_PORT', '5432')
        db = os.getenv('POSTGRES_TEST_DB', 'test_gemini_chatbot')
        user = os.getenv('POSTGRES_TEST_USER', 'test_user')
        password = os.getenv('POSTGRES_TEST_PASSWORD', 'test_password')

        return f"postgresql://{user}:{password}@{host}:{port}/{db}"

    @pytest.mark.skipif(
        not os.getenv('POSTGRES_TEST_HOST'),
        reason="PostgreSQL de prueba no configurado"
    )
    def test_real_postgresql_connection(self, postgresql_url):
        """Test conexión real a PostgreSQL (requiere configuración)."""
        result = check_db_connection(postgresql_url)
        assert result is True

    @pytest.mark.skipif(
        not os.getenv('POSTGRES_TEST_HOST'),
        reason="PostgreSQL de prueba no configurado"
    )
    def test_real_postgresql_operations(self, postgresql_url):
        """Test operaciones reales en PostgreSQL."""
        try:
            engine = create_engine(postgresql_url)

            # Test conexión
            with engine.connect() as conn:
                # Test query simple
                result = conn.execute(text("SELECT 1 as test"))
                row = result.fetchone()
                assert row[0] == 1

                # Test creación de tabla temporal
                conn.execute(text("""
                    CREATE TEMPORARY TABLE test_table (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))

                # Test inserción
                conn.execute(text("""
                    INSERT INTO test_table (name) VALUES ('test_record')
                """))

                # Test consulta
                result = conn.execute(text("""
                    SELECT name FROM test_table WHERE name = 'test_record'
                """))
                row = result.fetchone()
                assert row[0] == 'test_record'

                conn.commit()

        except Exception as e:
            pytest.fail(f"Error en operaciones PostgreSQL: {e}")

    def test_sqlite_fallback_operations(self):
        """Test operaciones con SQLite como fallback."""
        sqlite_url = "sqlite:///:memory:"

        try:
            engine = create_engine(sqlite_url)

            with engine.connect() as conn:
                # Test query simple
                result = conn.execute(text("SELECT 1 as test"))
                row = result.fetchone()
                assert row[0] == 1

                # Test creación de tabla
                conn.execute(text("""
                    CREATE TABLE test_table (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """))

                # Test inserción
                conn.execute(text("""
                    INSERT INTO test_table (name) VALUES ('test_record')
                """))

                # Test consulta
                result = conn.execute(text("""
                    SELECT name FROM test_table WHERE name = 'test_record'
                """))
                row = result.fetchone()
                assert row[0] == 'test_record'

                conn.commit()

        except Exception as e:
            pytest.fail(f"Error en operaciones SQLite: {e}")


@pytest.mark.database
class TestDatabasePerformance:
    """Tests de rendimiento para base de datos."""

    def test_connection_pool_performance(self):
        """Test rendimiento del pool de conexiones."""
        sqlite_url = "sqlite:///:memory:"
        engine = create_engine(sqlite_url, pool_size=5, max_overflow=10)

        import time
        start_time = time.time()

        # Simular múltiples conexiones
        connections = []
        for _ in range(10):
            conn = engine.connect()
            connections.append(conn)

        # Cerrar conexiones
        for conn in connections:
            conn.close()

        end_time = time.time()
        duration = end_time - start_time

        # Debe completarse en menos de 1 segundo
        assert duration < 1.0

    @pytest.mark.slow
    def test_bulk_insert_performance(self):
        """Test rendimiento de inserción masiva."""
        sqlite_url = "sqlite:///:memory:"
        engine = create_engine(sqlite_url)

        with engine.connect() as conn:
            # Crear tabla de prueba
            conn.execute(text("""
                CREATE TABLE performance_test (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT,
                    number INTEGER
                )
            """))

            import time
            start_time = time.time()

            # Insertar 1000 registros
            for i in range(1000):
                conn.execute(text("""
                    INSERT INTO performance_test (data, number)
                    VALUES (:data, :number)
                """), {"data": f"test_data_{i}", "number": i})

            conn.commit()
            end_time = time.time()
            duration = end_time - start_time

            # Verificar que se insertaron todos los registros
            result = conn.execute(
                text("SELECT COUNT(*) FROM performance_test"))
            count = result.fetchone()[0]
            assert count == 1000

            # Debe completarse en menos de 5 segundos
            assert duration < 5.0
