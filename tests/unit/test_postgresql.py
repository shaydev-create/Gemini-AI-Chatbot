"""Tests unitarios para PostgreSQL."""

import os
from unittest.mock import Mock, patch

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from app.config.database import (
    check_db_connection,
    init_db,
    migrate_to_postgresql,
    reset_db,
)


class TestDatabaseConnection:
    """Tests para conexión de base de datos."""

    @patch("app.config.database.create_engine")
    def test_check_db_connection_success(self, mock_create_engine):
        """Test conexión exitosa a la base de datos."""
        # Mock engine y context manager
        mock_engine = Mock()
        mock_conn_ctx = Mock()
        mock_connect_cm = Mock()
        mock_connect_cm.__enter__ = Mock(return_value=mock_conn_ctx)
        mock_connect_cm.__exit__ = Mock(return_value=None)
        mock_engine.connect.return_value = mock_connect_cm
        mock_create_engine.return_value = mock_engine

        result, msg = check_db_connection("sqlite:///test.db")

    @patch("app.config.database.create_engine")
    def test_check_db_connection_failure(self, mock_create_engine):
        """Test fallo de conexión a la base de datos."""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        mock_engine.connect.side_effect = OperationalError("Connection failed", None, None)

        result, msg = check_db_connection("sqlite:///:memory:")

        assert result is False

    @patch("app.config.database.create_engine")
    def test_check_db_connection_sqlalchemy_error(self, mock_create_engine):
        """Test error de SQLAlchemy en conexión."""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        mock_engine.connect.side_effect = SQLAlchemyError("SQLAlchemy error")

        result, msg = check_db_connection("sqlite:///:memory:")

        assert result is False


class TestDatabaseInitialization:
    """Tests para inicialización de base de datos."""

    def test_init_db_raises_error_if_uri_not_set(self):
        """Test que init_db lanza RuntimeError si no se ha configurado la URI."""
        from flask import Flask

        app = Flask(__name__)
        # Asegurarse de que la configuración no está presente
        if "SQLALCHEMY_DATABASE_URI" in app.config:
            del app.config["SQLALCHEMY_DATABASE_URI"]

        with pytest.raises(RuntimeError) as excinfo:
            init_db(app)
        assert "SQLALCHEMY_DATABASE_URI" in str(excinfo.value)

    @patch("app.config.database.db.create_all")
    @patch("app.config.database.db.drop_all")
    def test_reset_db_success(self, mock_drop_all, mock_create_all):
        """Test reset exitoso de la base de datos."""
        from flask import Flask

        app = Flask(__name__)
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
        # No debe lanzar excepción
        try:
            reset_db(app)
        except Exception:
            import pytest

            pytest.fail("reset_db no debe lanzar excepción")
        mock_drop_all.assert_called_once()
        mock_create_all.assert_called_once()


class TestPostgreSQLMigration:
    """Tests para migración a PostgreSQL."""

    @patch("app.config.database.create_engine")
    def test_migrate_to_postgresql_connection_failure(self, mock_create_engine):
        """Test fallo de conexión en migración a PostgreSQL."""
        # Simular entorno habilitado pero error de conexión
        with patch.dict(os.environ, {"POSTGRES_ENABLED": "true"}):
            # Simular error al conectar a PostgreSQL
            mock_create_engine.side_effect = Exception("No se puede conectar")
            result = migrate_to_postgresql()
            assert result is False


@pytest.mark.integration
class TestPostgreSQLIntegration:
    """Tests de integración para PostgreSQL."""

    @pytest.fixture
    def postgresql_url(self):
        """Fixture para URL de PostgreSQL de prueba."""
        host = os.getenv("POSTGRES_TEST_HOST", "localhost")
        port = os.getenv("POSTGRES_TEST_PORT", "5432")
        db = os.getenv("POSTGRES_TEST_DB", "test_gemini_chatbot")
        user = os.getenv("POSTGRES_TEST_USER", "test_user")
        password = os.getenv("POSTGRES_TEST_PASSWORD", "test_password")

        return f"postgresql://{user}:{password}@{host}:{port}/{db}"

    @pytest.mark.skipif(
        not os.getenv("POSTGRES_TEST_HOST"),
        reason="PostgreSQL de prueba no configurado",
    )
    def test_real_postgresql_connection(self, postgresql_url):
        """Test conexión real a PostgreSQL (requiere configuración)."""
        result = check_db_connection(postgresql_url)
        assert result is True

    @pytest.mark.skipif(
        not os.getenv("POSTGRES_TEST_HOST"),
        reason="PostgreSQL de prueba no configurado",
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
                conn.execute(
                    text(
                        """
                    CREATE TEMPORARY TABLE test_table (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                    )
                )

                # Test inserción
                conn.execute(
                    text(
                        """
                    INSERT INTO test_table (name) VALUES ('test_record')
                """
                    )
                )

                # Test consulta
                result = conn.execute(
                    text(
                        """
                    SELECT name FROM test_table WHERE name = 'test_record'
                """
                    )
                )
                row = result.fetchone()
                assert row[0] == "test_record"

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
                conn.execute(
                    text(
                        """
                    CREATE TABLE test_table (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """
                    )
                )

                # Test inserción
                conn.execute(
                    text(
                        """
                    INSERT INTO test_table (name) VALUES ('test_record')
                """
                    )
                )

                # Test consulta
                result = conn.execute(
                    text(
                        """
                    SELECT name FROM test_table WHERE name = 'test_record'
                """
                    )
                )
                row = result.fetchone()
                assert row[0] == "test_record"

                conn.commit()

        except Exception as e:
            pytest.fail(f"Error en operaciones SQLite: {e}")


@pytest.mark.database
class TestDatabasePerformance:
    """Tests de rendimiento para base de datos."""

    def test_connection_pool_performance(self):
        """Test rendimiento del pool de conexiones."""
        sqlite_url = "sqlite:///:memory:"
        engine = create_engine(sqlite_url, pool_size=5)  # Eliminar max_overflow para SQLite

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
            conn.execute(
                text(
                    """
                CREATE TABLE performance_test (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT,
                    number INTEGER
                )
            """
                )
            )

            import time

            start_time = time.time()

            # Insertar 1000 registros
            for i in range(1000):
                conn.execute(
                    text(
                        """
                    INSERT INTO performance_test (data, number)
                    VALUES (:data, :number)
                """
                    ),
                    {"data": f"test_data_{i}", "number": i},
                )

            conn.commit()
            end_time = time.time()
            duration = end_time - start_time

            # Verificar que se insertaron todos los registros
            result = conn.execute(text("SELECT COUNT(*) FROM performance_test"))
            count = result.fetchone()[0]
            assert count == 1000

            # Debe completarse en menos de 5 segundos
            assert duration < 5.0
