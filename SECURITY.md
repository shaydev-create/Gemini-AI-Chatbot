# 🔒 Guía de Seguridad - Protección de Credenciales

## ⚠️ IMPORTANTE - Manejo Seguro de Credenciales

Este proyecto utiliza credenciales sensibles que **NUNCA** deben subirse a GitHub. Sigue esta guía para mantener tu proyecto seguro.

## 📁 Archivos de Configuración

### ✅ Archivos SEGUROS para GitHub

- `.env.example` - Plantilla con marcadores de posición
- `.gitignore` - Configurado para proteger archivos sensibles
- `clean_credentials.py` - Script de limpieza automática

### ❌ Archivos que NUNCA deben subirse

- `.env` - Contiene credenciales reales
- `.env.backup` - Backup con credenciales reales
- `.env.local` - Configuración local
- `credentials/` - Directorio con archivos de credenciales
- `vertex-ai-key.json` - Claves de Google Cloud

## 🛡️ Configuración Inicial

### 1. Clonar el repositorio

```bash
git clone https://github.com/shaydev-create/Gemini-AI-Chatbot.git
cd Gemini-AI-Chatbot
```

### 2. Configurar variables de entorno

```bash
# Copiar plantilla
cp .env.example .env

# Editar con tus credenciales reales
notepad .env  # Windows
nano .env     # Linux/Mac
```

### 3. Generar claves de seguridad

```python
# Ejecutar en Python para generar claves seguras
import secrets
import string

def generate_secure_key(length=64):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

print("SECRET_KEY=" + generate_secure_key())
print("JWT_SECRET_KEY=" + generate_secure_key())
```

### 4. Generar claves VAPID para PWA

```python
import secrets
import base64

# Generar claves VAPID
private_key = secrets.token_bytes(32)
public_key = secrets.token_bytes(32)

print("VAPID_PRIVATE_KEY=" + base64.urlsafe_b64encode(private_key).decode())
print("VAPID_PUBLIC_KEY=" + base64.urlsafe_b64encode(public_key).decode())
```

## 🧹 Script de Limpieza Automática

Antes de hacer cualquier commit, ejecuta:

```bash
python clean_credentials.py
```

Este script:

- ✅ Crea backup de tu `.env` local
- ✅ Elimina archivos sensibles del directorio
- ✅ Verifica que `.env.example` esté limpio
- ✅ Confirma configuración de `.gitignore`

## 🚀 Flujo de Trabajo Seguro

### Para desarrollar localmente

1. Mantén tu `.env` con credenciales reales
2. Nunca hagas `git add .env`
3. Usa `git status` para verificar qué archivos vas a subir

### Para hacer commits

1. Ejecuta `python clean_credentials.py`
2. Verifica que solo archivos seguros están en staging
3. Haz commit y push normalmente
4. Restaura tu `.env` local: `cp .env.local.backup .env`

### Para colaboradores

1. Clona el repositorio
2. Copia `.env.example` a `.env`
3. Solicita credenciales al administrador del proyecto
4. Nunca compartas credenciales por medios inseguros

## 🔍 Verificación de Seguridad

### Comandos útiles

```bash
# Verificar qué archivos están trackeados
git ls-files | findstr "\.env"

# Verificar estado antes de commit
git status

# Verificar historial de archivos sensibles
git log --all --full-history -- .env .env.backup
```

### Señales de alerta

- GitHub te envía alertas de credenciales
- Archivos `.env` aparecen en `git status`
- Credenciales reales en `.env.example`

## 🆘 En caso de exposición accidental

1. **Inmediatamente:**
   - Revoca todas las API keys expuestas
   - Genera nuevas credenciales
   - Cambia todas las contraseñas

2. **Limpia el historial:**

   ```bash
   # Eliminar archivo del historial (PELIGROSO)
   git filter-branch --force --index-filter \
   "git rm --cached --ignore-unmatch .env" \
   --prune-empty --tag-name-filter cat -- --all
   
   # Forzar push (PELIGROSO)
   git push origin --force --all
   ```

3. **Notifica al equipo:**
   - Informa sobre la exposición
   - Comparte nuevas credenciales de forma segura

## 📞 Contacto

Si tienes dudas sobre seguridad, contacta al administrador del proyecto antes de hacer cualquier cambio.

---

**Recuerda: La seguridad es responsabilidad de todos. Cuando tengas dudas, pregunta antes de actuar.**