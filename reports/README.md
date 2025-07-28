# 📊 Reportes de Seguridad - Gemini AI Chatbot

## Propósito

Esta carpeta contiene los reportes generados por las herramientas de seguridad del proyecto. Estos reportes ayudan a identificar y resolver problemas de seguridad, especialmente relacionados con la exposición de credenciales.

## Tipos de Reportes

### Análisis de Credenciales

Los reportes de análisis de credenciales (`credential_scan_*.txt`) son generados por el script `check_exposed_credentials.py` y contienen información sobre posibles credenciales expuestas en el historial de Git.

## Importante

- Los reportes pueden contener información sensible y no deben ser compartidos públicamente
- Esta carpeta está configurada en `.gitignore` para evitar que los reportes se suban a GitHub
- Revisa regularmente los reportes para mantener la seguridad del proyecto

## Uso

Para generar un nuevo reporte de análisis de credenciales:

```bash
python scripts/check_exposed_credentials.py
```

El reporte se guardará en esta carpeta con un nombre que incluye la fecha y hora de generación.

---

**🚀 Gemini AI Futuristic Chatbot** - Desarrollado con ❤️ por [shaydev-create](https://github.com/shaydev-create)