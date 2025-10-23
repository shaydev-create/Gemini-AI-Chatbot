# 🚀 Chrome Built-in AI - Guía de Configuración

## 🔧 **Paso 1: Habilitar Chrome Flags Experimentales**

### **Abrir Chrome Flags:**
1. Abre Chrome y navega a: `chrome://flags/`
2. Busca y habilita los siguientes flags:

### **🧠 Flags requeridos para Chrome AI APIs:**

```
chrome://flags/#optimization-guide-on-device-model
Estado: Enabled

chrome://flags/#prompt-api-for-gemini-nano  
Estado: Enabled

chrome://flags/#summarization-api-for-gemini-nano
Estado: Enabled

chrome://flags/#writer-api-for-gemini-nano
Estado: Enabled

chrome://flags/#rewriter-api-for-gemini-nano
Estado: Enabled

chrome://flags/#translation-api
Estado: Enabled

chrome://flags/#language-detection-api
Estado: Enabled
```

### **⚠️ IMPORTANTE:**
Después de habilitar los flags, **REINICIA Chrome completamente**.

---

## 🔄 **Paso 2: Verificar disponibilidad de APIs**

### **Abrir DevTools y verificar:**

```javascript
// En la consola de Chrome (F12):

// 1. Verificar Prompt API
console.log('Prompt API:', 'ai' in window && 'languageModel' in window.ai);

// 2. Verificar Summarizer API  
console.log('Summarizer API:', 'ai' in window && 'summarizer' in window.ai);

// 3. Verificar Writer API
console.log('Writer API:', 'ai' in window && 'writer' in window.ai);

// 4. Verificar Rewriter API
console.log('Rewriter API:', 'ai' in window && 'rewriter' in window.ai);

// 5. Verificar Translator API
console.log('Translator API:', 'translation' in window);

// 6. Verificar Language Detection
console.log('Language Detection:', 'translation' in window && 'languageDetector' in window.translation);
```

**Resultado esperado:** `true` para todas las APIs

---

## 📱 **Paso 3: Verificar versión de Chrome**

### **Requisitos mínimos:**
- **Chrome Canary**: Versión 127+ (recomendado)
- **Chrome Dev**: Versión 126+  
- **Chrome Beta**: Versión 125+
- **Chrome Stable**: Puede no estar disponible aún

### **Verificar tu versión:**
1. Ir a: `chrome://settings/help`
2. Debe mostrar Chrome 125+ para soporte completo

---

## 🧪 **Paso 4: Instalar modelo Gemini Nano (si no está)**

### **Descargar modelo automáticamente:**

```javascript
// Ejecutar en DevTools para forzar descarga:
await window.ai.languageModel.create();
```

### **O manualmente:**
1. Ir a: `chrome://components/`
2. Buscar: "Optimization Guide On Device Model"
3. Click "Check for update" si está disponible

---

## ✅ **Paso 5: Probar implementación básica**

### **Código de prueba en DevTools:**

```javascript
// Test básico de todas las APIs
async function testChromeAI() {
  try {
    // 1. Prompt API
    const session = await window.ai.languageModel.create();
    const response = await session.prompt("Hello Chrome AI!");
    console.log('Prompt API works:', response);
    
    // 2. Summarizer API
    const summarizer = await window.ai.summarizer.create();
    const summary = await summarizer.summarize("This is a long text to summarize...");
    console.log('Summarizer works:', summary);
    
    // 3. Writer API
    const writer = await window.ai.writer.create();
    const written = await writer.write("Write a short email");
    console.log('Writer works:', written);
    
    // 4. Rewriter API  
    const rewriter = await window.ai.rewriter.create();
    const rewritten = await rewriter.rewrite("Make this formal", {tone: "formal"});
    console.log('Rewriter works:', rewritten);
    
    // 5. Translator API
    const translator = await window.translation.createTranslator({
      sourceLanguage: 'en',
      targetLanguage: 'es'
    });
    const translated = await translator.translate("Hello world");
    console.log('Translator works:', translated);
    
  } catch (error) {
    console.error('Chrome AI Error:', error);
  }
}

// Ejecutar test
testChromeAI();
```

---

## 🔧 **Troubleshooting Común**

### **Si las APIs no están disponibles:**

1. **Verificar flags**: Todos habilitados y Chrome reiniciado
2. **Verificar versión**: Chrome 125+ mínimo  
3. **Verificar región**: Algunas APIs pueden estar geo-restringidas
4. **Intentar Chrome Canary**: Versión más reciente con todas las features

### **Si el modelo no se descarga:**
1. Conexión a internet estable requerida
2. Espacio en disco (modelo ~3GB)
3. Reintentar después de reiniciar Chrome

---

## 🎯 **Para el Hackathon**

### **Requisitos completados:**
- ✅ Todas las 6 Chrome Built-in AI APIs funcionando
- ✅ Implementación híbrida (Chrome AI + Gemini API)
- ✅ Fallback automático cuando Chrome AI no disponible

### **Testing antes del submission:**
- Probar en Chrome limpio
- Verificar en diferentes sistemas
- Documentar requisitos de instalación

---

**🚀 Una vez completado este setup, podrás implementar las 3 APIs faltantes en tu aplicación!**