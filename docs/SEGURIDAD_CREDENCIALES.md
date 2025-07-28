# 🔒 Guía de Seguridad para Credenciales

## Protección de Credenciales en GitHub

Este documento explica cómo proteger adecuadamente las credenciales y claves API en tu proyecto Gemini AI Chatbot, especialmente al usar GitHub.

## ⚠️ Problema: Exposición de Credenciales

GitHub detecta automáticamente cuando se suben credenciales o claves API a repositorios públicos y envía alertas de seguridad. Esto ocurre porque:

1. Las credenciales en archivos `.env` pueden quedar expuestas en el historial de Git
2. Las claves API y contraseñas pueden ser utilizadas por actores maliciosos
3. Violar la seguridad de las credenciales puede resultar en uso no autorizado de servicios de pago

## ✅ Solución: Protección de Archivos .env

Hemos implementado varias capas de protección para tus credenciales:

### 1. Archivo .gitignore

El archivo `.gitignore` ya está configurado para excluir archivos sensibles:

```
.env
.env.local
.env.*.local
.env.development
.env.test
.env.production
```

### 2. Archivo .env.example

Hemos creado un archivo `.env.example` que contiene la estructura del archivo de configuración pero con valores de ejemplo, sin credenciales reales.

### 3. Script de Limpieza de Credenciales

Hemos añadido un script `scripts/secure_env.py` que puedes ejecutar antes de hacer commit para limpiar automáticamente las credenciales reales de tu archivo `.env` y reemplazarlas con placeholders seguros.

### 4. Archivo .gitattributes

Hemos añadido un archivo `.gitattributes` que marca los archivos `.env` como secretos, lo que ayuda a prevenir su inclusión accidental en commits.

## 📋 Instrucciones de Uso

### Antes de hacer commit:

1. Ejecuta el script de limpieza de credenciales:

```bash
python scripts/secure_env.py
```

2. Verifica que el archivo `.env` no contenga credenciales reales:

```bash
cat .env  # En Linux/Mac
type .env  # En Windows
```

3. Procede con el commit y push

### Después de hacer pull:

Si has limpiado tus credenciales antes de hacer commit, necesitarás restaurarlas después de hacer pull:

```bash
# Si tienes un backup
cp .env.backup .env  # En Linux/Mac
copy .env.backup .env  # En Windows
```

## 🔐 Opciones Avanzadas de Seguridad

### Uso de Variables de Entorno del Sistema

En lugar de usar un archivo `.env`, considera configurar las variables de entorno directamente en tu sistema o en tu plataforma de despliegue.

### Uso de Gestores de Secretos

Para proyectos más grandes, considera usar gestores de secretos como:

- GitHub Secrets (para GitHub Actions)
- HashiCorp Vault
- AWS Secrets Manager
- Google Secret Manager

### Cifrado de Archivos con git-crypt

Para equipos que necesitan compartir credenciales de forma segura, considera usar `git-crypt` para cifrar archivos sensibles en el repositorio.

## 📚 Recursos Adicionales

- [Documentación de GitHub sobre secretos](https://docs.github.com/es/actions/security-guides/encrypted-secrets)
- [Mejores prácticas para gestión de secretos](https://docs.github.com/es/code-security/secret-scanning/about-secret-scanning)
- [Documentación de git-crypt](https://github.com/AGWA/git-crypt)

## 📞 Soporte

Si tienes preguntas sobre la seguridad de credenciales en este proyecto, contacta al equipo de desarrollo.