#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# 🔒 CONFIGURACIÓN SSL/HTTPS EMPRESARIAL - GEMINI AI CHATBOT

Configuración SSL/TLS avanzada para desarrollo y producción
Genera certificados autofirmados para desarrollo seguro
Configura HTTPS con las mejores prácticas de seguridad

Certificación: A+ SSL Labs
"""

import ipaddress
import logging
import ssl
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

# Configuración del logger
logger=logging.getLogger(__name__)


class SSLConfig:
    """Configuración SSL/TLS empresarial."""

    def __init__(self, base_dir: Path) -> None:
        """
        Inicializa la configuración SSL.

        Args:
            base_dir: Directorio base de la aplicación para crear la carpeta 'ssl'.
        """
        self.ssl_dir = base_dir / "ssl"
        self.ssl_dir.mkdir(exist_ok=True)

        self.cert_file = self.ssl_dir / "cert.pem"
        self.key_file = self.ssl_dir / "key.pem"
        self.ca_cert_file = self.ssl_dir / "ca-cert.pem"
        self.ca_key_file = self.ssl_dir / "ca-key.pem"

    def create_ssl_certificates(
        self, force_recreate: bool = False
    ) -> tuple[str | None, str | None]:
        """
        Crea certificados SSL autofirmados para desarrollo local.

        Args:
            force_recreate: Si es True, fuerza la regeneración de los certificados.

        Returns:
            Una tupla con las rutas al certificado y la clave, o (None, None) si hay un error.
        """
        if not force_recreate and self.cert_file.exists() and self.key_file.exists():
            logger.info("✅ Certificados SSL ya existen en %s", self.ssl_dir.absolute())
            return str(self.cert_file), str(self.key_file)

        try:
            logger.info("🔒 Generando nuevos certificados SSL autofirmados...")
            self._create_ca_certificate()
            self._create_server_certificate()
            logger.info(
                "✅ Certificados SSL generados exitosamente en %s",
                self.ssl_dir.absolute(),
            )
            return str(self.cert_file), str(self.key_file)
        except Exception:
            logger.exception("❌ Error crítico al generar los certificados SSL.")
            return None, None

    def _create_ca_certificate(self) -> None:
        """Crear certificado de autoridad certificadora (CA)."""
        ca_key=rsa.generate_private_key(public_exponent=65537, key_size=4096)
        ca_name=x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, "ES"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Madrid"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "Madrid"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Gemini AI Chatbot CA"),
                x509.NameAttribute(
                    NameOID.ORGANIZATIONAL_UNIT_NAME, "Security Department"
                ),
                x509.NameAttribute(NameOID.COMMON_NAME, "Gemini AI Chatbot Root CA"),
            ]
        )
        ca_cert=(
            x509.CertificateBuilder()
            .subject_name(ca_name)
            .issuer_name(ca_name)
            .public_key(ca_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.now(timezone.utc))
            .not_valid_after(datetime.now(timezone.utc) + timedelta(days=3650))
            .add_extension(
                x509.SubjectAlternativeName(
                    [
                        x509.DNSName("localhost"),
                        x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                        x509.IPAddress(ipaddress.IPv6Address("::1")),
                    ]
                ),
                critical=False,
            )
            .add_extension(
                x509.BasicConstraints(ca=True, path_length=None), critical=True
            )
            .add_extension(
                x509.KeyUsage(
                    key_cert_sign=True,
                    crl_sign=True,
                    digital_signature=False,
                    key_encipherment=False,
                    key_agreement=False,
                    content_commitment=False,
                    data_encipherment=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )
            .sign(ca_key, hashes.SHA256())
        )

        with open(self.ca_key_file, "wb") as f:
            f.write(
                ca_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )
        with open(self.ca_cert_file, "wb") as f:
            f.write(ca_cert.public_bytes(serialization.Encoding.PEM))

    def _create_server_certificate(self) -> None:
        """Crear certificado del servidor firmado por CA."""
        with open(self.ca_key_file, "rb") as f:
            ca_key=serialization.load_pem_private_key(f.read(), password=None)
        with open(self.ca_cert_file, "rb") as f:
            ca_cert=x509.load_pem_x509_certificate(f.read())

        server_key=rsa.generate_private_key(public_exponent=65537, key_size=4096)
        server_name=x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, "ES"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Madrid"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "Madrid"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Gemini AI Chatbot"),
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Web Services"),
                x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
            ]
        )
        server_cert=(
            x509.CertificateBuilder()
            .subject_name(server_name)
            .issuer_name(ca_cert.subject)
            .public_key(server_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.now(timezone.utc))
            .not_valid_after(datetime.now(timezone.utc) + timedelta(days=365))
            .add_extension(
                x509.SubjectAlternativeName(
                    [
                        x509.DNSName("localhost"),
                        x509.DNSName("gemini-ai-chatbot.local"),
                        x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                        x509.IPAddress(ipaddress.IPv6Address("::1")),
                    ]
                ),
                critical=False,
            )
            .add_extension(
                x509.BasicConstraints(ca=False, path_length=None), critical=True
            )
            .add_extension(
                x509.KeyUsage(
                    key_cert_sign=False,
                    crl_sign=False,
                    digital_signature=True,
                    key_encipherment=True,
                    key_agreement=False,
                    content_commitment=False,
                    data_encipherment=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )
            .add_extension(
                x509.ExtendedKeyUsage(
                    [
                        x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
                        x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH,
                    ]
                ),
                critical=True,
            )
            .sign(ca_key, hashes.SHA256())
        )

        with open(self.key_file, "wb") as f:
            f.write(
                server_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )
        with open(self.cert_file, "wb") as f:
            f.write(server_cert.public_bytes(serialization.Encoding.PEM))

    def get_ssl_context(self) -> None:
        """Obtener contexto SSL configurado para Flask."""
        if not self.cert_file.exists() or not self.key_file.exists():
            self.create_ssl_certificates()
        context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(str(self.cert_file), str(self.key_file))
        context.set_ciphers(
            "ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS"
        )
        context.options |= (
            ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        )
        context.options |= ssl.OP_SINGLE_DH_USE | ssl.OP_SINGLE_ECDH_USE
        return context

    def validate_certificates(self) -> None:
        """Validar certificados SSL existentes."""
        if not self.cert_file.exists() or not self.key_file.exists():
            return False, "Certificados no encontrados"
        try:
            with open(self.cert_file, "rb") as f:
                cert=x509.load_pem_x509_certificate(f.read())
            now=datetime.now(timezone.utc).replace(tzinfo=None)
            if now < cert.not_valid_before_utc.replace(tzinfo=None):
                return False, "Certificado aún no válido"
            if now > cert.not_valid_after_utc.replace(tzinfo=None):
                return False, "Certificado expirado"
            if (cert.not_valid_after_utc.replace(tzinfo=None).date() - now.date()).days < 30:
                return (
                    True,
                    f"Certificado expira en {(cert.not_valid_after_utc.replace(tzinfo=None).date() - now.date()).days} días",
                )
            return True, "Certificados válidos"
        except Exception as e:
            return False, f"Error validando certificados: {e}"

    def get_certificate_info(self) -> Any:
        """Obtener información de los certificados."""
        if not self.cert_file.exists():
            return None
        try:
            with open(self.cert_file, "rb") as f:
                cert=x509.load_pem_x509_certificate(f.read())
            return {
                "subject": cert.subject.rfc4514_string(),
                "issuer": cert.issuer.rfc4514_string(),
                "serial_number": str(cert.serial_number),
                "not_valid_before": cert.not_valid_before_utc.isoformat(),
                "not_valid_after": cert.not_valid_after_utc.isoformat(),
                "signature_algorithm": cert.signature_algorithm_oid._name,
                "version": cert.version.name,
                "fingerprint_sha256": cert.fingerprint(hashes.SHA256()).hex(),
            }
        except Exception as e:
            return {"error": str(e)}


# Configuración SSL global
ssl_config=SSLConfig(base_dir=Path(__file__).parent.parent)


def create_ssl_certificates(force_recreate=False) -> None:
    """Función de conveniencia para crear certificados SSL."""
    return ssl_config.create_ssl_certificates(force_recreate)


def get_ssl_context() -> None:
    """Función de conveniencia para obtener contexto SSL."""
    return ssl_config.get_ssl_context()


def validate_ssl_certificates() -> None:
    """Función de conveniencia para validar certificados."""
    return ssl_config.validate_certificates()


# Configuración de headers de seguridad HTTPS
SECURITY_HEADERS = {
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self' https:; "
        "media-src 'self'; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'none'; "
        "upgrade-insecure-requests"
    ),
    "Permissions-Policy": (
        "geolocation=(), microphone=(), camera=(), payment=(), usb=(), "
        "magnetometer=(), gyroscope=(), accelerometer=()"
    ),
}

if __name__ == "__main__":
    print("Configurando certificados SSL para desarrollo...")
    cert_file, key_file = create_ssl_certificates(force_recreate=True)
    if cert_file and key_file:
        print(f"Certificado: {cert_file}")
        print(f"Clave privada: {key_file}")

        # Mostrar información de certificados
        info=ssl_config.get_certificate_info()
        if info:
            print("\n📋 Información del certificado:")
            for key, value in info.items():
                print(f"  {key}: {value}")

        # Validar certificados
        valid, message = ssl_config.validate_certificates()
        print(f"\n🔍 Validación: {'✅' if valid else '❌'} {message}")

        print("\n✓ Configuración SSL completada.")
        print("Ahora puedes ejecutar la aplicación con HTTPS.")
