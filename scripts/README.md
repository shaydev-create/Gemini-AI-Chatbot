# 🛠️ Scripts de Utilidad - Gemini AI Chatbot

Esta carpeta contiene scripts de utilidad para ayudar en el desarrollo, configuración y mantenimiento del proyecto Gemini AI Chatbot.

## 🔒 Scripts de Seguridad

### `security_check.py`

**Descripción:** Ejecuta todas las verificaciones de seguridad en un solo comando.

**Uso:**
```bash
python scripts/security_check.py
```

**Funcionalidad:**
- Verifica la configuración de `.gitignore` y `.gitattributes`
- Busca credenciales expuestas en el historial de Git
- Limpia el archivo `.env` de credenciales reales
- Muestra recomendaciones de seguridad

### `secure_env.py`

**Descripción:** Limpia el archivo `.env` de credenciales reales y las reemplaza con placeholders seguros.

**Uso:**
```bash
python scripts/secure_env.py
```

**Funcionalidad:**
- Crea un backup del archivo `.env` actual
- Reemplaza las credenciales reales con placeholders
- Permite hacer commit de forma segura

### `check_exposed_credentials.py`

**Descripción:** Analiza el historial de Git para detectar posibles credenciales expuestas.

**Uso:**
```bash
python scripts/check_exposed_credentials.py
```

**Funcionalidad:**
- Busca patrones de credenciales en el historial de Git
- Genera un reporte de análisis
- Proporciona recomendaciones para limpiar el historial

### `setup_api_keys.py`

**Descripción:** Ayuda a configurar las claves API de forma segura.

**Uso:**
```bash
python scripts/setup_api_keys.py
```

**Funcionalidad:**
- Configura y prueba las claves API de Gemini
- Verifica la validez de las claves
- Actualiza el archivo `.env` de forma segura

## 🔄 Flujo de Trabajo Recomendado

1. **Configuración inicial:**
   ```bash
   python scripts/setup_api_keys.py
   ```

2. **Antes de hacer commit:**
   ```bash
   python scripts/secure_env.py
   ```

3. **Verificación periódica:**
   ```bash
   python scripts/check_exposed_credentials.py
   ```

4. **Verificación completa:**
   ```bash
   python scripts/security_check.py
   ```

## ⚠️ Importante

- Nunca subas credenciales reales a GitHub
- Ejecuta `secure_env.py` antes de hacer commit
- Consulta la guía completa en `docs/SEGURIDAD_CREDENCIALES.md`

---

**🚀 Gemini AI Futuristic Chatbot** - Desarrollado con ❤️ por [shaydev-create](https://github.com/shaydev-create)