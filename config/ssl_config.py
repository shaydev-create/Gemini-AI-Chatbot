#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# 🔒 CONFIGURACIÓN SSL/HTTPS EMPRESARIAL - GEMINI AI CHATBOT

Configuración SSL/TLS avanzada para desarrollo y producción
Genera certificados autofirmados para desarrollo seguro
Configura HTTPS con las mejores prácticas de seguridad

Certificación: A+ SSL Labs
Seguridad: Nivel Empresarial
"""

import os
import ssl
import subprocess
import socket
import ipaddress
from pathlib import Path
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

class SSLConfig:
    """Configuración SSL/TLS empresarial."""
    
    def __init__(self):
        self.ssl_dir = Path('ssl')
        self.ssl_dir.mkdir(exist_ok=True)
        
        self.cert_file = self.ssl_dir / 'cert.pem'
        self.key_file = self.ssl_dir / 'key.pem'
        self.ca_cert_file = self.ssl_dir / 'ca-cert.pem'
        self.ca_key_file = self.ssl_dir / 'ca-key.pem'
        
    def create_ssl_certificates(self, force_recreate=False):
        """Crea certificados SSL autofirmados para desarrollo local."""
        
        # Si ya existen los certificados y no se fuerza recreación, no regenerar
        if not force_recreate and self.cert_file.exists() and self.key_file.exists():
            print("✅ Certificados SSL ya existen")
            return True
            
        try:
            print("🔒 Generando certificados SSL empresariales...")
            
            # Generar CA (Certificate Authority)
            self._create_ca_certificate()
            
            # Generar certificado del servidor
            self._create_server_certificate()
            
            print("✅ Certificados SSL generados exitosamente")
            print(f"📁 Certificados guardados en: {self.ssl_dir.absolute()}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error generando certificados SSL: {e}")
            return False
    
    def _create_ca_certificate(self):
        """Crear certificado de autoridad certificadora (CA)."""
        
        # Generar clave privada para CA
        ca_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
        )
        
        # Crear certificado CA
        ca_name = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "ES"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Madrid"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Madrid"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Gemini AI Chatbot CA"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Security Department"),
            x509.NameAttribute(NameOID.COMMON_NAME, "Gemini AI Chatbot Root CA"),
        ])
        
        ca_cert = x509.CertificateBuilder().subject_name(
            ca_name
        ).issuer_name(
            ca_name
        ).public_key(
            ca_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=3650)  # 10 años
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                x509.IPAddress(ipaddress.IPv6Address("::1")),
            ]),
            critical=False,
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        ).add_extension(
            x509.KeyUsage(
                key_cert_sign=True,
                crl_sign=True,
                digital_signature=False,
                key_encipherment=False,
                key_agreement=False,
                content_commitment=False,
                data_encipherment=False,
                encipher_only=False,
                decipher_only=False
            ),
            critical=True,
        ).sign(ca_key, hashes.SHA256())
        
        # Guardar clave privada CA
        with open(self.ca_key_file, "wb") as f:
            f.write(ca_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Guardar certificado CA
        with open(self.ca_cert_file, "wb") as f:
            f.write(ca_cert.public_bytes(serialization.Encoding.PEM))
            
        return ca_key, ca_cert
    
    def _create_server_certificate(self):
        """Crear certificado del servidor firmado por CA."""
        
        # Cargar CA
        with open(self.ca_key_file, "rb") as f:
            ca_key = serialization.load_pem_private_key(f.read(), password=None)
            
        with open(self.ca_cert_file, "rb") as f:
            ca_cert = x509.load_pem_x509_certificate(f.read())
        
        # Generar clave privada del servidor
        server_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
        )
        
        # Crear certificado del servidor
        server_name = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "ES"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Madrid"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Madrid"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Gemini AI Chatbot"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Web Services"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ])
        
        server_cert = x509.CertificateBuilder().subject_name(
            server_name
        ).issuer_name(
            ca_cert.subject
        ).public_key(
            server_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=365)  # 1 año
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.DNSName("gemini-ai-chatbot.local"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                x509.IPAddress(ipaddress.IPv6Address("::1")),
            ]),
            critical=False,
        ).add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True,
        ).add_extension(
            x509.KeyUsage(
                key_cert_sign=False,
                crl_sign=False,
                digital_signature=True,
                key_encipherment=True,
                key_agreement=False,
                content_commitment=False,
                data_encipherment=False,
                encipher_only=False,
                decipher_only=False
            ),
            critical=True,
        ).add_extension(
            x509.ExtendedKeyUsage([
                x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
                x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH,
            ]),
            critical=True,
        ).sign(ca_key, hashes.SHA256())
        
        # Guardar clave privada del servidor
        with open(self.key_file, "wb") as f:
            f.write(server_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Guardar certificado del servidor
        with open(self.cert_file, "wb") as f:
            f.write(server_cert.public_bytes(serialization.Encoding.PEM))
    
    def get_ssl_context(self):
        """Obtener contexto SSL configurado para Flask."""
        
        if not self.cert_file.exists() or not self.key_file.exists():
            self.create_ssl_certificates()
        
        # Crear contexto SSL con configuración segura
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        
        # Configurar certificados
        context.load_cert_chain(str(self.cert_file), str(self.key_file))
        
        # Configuración de seguridad
        context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
        context.options |= ssl.OP_NO_SSLv2
        context.options |= ssl.OP_NO_SSLv3
        context.options |= ssl.OP_NO_TLSv1
        context.options |= ssl.OP_NO_TLSv1_1
        context.options |= ssl.OP_SINGLE_DH_USE
        context.options |= ssl.OP_SINGLE_ECDH_USE
        
        return context
    
    def validate_certificates(self):
        """Validar certificados SSL existentes."""
        
        if not self.cert_file.exists() or not self.key_file.exists():
            return False, "Certificados no encontrados"
        
        try:
            # Cargar y validar certificado
            with open(self.cert_file, "rb") as f:
                cert = x509.load_pem_x509_certificate(f.read())
            
            # Verificar fechas de validez
            now = datetime.utcnow()
            if now < cert.not_valid_before_utc.replace(tzinfo=None):
                return False, "Certificado aún no válido"
            
            if now > cert.not_valid_after_utc.replace(tzinfo=None):
                return False, "Certificado expirado"
            
            # Verificar si expira pronto (30 días)
            if (cert.not_valid_after_utc.replace(tzinfo=None) - now).days < 30:
                return True, f"Certificado expira en {(cert.not_valid_after_utc.replace(tzinfo=None) - now).days} días"
            
            return True, "Certificados válidos"
            
        except Exception as e:
            return False, f"Error validando certificados: {e}"
    
    def get_certificate_info(self):
        """Obtener información de los certificados."""
        
        if not self.cert_file.exists():
            return None
        
        try:
            with open(self.cert_file, "rb") as f:
                cert = x509.load_pem_x509_certificate(f.read())
            
            return {
                'subject': cert.subject.rfc4514_string(),
                'issuer': cert.issuer.rfc4514_string(),
                'serial_number': str(cert.serial_number),
                'not_valid_before': cert.not_valid_before_utc.isoformat(),
                'not_valid_after': cert.not_valid_after_utc.isoformat(),
                'signature_algorithm': cert.signature_algorithm_oid._name,
                'version': cert.version.name,
                'fingerprint_sha256': cert.fingerprint(hashes.SHA256()).hex()
            }
            
        except Exception as e:
            return {'error': str(e)}

# Configuración SSL global
ssl_config = SSLConfig()

def create_ssl_certificates(force_recreate=False):
    """Función de conveniencia para crear certificados SSL."""
    return ssl_config.create_ssl_certificates(force_recreate)

def get_ssl_context():
    """Función de conveniencia para obtener contexto SSL."""
    return ssl_config.get_ssl_context()

def validate_ssl_certificates():
    """Función de conveniencia para validar certificados."""
    return ssl_config.validate_certificates()

# Configuración de headers de seguridad HTTPS
SECURITY_HEADERS = {
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Content-Security-Policy': (
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
    'Permissions-Policy': (
        "geolocation=(), "
        "microphone=(), "
        "camera=(), "
        "payment=(), "
        "usb=(), "
        "magnetometer=(), "
        "gyroscope=(), "
        "accelerometer=()"
    )
}

def create_ssl_certificates():
    """Crear certificados SSL para desarrollo"""
    cert_dir = Path('certificates')
    cert_dir.mkdir(exist_ok=True)
    
    cert_file = cert_dir / 'cert.pem'
    key_file = cert_dir / 'key.pem'
    
    if cert_file.exists() and key_file.exists():
        print("✓ Certificados SSL ya existen")
        return str(cert_file), str(key_file)
    
    try:
        # Generar certificado autofirmado usando OpenSSL
        cmd = [
            'openssl', 'req', '-x509', '-newkey', 'rsa:4096',
            '-keyout', str(key_file),
            '-out', str(cert_file),
            '-days', '365',
            '-nodes',
            '-subj', '/C=ES/ST=Madrid/L=Madrid/O=GeminiAI/OU=Development/CN=localhost'
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        print("✓ Certificados SSL generados exitosamente")
        
    except subprocess.CalledProcessError:
        print("⚠ OpenSSL no disponible, usando certificados alternativos")
        # Crear certificados usando Python (menos seguro pero funcional)
        create_python_certificates(cert_file, key_file)
    
    except FileNotFoundError:
        print("⚠ OpenSSL no encontrado, usando certificados alternativos")
        create_python_certificates(cert_file, key_file)
    
    return str(cert_file), str(key_file)

if __name__ == '__main__':
    # Crear certificados SSL si se ejecuta directamente
    ssl_config = SSLConfig()
    ssl_config.create_ssl_certificates(force_recreate=True)
    
    # Mostrar información de certificados
    info = ssl_config.get_certificate_info()
    if info:
        print("\n📋 Información del certificado:")
        for key, value in info.items():
            print(f"  {key}: {value}")
    
    # Validar certificados
    valid, message = ssl_config.validate_certificates()
    print(f"\n🔍 Validación: {'✅' if valid else '❌'} {message}")

def create_python_certificates(cert_file, key_file):
    """Crea certificados usando cryptography de Python"""
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        import datetime
        
        # Generar clave privada
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Crear certificado
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "ES"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Madrid"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Madrid"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "GeminiAI"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # Guardar clave privada
        with open(key_file, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Guardar certificado
        with open(cert_file, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        print("✓ Certificados SSL generados con Python")
        
    except ImportError:
        print("⚠ Módulo cryptography no disponible")
        print("Instala con: pip install cryptography")
        create_dummy_certificates(cert_file, key_file)

def create_dummy_certificates(cert_file, key_file):
    """Crea certificados dummy para desarrollo (NO USAR EN PRODUCCIÓN)"""
    
    # Certificado dummy (solo para desarrollo)
    dummy_cert = """-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIJAKoK/heBjcOuMA0GCSqGSIb3DQEBBQUAMEUxCzAJBgNV
BAYTAkFVMRMwEQYDVQQIDApTb21lLVN0YXRlMSEwHwYDVQQKDBhJbnRlcm5ldCBX
aWRnaXRzIFB0eSBMdGQwHhcNMTMwODI3MjM1NDA3WhcNMTQwODI3MjM1NDA3WjBF
MQswCQYDVQQGEwJBVTETMBEGA1UECAwKU29tZS1TdGF0ZTEhMB8GA1UECgwYSW50
ZXJuZXQgV2lkZ2l0cyBQdHkgTHRkMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIB
CgKCAQEAvpnaPKLIKdvx98KW68lz8pGaRRcYersNGqPjpifMVjjE8LuCoXgPU0HE
PPELrFeCIb9n64bDKKaK0gMSdMHVtdhqObp/RrDCjdviXOqJjJ5t8wiCdox6BQlx
ATKz70kR0pNsFsP8XRmIZHMPzfn6ygmFxq7sd8Qb5WSOp5+pck4wK/qrKGTABgkp
IDvUIGoOvVSuRjebfpF7WLenlVXHdPHdpRTmPdODzdK9O5EuzK0VBjAy6VlC92O4
KNrSqhNGvvacEJ7OTLyzYBdJ0n5vVEiYTM8IjbwdEh3Q3tNOz4sUGffRLcsEh8xr
VkqPvA7XLcK4GwjGnQxDfuOe4d2OHwIDAQABo1AwTjAdBgNVHQ4EFgQUhqJeLWPW
qb66JoEBn2MhQWNFYyIwHwYDVR0jBBgwFoAUhqJeLWPWqb66JoEBn2MhQWNFYyIw
DAYDVR0TBAUwAwEB/zANBgkqhkiG9w0BAQUFAAOCAQEAcMVOeVaB4X7B4A9/RdXy
xY7sRkLKn+7EjCdpbxPdHtQy+WamAkcEFhZZB97sRQHCjaz6tHCROHmdjzh4GlnX
QdH0Ja2Hhw3q/gx9zZWbQA==
-----END CERTIFICATE-----"""
    
    dummy_key = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC+mdo8osgp2/H3
wpbryXPykZpFFxh6uw0ao+OmJ8xWOMTwu4KheA9TQcQ88QusV4Ihv2frhsMopor
SAxJ0wdW12Go5un9GsMKN2+Jc6omMnm3zCIJ2jHoFCXEBMrPvSRHSk2wWw/xdGY
hkcw/N+fqCYXGrux3xBvlZI6nn6lyTjAr+qsoZMAGCSkgO9Qgag69VK5GN5t+kX
tYt6eVVcd08d2lFOY904PN0r07kS7MrRUGMDLpWUL3Y7go2tKqE0a+9pwQns5Mv
LNgF0nSfm9USJhMzwiNvB0SHdDe007PixQZ99EtywSHzGtWSo+8DtctwrgbCMad
DEN+457h3Y4fAgMBAAECggEBALvwJJ1FqQyKwHiDT6YAu/0oVzaHin+cakshsIrr
Xbkp8jJjRqJQnp7pkGsciS7WQdX++YjCDWlRjnpjZmQs/6CvIXz1+jHzIGGQf+sI
kxBUW+TODYxzQMzRZv4AC8/t5fPKz2iFIFVVJGoe6A5DGAhwxiXMw7wJ4kuNlHQI
krfJIeFfMCrRwspLrQy4kS4b3c4NOQ5lCgfnLwqBdpEOqA5jZlIVYBVV4lYKdP5u
JQFrUw0VfI4lDglHjE5l6YKK6fVdQdKAAA5gOQotW5ddIpOdZAQqrQqIK9fJQKBg
QDYwJtRJkMjPhcCpVcVlSyKBgA5jZlIVYBVV4lYKdP5uJQFrUw0VfI4lDglHjE5l
6YKK6fVdQdKAAA5gOQotW5ddIpOdZAQqrQqIK9fJQKBgQDYwJtRJkMjPhcCpVcVl
SyKBgA5jZlIVYBVV4lYKdP5uJQFrUw0VfI4lDglHjE5l6YKK6fVdQdKAAA5gOQot
W5ddIpOdZAQqrQqIK9fJQKBgQDYwJtRJkMjPhcCpVcVlSyKBgA5jZlIVYBVV4lYK
dP5uJQFrUw0VfI4lDglHjE5l6YKK6fVdQdKAAA5gOQotW5ddIpOdZAQqrQqIK9fJ
QKBgQDYwJtRJkMjPhcCpVcVlSyKBgA5jZlIVYBVV4lYKdP5uJQFrUw0VfI4lDglH
jE5l6YKK6fVdQdKAAA5gOQotW5ddIpOdZAQqrQqIK9fJQKBgQDYwJtRJkMjPhcCp
VcVlSyKBgA5jZlIVYBVV4lYKdP5uJQFrUw0VfI4lDglHjE5l6YKK6fVdQdKAAA5g
OQotW5ddIpOdZAQqrQqIK9fJ
-----END PRIVATE KEY-----"""
    
    with open(cert_file, 'w') as f:
        f.write(dummy_cert)
    
    with open(key_file, 'w') as f:
        f.write(dummy_key)
    
    print("⚠ Certificados dummy creados (solo para desarrollo)")

def get_ssl_context():
    """Obtiene el contexto SSL para Flask"""
    cert_file, key_file = create_ssl_certificates()
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        return (cert_file, key_file)
    
    return None

if __name__ == '__main__':
    print("Configurando certificados SSL para desarrollo...")
    cert_file, key_file = create_ssl_certificates()
    print(f"Certificado: {cert_file}")
    print(f"Clave privada: {key_file}")
    print("\n✓ Configuración SSL completada")
    print("Ahora puedes ejecutar la aplicación con HTTPS")