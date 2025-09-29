# Pruebas End-to-End para Chat Gemini

Este directorio contiene scripts de prueba para verificar la funcionalidad de la interfaz de chat de Gemini AI.

## Estructura de Pruebas

Las pruebas están organizadas en tres categorías principales:

1. **Funcionalidad Principal** (`test_chat_core_functionality.js`)
   - Verifica elementos DOM esenciales
   - Prueba el fondo de partículas
   - Valida la funcionalidad de entrada de texto
   - Comprueba el envío y recepción de mensajes
   - Evalúa el diseño responsive
   - Verifica accesibilidad básica

2. **Escenarios de Error** (`test_chat_error_scenarios.js`)
   - Simula errores de red
   - Prueba timeouts de respuesta
   - Verifica recuperación de errores de JavaScript
   - Comprueba recuperación de manipulación del DOM
   - Evalúa manejo de problemas de memoria

3. **Fondo de Partículas** (`test_particles_background.js`)
   - Verifica inicialización correcta
   - Mide rendimiento (FPS y uso de memoria)
   - Prueba interactividad con el mouse
   - Comprueba redimensionamiento

## Cómo Ejecutar las Pruebas

Las pruebas se pueden ejecutar de dos formas:

### 1. Desde la Interfaz de Usuario (Recomendado)

Cuando se accede a la página de chat en modo desarrollo (localhost), aparecerá un botón de pruebas (🧪) en la esquina inferior derecha de la pantalla. Al hacer clic en este botón, se abrirá un panel con opciones para ejecutar todas las pruebas o suites específicas.

### 2. Desde la Consola del Navegador

También se pueden ejecutar las pruebas manualmente desde la consola del navegador:

```javascript
// Ejecutar todas las pruebas
runAllTests();

// Ejecutar una suite específica
runTestSuite('Funcionalidad principal');
runTestSuite('Escenarios de error');
runTestSuite('Fondo de partículas');

// Ejecutar una prueba específica
runSpecificTest('domElements');
runSpecificParticlesTest('performance');
testSpecificErrorScenario('network');
```

## Interpretación de Resultados

Los resultados de las pruebas se muestran en un panel en la interfaz y en la consola del navegador. Cada prueba puede tener uno de estos estados:

- ✅ **PASÓ**: La funcionalidad funciona correctamente
- ❌ **FALLÓ**: Se detectaron problemas que requieren atención

Además, se proporciona una tasa de éxito general y detalles específicos para cada prueba.

## Exportación de Resultados

Los resultados de las pruebas se pueden exportar a un archivo JSON para su análisis posterior utilizando el botón "Exportar resultados" en el panel de informe.

## Solución de Problemas Comunes

### Los scripts de prueba no se cargan

Verifica que:
1. Estás accediendo a la página en modo desarrollo (localhost)
2. La estructura de directorios es correcta
3. No hay errores de JavaScript en la consola

### Las pruebas fallan inesperadamente

1. Verifica la conexión a Internet para las pruebas de API
2. Comprueba si hay conflictos con extensiones del navegador
3. Intenta ejecutar en modo incógnito

## Desarrollo de Nuevas Pruebas

Para añadir nuevas pruebas:

1. Crea un nuevo archivo de prueba en el directorio `tests/e2e/`
2. Sigue el patrón de los archivos existentes
3. Actualiza `run_all_tests.js` para incluir tu nueva suite de pruebas

## Mantenimiento

Estas pruebas deben actualizarse cuando:

1. Se añaden nuevas funcionalidades a la interfaz de chat
2. Se modifican componentes existentes
3. Se cambian las expectativas de rendimiento

---

**Nota**: Estas pruebas están diseñadas para ejecutarse en un entorno de desarrollo y pueden no ser adecuadas para producción sin modificaciones adicionales.