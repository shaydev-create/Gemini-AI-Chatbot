# Guía de Dependencias: python-magic

## Problema Resuelto

Se ha corregido un error en el flujo de trabajo de CI/CD relacionado con la dependencia `python-magic-bin==0.4.14`, que causaba el siguiente error:

```
ERROR: No se pudo encontrar una versión que satisfaga el requisito python-magic-bin==0.4.14 (de versiones: ninguna)
ERROR: No se encontró una distribución coincidente para python-magic-bin==0.4.14
Error: Proceso completado con el código de salida 1.
```

## Solución Implementada

1. **Eliminación de dependencia problemática**:
   - Se ha eliminado `python-magic-bin==0.4.14` del archivo `requirements.txt`
   - Se mantiene `python-magic==0.4.27` que ya estaba incluido en las dependencias

2. **Actualización del Dockerfile**:
   - Se han añadido las dependencias del sistema necesarias para `python-magic`:
     ```dockerfile
     libmagic1
     libmagic-dev
     ```

## Razones del Cambio

- `python-magic-bin` está diseñado principalmente para Windows y tiene problemas de compatibilidad con versiones recientes de Python
- `python-magic` es multiplataforma y más mantenido, pero requiere la instalación de `libmagic` en sistemas Linux
- Esta solución funciona en todos los entornos (desarrollo local, CI/CD, producción)

## Mejores Prácticas para Dependencias de python-magic

### En Entornos Windows (Desarrollo Local)

Si desarrollas en Windows y necesitas `python-magic`, tienes dos opciones:

1. **Usar python-magic con DLLs manuales**:
   - Instalar `python-magic`
   - Descargar e instalar las DLLs de libmagic manualmente

2. **Usar python-magic-bin solo en desarrollo local**:
   - Añadir `python-magic-bin` a un archivo de requisitos específico para desarrollo en Windows
   - No incluirlo en el `requirements.txt` principal

### En Entornos Linux/Docker (CI/CD, Producción)

1. **Usar python-magic con libmagic**:
   - Instalar `python-magic` vía pip
   - Instalar `libmagic1` y `libmagic-dev` vía apt-get (o el gestor de paquetes correspondiente)

### Configuración Multiplataforma

Para proyectos que necesitan funcionar en múltiples plataformas, considera:

1. **Separar requisitos por plataforma**:
   ```
   requirements/
     base.txt       # Dependencias comunes
     windows.txt    # Específicas para Windows
     linux.txt      # Específicas para Linux
   ```

2. **Detección de plataforma en scripts**:
   ```python
   import platform
   
   if platform.system() == 'Windows':
       # Configuración para Windows
   else:
       # Configuración para Linux/Mac
   ```

## Verificación

Para verificar que la solución funciona correctamente:

1. **En entorno de desarrollo**:
   ```bash
   pip install -r requirements.txt
   python -c "import magic; print(magic.Magic().from_file('requirements.txt'))"
   ```

2. **En Docker**:
   ```bash
   docker build -t gemini-app .
   docker run gemini-app python -c "import magic; print(magic.Magic().from_file('requirements.txt'))"
   ```

Esta configuración debería resolver los problemas con `python-magic` en todos los entornos de ejecución del proyecto.