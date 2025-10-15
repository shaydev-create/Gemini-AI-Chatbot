import ssl
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch, ANY

import pytest
from cryptography.hazmat.primitives import serialization

from app.config.ssl_config import (
    SECURITY_HEADERS,
    SSLConfig,
    create_ssl_certificates,
    get_ssl_context,
    validate_ssl_certificates,
)


@pytest.fixture
def mock_ssl_config_instance(tmp_path):
    """Fixture para una instancia de SSLConfig con un directorio temporal."""
    return SSLConfig(base_dir=tmp_path)


@pytest.fixture
def mock_certs_exist(mock_ssl_config_instance):
    """Fixture para simular que los certificados existen."""
    mock_ssl_config_instance.cert_file.touch()
    mock_ssl_config_instance.key_file.touch()
    mock_ssl_config_instance.ca_cert_file.touch()
    mock_ssl_config_instance.ca_key_file.touch()


class TestSSLConfig:
    def test_init(self, tmp_path):
        """Verifica que el directorio SSL se crea y las rutas de archivo son correctas."""
        ssl_config = SSLConfig(base_dir=tmp_path)
        assert ssl_config.ssl_dir.exists()
        assert ssl_config.ssl_dir == tmp_path / "ssl"
        assert ssl_config.cert_file == tmp_path / "ssl" / "cert.pem"
        assert ssl_config.key_file == tmp_path / "ssl" / "key.pem"
        assert ssl_config.ca_cert_file == tmp_path / "ssl" / "ca-cert.pem"
        assert ssl_config.ca_key_file == tmp_path / "ssl" / "ca-key.pem"

    @patch("app.config.ssl_config.SSLConfig._create_ca_certificate")
    @patch("app.config.ssl_config.SSLConfig._create_server_certificate")
    def test_create_ssl_certificates_recreate(
        self, mock_create_server, mock_create_ca, mock_ssl_config_instance
    ):
        """Verifica la creación forzada de certificados."""
        cert, key = mock_ssl_config_instance.create_ssl_certificates(
            force_recreate=True
        )
        mock_create_ca.assert_called_once()
        mock_create_server.assert_called_once()
        assert cert == str(mock_ssl_config_instance.cert_file)
        assert key == str(mock_ssl_config_instance.key_file)

    @patch("app.config.ssl_config.SSLConfig._create_ca_certificate")
    @patch("app.config.ssl_config.SSLConfig._create_server_certificate")
    def test_create_ssl_certificates_exist(
        self,
        mock_create_server,
        mock_create_ca,
        mock_ssl_config_instance,
        mock_certs_exist,
    ):
        """Verifica que no se recrean certificados si ya existen y no se fuerza la recreación."""
        cert, key = mock_ssl_config_instance.create_ssl_certificates(
            force_recreate=False
        )
        mock_create_ca.assert_not_called()
        mock_create_server.assert_not_called()
        assert cert == str(mock_ssl_config_instance.cert_file)
        assert key == str(mock_ssl_config_instance.key_file)

    @patch("app.config.ssl_config.logger")
    @patch(
        "app.config.ssl_config.SSLConfig._create_ca_certificate",
        side_effect=Exception("Test Error"),
    )
    def test_create_ssl_certificates_error(
        self, mock_create_ca, mock_logger, mock_ssl_config_instance
    ):
        """Verifica el manejo de errores durante la creación de certificados."""
        cert, key = mock_ssl_config_instance.create_ssl_certificates(
            force_recreate=True
        )
        mock_logger.exception.assert_called_once_with(
            "❌ Error crítico al generar los certificados SSL."
        )
        assert cert is None
        assert key is None

    @patch("app.config.ssl_config.rsa.generate_private_key")
    @patch("app.config.ssl_config.x509.CertificateBuilder")
    @patch("builtins.open")
    def test_create_ca_certificate(
        self, mock_open, mock_cert_builder, mock_rsa_key, mock_ssl_config_instance
    ):
        """Verifica la creación del certificado CA."""
        mock_key_instance = MagicMock()
        mock_key_instance.private_bytes.return_value = b"private key bytes"
        mock_rsa_key.return_value = mock_key_instance
        mock_cert_instance = MagicMock()
        mock_cert_instance.public_bytes.return_value = b"public cert bytes"
        mock_cert_builder.return_value.subject_name.return_value.issuer_name.return_value.public_key.return_value.serial_number.return_value.not_valid_before.return_value.not_valid_after.return_value.add_extension.return_value.add_extension.return_value.add_extension.return_value.sign.return_value = mock_cert_instance

        mock_file_handle = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file_handle

        # Create the actual files so the existence checks pass
        mock_ssl_config_instance.ca_key_file.parent.mkdir(parents=True, exist_ok=True)
        mock_ssl_config_instance.ca_key_file.touch()
        mock_ssl_config_instance.ca_cert_file.touch()

        mock_ssl_config_instance._create_ca_certificate()

        mock_rsa_key.assert_called_once()
        mock_cert_builder.assert_called_once()
        mock_key_instance.private_bytes.assert_called_once_with(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=ANY,
        )
        mock_cert_instance.public_bytes.assert_called_once_with(
            serialization.Encoding.PEM
        )
        assert mock_file_handle.write.call_count == 2
        assert mock_ssl_config_instance.ca_key_file.exists()
        assert mock_ssl_config_instance.ca_cert_file.exists()

    @patch("app.config.ssl_config.rsa.generate_private_key")
    @patch("app.config.ssl_config.x509.CertificateBuilder")
    @patch("app.config.ssl_config.serialization.load_pem_private_key")
    @patch("app.config.ssl_config.x509.load_pem_x509_certificate")
    @patch("builtins.open")
    def test_create_server_certificate(
        self,
        mock_open,
        mock_load_cert,
        mock_load_key,
        mock_cert_builder,
        mock_rsa_key,
        mock_ssl_config_instance,
        mock_certs_exist,
    ):
        """Verifica la creación del certificado del servidor."""
        mock_ca_key_instance = MagicMock()
        mock_load_key.return_value = mock_ca_key_instance

        mock_ca_cert_instance = MagicMock()
        mock_ca_cert_instance.subject.rfc4514_string.return_value = (
            "CN=Gemini AI Chatbot Root CA"
        )
        mock_load_cert.return_value = mock_ca_cert_instance

        mock_server_key_instance = MagicMock()
        mock_server_key_instance.private_bytes.return_value = (
            b"server private key bytes"
        )
        mock_rsa_key.return_value = mock_server_key_instance
        mock_server_cert_instance = MagicMock()
        mock_server_cert_instance.public_bytes.return_value = (
            b"server public cert bytes"
        )
        mock_cert_builder.return_value.subject_name.return_value.issuer_name.return_value.public_key.return_value.serial_number.return_value.not_valid_before.return_value.not_valid_after.return_value.add_extension.return_value.add_extension.return_value.add_extension.return_value.add_extension.return_value.sign.return_value = mock_server_cert_instance

        mock_file_handle = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file_handle

        # Create the actual files so the existence checks pass
        mock_ssl_config_instance.key_file.parent.mkdir(parents=True, exist_ok=True)
        mock_ssl_config_instance.key_file.touch()
        mock_ssl_config_instance.cert_file.touch()

        mock_ssl_config_instance._create_server_certificate()

        mock_load_key.assert_called_once()
        mock_load_cert.assert_called_once()
        mock_rsa_key.assert_called_once()
        mock_cert_builder.assert_called_once()
        mock_server_key_instance.private_bytes.assert_called_once_with(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=ANY,
        )
        mock_server_cert_instance.public_bytes.assert_called_once_with(
            serialization.Encoding.PEM
        )
        # open es llamado 4 veces: 2 para lectura (CA key/cert) y 2 para escritura (server key/cert)
        assert mock_open.call_count == 4
        # write es llamado 2 veces: una para la clave del servidor y otra para el certificado
        assert mock_file_handle.write.call_count == 2
        assert mock_ssl_config_instance.cert_file.exists()
        assert mock_ssl_config_instance.key_file.exists()

    @patch("app.config.ssl_config.ssl.SSLContext")
    @patch("app.config.ssl_config.SSLConfig.create_ssl_certificates")
    def test_get_ssl_context(
        self,
        mock_create_certs,
        mock_ssl_context,
        mock_ssl_config_instance,
        mock_certs_exist,
    ):
        """Verifica que se obtiene un contexto SSL válido."""
        mock_context_instance = MagicMock()
        mock_ssl_context.return_value = mock_context_instance

        context = mock_ssl_config_instance.get_ssl_context()

        mock_create_certs.assert_not_called()  # Certs exist
        mock_ssl_context.assert_called_once_with(ssl.PROTOCOL_TLS_SERVER)
        mock_context_instance.load_cert_chain.assert_called_once_with(
            str(mock_ssl_config_instance.cert_file),
            str(mock_ssl_config_instance.key_file),
        )
        assert context == mock_context_instance

    @patch("app.config.ssl_config.ssl.SSLContext")
    @patch("app.config.ssl_config.SSLConfig.create_ssl_certificates")
    def test_get_ssl_context_certs_not_exist(
        self, mock_create_certs, mock_ssl_context, mock_ssl_config_instance
    ):
        """Verifica que se crean certificados si no existen al obtener el contexto SSL."""
        # Simulate certs not existing
        mock_ssl_config_instance.cert_file.unlink(missing_ok=True)
        mock_ssl_config_instance.key_file.unlink(missing_ok=True)

        mock_context_instance = MagicMock()
        mock_ssl_context.return_value = mock_context_instance

        context = mock_ssl_config_instance.get_ssl_context()

        mock_create_certs.assert_called_once()
        mock_ssl_context.assert_called_once_with(ssl.PROTOCOL_TLS_SERVER)
        mock_context_instance.load_cert_chain.assert_called_once_with(
            str(mock_ssl_config_instance.cert_file),
            str(mock_ssl_config_instance.key_file),
        )
        assert context == mock_context_instance

    @patch("app.config.ssl_config.x509.load_pem_x509_certificate")
    @patch("builtins.open")
    def test_validate_certificates_valid(
        self, mock_open, mock_load_cert, mock_ssl_config_instance, mock_certs_exist
    ):
        """Verifica la validación de certificados válidos."""
        mock_cert = MagicMock()
        # Create timezone-aware datetime objects for the certificate
        now_utc = datetime.now(timezone.utc)
        before_utc = now_utc - timedelta(days=10)
        after_utc = now_utc + timedelta(days=60)
        
        # Mock the certificate datetime attributes with replace method
        mock_before = MagicMock()
        mock_before.replace.return_value = before_utc.replace(tzinfo=None)
        mock_after = MagicMock()
        mock_after.replace.return_value = after_utc.replace(tzinfo=None)
        
        mock_cert.not_valid_before_utc = mock_before
        mock_cert.not_valid_after_utc = mock_after
        mock_cert.subject.rfc4514_string.return_value = "CN=test_subject"
        mock_cert.issuer.rfc4514_string.return_value = "CN=test_issuer"
        mock_cert.serial_number = 12345
        mock_cert.signature_algorithm_oid._name = "SHA256"
        mock_cert.version.name = "v3"
        mock_cert.fingerprint.return_value.hex.return_value = "test_fingerprint"
        mock_load_cert.return_value = mock_cert

        valid, message = mock_ssl_config_instance.validate_certificates()
        assert valid is True
        assert "Certificados válidos" in message

    @patch("app.config.ssl_config.x509.load_pem_x509_certificate")
    @patch("builtins.open")
    def test_validate_certificates_expired(
        self, mock_open, mock_load_cert, mock_ssl_config_instance, mock_certs_exist
    ):
        """Verifica la validación de certificados expirados."""
        mock_cert = MagicMock()
        # Create timezone-aware datetime objects for the certificate
        now_utc = datetime.now(timezone.utc)
        before_utc = now_utc - timedelta(days=60)
        after_utc = now_utc - timedelta(days=10)
        
        # Mock the certificate datetime attributes with replace method
        mock_before = MagicMock()
        mock_before.replace.return_value = before_utc.replace(tzinfo=None)
        mock_after = MagicMock()
        mock_after.replace.return_value = after_utc.replace(tzinfo=None)
        
        mock_cert.not_valid_before_utc = mock_before
        mock_cert.not_valid_after_utc = mock_after
        mock_cert.subject.rfc4514_string.return_value = "CN=test_subject"
        mock_cert.issuer.rfc4514_string.return_value = "CN=test_issuer"
        mock_cert.serial_number = 12345
        mock_cert.signature_algorithm_oid._name = "SHA256"
        mock_cert.version.name = "v3"
        mock_cert.fingerprint.return_value.hex.return_value = "test_fingerprint"
        mock_load_cert.return_value = mock_cert

        valid, message = mock_ssl_config_instance.validate_certificates()
        assert valid is False
        assert "Certificado expirado" in message

    @patch("app.config.ssl_config.x509.load_pem_x509_certificate")
    @patch("builtins.open")
    def test_validate_certificates_not_yet_valid(
        self, mock_open, mock_load_cert, mock_ssl_config_instance, mock_certs_exist
    ):
        """Verifica la validación de certificados aún no válidos."""
        mock_cert = MagicMock()
        # Create timezone-aware datetime objects for the certificate
        now_utc = datetime.now(timezone.utc)
        before_utc = now_utc + timedelta(days=10)
        after_utc = now_utc + timedelta(days=60)
        
        # Mock the certificate datetime attributes with replace method
        mock_before = MagicMock()
        mock_before.replace.return_value = before_utc.replace(tzinfo=None)
        mock_after = MagicMock()
        mock_after.replace.return_value = after_utc.replace(tzinfo=None)
        
        mock_cert.not_valid_before_utc = mock_before
        mock_cert.not_valid_after_utc = mock_after
        mock_cert.subject.rfc4514_string.return_value = "CN=test_subject"
        mock_cert.issuer.rfc4514_string.return_value = "CN=test_issuer"
        mock_cert.serial_number = 12345
        mock_cert.signature_algorithm_oid._name = "SHA256"
        mock_cert.version.name = "v3"
        mock_cert.fingerprint.return_value.hex.return_value = "test_fingerprint"
        mock_load_cert.return_value = mock_cert

        valid, message = mock_ssl_config_instance.validate_certificates()
        assert valid is False
        assert "Certificado aún no válido" in message

    @patch("app.config.ssl_config.x509.load_pem_x509_certificate")
    @patch("builtins.open")
    def test_validate_certificates_expiring_soon(
        self, mock_open, mock_load_cert, mock_ssl_config_instance, mock_certs_exist
    ):
        """Verifica la validación de certificados que expiran pronto."""
        mock_cert = MagicMock()
        # Create timezone-aware datetime objects for the certificate
        now_utc = datetime.now(timezone.utc)
        before_utc = now_utc - timedelta(days=10)
        after_utc = now_utc + timedelta(days=15)
        
        # Mock the certificate datetime attributes with replace method
        mock_before = MagicMock()
        mock_before.replace.return_value = before_utc.replace(tzinfo=None)
        mock_after = MagicMock()
        mock_after.replace.return_value = after_utc.replace(tzinfo=None)
        
        mock_cert.not_valid_before_utc = mock_before
        mock_cert.not_valid_after_utc = mock_after
        mock_cert.subject.rfc4514_string.return_value = "CN=test_subject"
        mock_cert.issuer.rfc4514_string.return_value = "CN=test_issuer"
        mock_cert.serial_number = 12345
        mock_cert.signature_algorithm_oid._name = "SHA256"
        mock_cert.version.name = "v3"
        mock_cert.fingerprint.return_value.hex.return_value = "test_fingerprint"
        mock_load_cert.return_value = mock_cert

        valid, message = mock_ssl_config_instance.validate_certificates()
        assert valid is True
        assert "Certificado expira en 15 días" in message

    def test_validate_certificates_not_found(self, mock_ssl_config_instance):
        """Verifica la validación cuando no se encuentran los certificados."""
        valid, message = mock_ssl_config_instance.validate_certificates()
        assert valid is False
        assert "Certificados no encontrados" in message

    @patch("app.config.ssl_config.logger")
    @patch(
        "app.config.ssl_config.x509.load_pem_x509_certificate",
        side_effect=Exception("Parse Error"),
    )
    @patch("builtins.open")
    def test_validate_certificates_error(
        self,
        mock_open,
        mock_load_cert,
        mock_logger,
        mock_ssl_config_instance,
        mock_certs_exist,
    ):
        """Verifica el manejo de errores durante la validación de certificados."""
        valid, message = mock_ssl_config_instance.validate_certificates()
        assert valid is False
        assert "Error validando certificados: Parse Error" in message

    @patch("app.config.ssl_config.x509.load_pem_x509_certificate")
    @patch("builtins.open")
    def test_get_certificate_info(
        self, mock_open, mock_load_cert, mock_ssl_config_instance, mock_certs_exist
    ):
        """Verifica la obtención de información del certificado."""
        mock_cert = MagicMock()
        mock_cert.subject.rfc4514_string.return_value = "subject_test"
        mock_cert.issuer.rfc4514_string.return_value = "issuer_test"
        mock_cert.serial_number = 12345
        mock_cert.not_valid_before_utc = datetime(2023, 1, 1, tzinfo=timezone.utc)
        mock_cert.not_valid_after_utc = datetime(2024, 1, 1, tzinfo=timezone.utc)
        mock_cert.signature_algorithm_oid._name = "SHA256"
        mock_cert.version.name = "v3"
        mock_cert.fingerprint.return_value.hex.return_value = "fingerprint_test"
        mock_load_cert.return_value = mock_cert

        info = mock_ssl_config_instance.get_certificate_info()
        assert info is not None
        assert info["subject"] == "subject_test"
        assert info["issuer"] == "issuer_test"
        assert info["serial_number"] == "12345"
        assert info["not_valid_before"] == "2023-01-01T00:00:00+00:00"
        assert info["not_valid_after"] == "2024-01-01T00:00:00+00:00"
        assert info["signature_algorithm"] == "SHA256"
        assert info["version"] == "v3"
        assert info["fingerprint_sha256"] == "fingerprint_test"

    def test_get_certificate_info_no_cert(self, mock_ssl_config_instance):
        """Verifica que se devuelve None si no hay certificado."""
        info = mock_ssl_config_instance.get_certificate_info()
        assert info is None

    @patch("app.config.ssl_config.logger")
    @patch(
        "app.config.ssl_config.x509.load_pem_x509_certificate",
        side_effect=Exception("Info Error"),
    )
    @patch("builtins.open")
    def test_get_certificate_info_error(
        self,
        mock_open,
        mock_load_cert,
        mock_logger,
        mock_ssl_config_instance,
        mock_certs_exist,
    ):
        """Verifica el manejo de errores al obtener información del certificado."""
        info = mock_ssl_config_instance.get_certificate_info()
        assert info == {"error": "Info Error"}


class TestModuleFunctions:
    @patch("app.config.ssl_config.ssl_config")
    def test_create_ssl_certificates_func(self, mock_ssl_config):
        """Verifica la función de conveniencia create_ssl_certificates."""
        create_ssl_certificates(force_recreate=True)
        mock_ssl_config.create_ssl_certificates.assert_called_once_with(True)

    @patch("app.config.ssl_config.ssl_config")
    def test_get_ssl_context_func(self, mock_ssl_config):
        """Verifica la función de conveniencia get_ssl_context."""
        get_ssl_context()
        mock_ssl_config.get_ssl_context.assert_called_once()

    @patch("app.config.ssl_config.ssl_config")
    def test_validate_ssl_certificates_func(self, mock_ssl_config):
        """Verifica la función de conveniencia validate_ssl_certificates."""
        validate_ssl_certificates()
        mock_ssl_config.validate_certificates.assert_called_once()

    def test_security_headers(self):
        """Verifica que los SECURITY_HEADERS están definidos y tienen contenido."""
        assert isinstance(SECURITY_HEADERS, dict)
        assert len(SECURITY_HEADERS) > 0
        assert "Strict-Transport-Security" in SECURITY_HEADERS
        assert "Content-Security-Policy" in SECURITY_HEADERS
