# 🔍 Guía Visual para Encontrar Chrome AI Flags

## 🎯 Ubicación de los Flags (Actualizado Octubre 2025)

Los nombres de los flags han cambiado recientemente. Aquí están los **nombres actuales**:

### 📋 LISTA ACTUALIZADA DE FLAGS

#### 1. **Flag Principal (OBLIGATORIO)**
```
Buscar: "Prompt API for Gemini Nano"
Nombre exacto: #prompt-api-for-gemini-nano
Estado: Enabled
```

#### 2. **Modelo en Dispositivo (CRÍTICO)**
```
Buscar: "Optimization Guide On Device Model"  
Nombre exacto: #optimization-guide-on-device-model
Estado: Enabled
```

#### 3. **APIs Específicas (OPCIONALES pero RECOMENDADAS)**
```
Buscar: "Summarization API for Gemini Nano"
Nombre exacto: #summarization-api-for-gemini-nano
Estado: Enabled

Buscar: "Rewriter API for Gemini Nano"
Nombre exacto: #rewriter-api-for-gemini-nano  
Estado: Enabled

Buscar: "Composer API for Gemini Nano"
Nombre exacto: #composer-api-for-gemini-nano
Estado: Enabled

Buscar: "Translation API"
Nombre exacto: #translation-api
Estado: Enabled
```

## 🔍 TÉCNICA DE BÚSQUEDA PASO A PASO

### Método 1: Búsqueda por Palabras Clave

1. **Abre Chrome Canary**
2. **Ve a**: `chrome://flags/`
3. **En la caja de búsqueda**, prueba estos términos:

```
🔍 Términos de búsqueda (uno por vez):
• "gemini nano"
• "prompt api" 
• "optimization guide"
• "on device model"
• "summarization api"
• "rewriter api"
• "composer api"
• "translation api"
• "ai assistant"
```

### Método 2: Búsqueda por Secciones

Los flags suelen estar en estas secciones:
- **Experimental Web Platform features**
- **Privacy and security**
- **Performance**
- **Developer tools**

## 📱 SCREENSHOTS DE REFERENCIA

### ✅ Así se ven cuando están CORRECTOS:
```
🟢 Prompt API for Gemini Nano                    [Enabled ▼]
🟢 Optimization Guide On Device Model            [Enabled ▼]  
🟢 Summarization API for Gemini Nano            [Enabled ▼]
🟢 Rewriter API for Gemini Nano                 [Enabled ▼]
🟢 Composer API for Gemini Nano                 [Enabled ▼]
🟢 Translation API                               [Enabled ▼]
```

### ❌ Así se ven cuando están INCORRECTOS:
```
🔴 Prompt API for Gemini Nano                    [Default ▼]
🔴 Optimization Guide On Device Model            [Disabled ▼]
🔴 Summarization API for Gemini Nano            [Default ▼]
```

## 🚨 SI NO ENCUENTRAS LOS FLAGS

### Verificaciones Previas:
1. **¿Tienes Chrome Canary?** (No Chrome regular)
   - Ve a `chrome://version/`
   - Debe decir "Google Chrome Canary" 

2. **¿Versión reciente?**
   - Debe ser versión 120+ 
   - Ve a `chrome://settings/help` para actualizar

3. **¿Sistema compatible?**
   - Windows 10/11 (x64)
   - macOS 12+
   - Linux Ubuntu 20.04+

### Nombres Alternativos (si los nombres cambiaron):

```
Buscar también por:
• "Built-in AI"
• "Web AI"
• "Experimental AI"
• "Machine Learning"
• "On-device AI"
• "Local AI"
• "Gemini"
• "LLM"
```

## 🎯 VERIFICACIÓN RÁPIDA

### Después de habilitar los flags:

1. **Reinicia Chrome Canary** (IMPORTANTE)
2. **Ve a tu aplicación**: `http://127.0.0.1:5000`
3. **Abre DevTools** (F12)
4. **En Console, ejecuta**:
   ```javascript
   console.log('AI disponible:', 'ai' in window);
   console.log('Prompt API:', window.ai?.assistant);
   ```
5. **Debe mostrar**:
   ```
   AI disponible: true
   Prompt API: [object Object]
   ```

## 🔧 SOLUCIÓN A PROBLEMAS COMUNES

### Problema: "Flag no encontrado"
**Solución**: 
- Actualiza Chrome Canary
- Busca con términos más generales
- Usa nombres alternativos

### Problema: "Flag habilitado pero no funciona"
**Solución**:
1. Cierra TODAS las ventanas de Chrome
2. Reinicia Chrome Canary
3. Ve directamente a tu aplicación
4. Espera 2-3 minutos (descarga de modelos)

### Problema: "Dice que descarga modelos pero no termina"
**Solución**:
- Verifica conexión a internet
- Libera al menos 2GB de espacio
- Cierra otras aplicaciones pesadas
- Espera hasta 15 minutos la primera vez

## 📞 ÚLTIMO RECURSO

Si después de todo esto no funciona:

### Opción A: Uso de Parámetros de Línea de Comandos
```bash
# Cierra Chrome Canary completamente
# Ejecuta desde línea de comandos:
chrome.exe --enable-features=AIAssistantAPI,PromptAPIForGeminiNano --enable-ai-assistant-api
```

### Opción B: Usar Modo Híbrido
- En lugar de "🧠 Local"
- Usa "🔄 Híbrido" que combina ambos
- Funciona aunque Chrome AI no esté disponible

### Opción C: Esperar Actualizaciones
- Chrome Built-in AI está en desarrollo activo
- Nuevas versiones salen cada semana
- Los flags pueden cambiar de nombre

## 🎉 ¡ÉXITO!

Cuando todo funcione correctamente verás:
- ✅ Botón "🤖 Chrome AI" visible
- ✅ Opción "🧠 Local" disponible (no dice N/A)
- ✅ Respuestas instantáneas (<1 segundo)
- ✅ Funciona sin internet
- ✅ Notificación: "Chrome Built-in AI disponible"

---

**💡 CONSEJO FINAL**: No te desanimes si no funciona inmediatamente. Chrome Built-in AI es tecnología experimental y puede requerir varios intentos para configurar correctamente.