# Plan de Trabajo: Refactorización y Limpieza (Próxima Sesión)

## Estado Actual (Hito: Gemini 2.0 + PDFs + Memoria)
El proyecto ha alcanzado un nivel de funcionalidad muy alto. El backend es robusto y maneja contexto e historial. El frontend es visualmente atractivo y funcional, pero su estructura interna necesita organización.

## Objetivos para la Próxima Sesión
El objetivo principal será **mejorar la mantenibilidad** sin alterar la funcionalidad visible.

### 1. Refactorización del Frontend (`chat.html`)
El archivo `chat.html` ha crecido demasiado. Debemos dividirlo:

- [ ] **Extraer CSS:** Mover todos los estilos `<style>` a `app/static/css/chat.css`.
- [ ] **Modularizar JavaScript:** Crear archivos JS específicos en `app/static/js/`:
    - `ui.js`: Manejo de partículas, animaciones, scroll, toggles de UI.
    - `api.js`: Funciones `sendMessage`, `uploadFile`, comunicación con el backend.
    - `files.js`: Lógica de Drag & Drop, previsualización de PDFs e Imágenes.
    - `chat.js`: Inicialización y lógica principal.
- [ ] **Limpiar HTML:** Dejar `chat.html` limpio, solo con estructura y referencias a los nuevos archivos.

### 2. Optimización del Backend (`routes.py`)
- [ ] **Limpiar Rutas:** Mover la lógica de construcción de prompts (los strings largos con `f"""..."""`) a una clase `PromptBuilder` en `app/services/`.
- [ ] **Gestión de Sesiones:** Evaluar mover el historial de chat a una base de datos ligera (SQLite) en lugar de pasarlo ida y vuelta al frontend (opcional, para escalabilidad).

### 3. Pruebas
- [ ] Verificar que la carga de PDFs siga funcionando tras mover el JS.
- [ ] Verificar que la memoria de conversación se mantenga.

---
**Nota para el Desarrollador:**
Este proyecto es un éxito. Descansa y vuelve con energía para esta fase de limpieza. ¡El trabajo duro de funcionalidad ya está hecho!
