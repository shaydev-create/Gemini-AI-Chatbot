# 🚀 Chrome Built-in AI - Guía de Configuración

## 🔧 **Paso 1: Habilitar Chrome Flags Experimentales**

### **Abrir Chrome Flags:**
1. Abre Chrome y navega a: `chrome://flags/`
2. Busca y habilita los siguientes flags:

### **🧠 Flags requeridos para Chrome AI APIs (Actualizado 2025):**

```
chrome://flags/#optimization-guide-on-device-model
Estado: Enabled BypassPerfRequirement

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

// 1. Verificar Prompt API (Nuevo namespace estándar)
console.log('Prompt API:', window.ai && window.ai.languageModel);

// 2. Verificar Summarizer API  
console.log('Summarizer API:', window.ai && window.ai.summarizer);

// 3. Verificar Writer API
console.log('Writer API:', window.ai && window.ai.writer);

// 4. Verificar Rewriter API
console.log('Rewriter API:', window.ai && window.ai.rewriter);

// 5. Verificar Translator API
console.log('Translator API:', window.ai && window.ai.translator);

// 6. Verificar Language Detection
console.log('Language Detection:', window.ai && window.ai.languageDetector);
```

**Resultado esperado:** Objetos definidos para todas las APIs.

---

## 📱 **Paso 3: Verificar versión de Chrome**

### **Requisitos mínimos:**
- **Chrome Canary**: Versión 128+ (recomendado para Hackathon)
- **Chrome Dev**: Versión 127+  

### **Verificar tu versión:**
1. Ir a: `chrome://settings/help`

---

## 🧪 **Paso 4: Instalar modelo Gemini Nano (si no está)**

### **Descargar modelo automáticamente:**

```javascript
// Ejecutar en DevTools para forzar descarga:
await window.ai.languageModel.create({
    monitor(m) {
        m.addEventListener('downloadprogress', (e) => {
            console.log(`Descargando: ${Math.round((e.loaded / e.total) * 100)}%`);
        });
    }
});
```

### **O manualmente:**
1. Ir a: `chrome://components/`
2. Buscar: "Optimization Guide On Device Model"
3. Click "Check for update" si está disponible. Si dice "Component not updated", intenta forzar la descarga desde la consola como se muestra arriba.

---

## ✅ **Paso 5: Probar implementación básica**

### **Código de prueba en DevTools:**

```javascript
// Test básico de Prompt API
async function testChromeAI() {
  try {
    const session = await window.ai.languageModel.create({
        systemPrompt: "You are a helpful assistant."
    });
    const response = await session.prompt("Hello Chrome AI!");
    console.log('Prompt API works:', response);
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