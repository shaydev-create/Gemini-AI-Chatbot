# 🚀 Guía de Contribución - Gemini AI Chatbot

¡Gracias por tu interés en contribuir al proyecto Gemini AI Chatbot! Esta guía te ayudará a empezar.

## 📋 Tabla de Contenidos

- [🤝 Cómo Contribuir](#cómo-contribuir)
- [🐛 Reportar Bugs](#reportar-bugs)
- [💡 Sugerir Funcionalidades](#sugerir-funcionalidades)
- [🔧 Configuración de Desarrollo](#configuración-de-desarrollo)
- [📝 Estándares de Código](#estándares-de-código)
- [🧪 Testing](#testing)
- [📖 Documentación](#documentación)

## 🤝 Cómo Contribuir

### 1. Fork del Repositorio
```bash
# Fork en GitHub y luego clona tu fork
git clone https://github.com/tu-usuario/gemini-ai-chatbot.git
cd gemini-ai-chatbot
```

### 2. Configurar Upstream
```bash
git remote add upstream https://github.com/original-usuario/gemini-ai-chatbot.git
```

### 3. Crear Rama de Feature
```bash
git checkout -b feature/nombre-descriptivo
# o
git checkout -b bugfix/descripcion-del-bug
```

### 4. Realizar Cambios
- Sigue los estándares de código
- Añade tests para nuevas funcionalidades
- Actualiza documentación si es necesario

### 5. Commit y Push
```bash
git add .
git commit -m "feat: descripción clara del cambio"
git push origin feature/nombre-descriptivo
```

### 6. Crear Pull Request
- Ve a GitHub y crea un Pull Request
- Describe claramente los cambios realizados
- Referencia issues relacionados

## 🐛 Reportar Bugs

### Antes de Reportar
- Busca en issues existentes
- Verifica que sea reproducible
- Prueba con la última versión

### Template de Bug Report
```markdown
**Descripción del Bug**
Descripción clara y concisa del problema.

**Pasos para Reproducir**
1. Ve a '...'
2. Haz clic en '....'
3. Desplázate hacia '....'
4. Ve el error

**Comportamiento Esperado**
Descripción clara de lo que esperabas que pasara.

**Screenshots**
Si aplica, añade screenshots para explicar el problema.

**Información del Sistema:**
- OS: [e.g. Windows 10, macOS 12.0, Ubuntu 20.04]
- Navegador: [e.g. Chrome 96, Firefox 94]
- Versión Python: [e.g. 3.9.7]
- Versión de la App: [e.g. 1.0.0]

**Contexto Adicional**
Cualquier otra información relevante sobre el problema.
```

## 💡 Sugerir Funcionalidades

### Template de Feature Request
```markdown
**¿Tu feature request está relacionado con un problema?**
Descripción clara y concisa del problema. Ej. Siempre me frustra cuando [...]

**Describe la solución que te gustaría**
Descripción clara y concisa de lo que quieres que pase.

**Describe alternativas que hayas considerado**
Descripción clara y concisa de cualquier solución o feature alternativa.

**Contexto adicional**
Cualquier otro contexto o screenshots sobre el feature request.
```

## 🔧 Configuración de Desarrollo

### 1. Entorno Virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

### 2. Instalar Dependencias
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Dependencias de desarrollo
```

### 3. Configurar Pre-commit Hooks
```bash
pre-commit install
```

### 4. Variables de Entorno
```bash
cp .env.example .env.development
# Editar .env.development con configuraciones de desarrollo
```

### 5. Base de Datos de Desarrollo
```bash
python -c "from app import app; from src.models import init_db; init_db(app)"
```

## 📝 Estándares de Código

### Python (PEP 8)
- Usar 4 espacios para indentación
- Líneas máximo 88 caracteres (Black formatter)
- Nombres de variables en snake_case
- Nombres de clases en PascalCase
- Docstrings para funciones y clases

### JavaScript
- Usar 2 espacios para indentación
- Usar const/let en lugar de var
- Nombres de variables en camelCase
- Usar comillas simples para strings

### HTML/CSS
- Usar 2 espacios para indentación
- Nombres de clases en kebab-case
- Usar HTML5 semántico
- CSS organizado por componentes

### Commits
Usar [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: añadir nueva funcionalidad de chat
fix: corregir bug en autenticación
docs: actualizar README
style: formatear código con black
refactor: reorganizar estructura de archivos
test: añadir tests para API
chore: actualizar dependencias
```

## 🧪 Testing

### Ejecutar Tests
```bash
# Todos los tests
python -m pytest

# Tests específicos
python -m pytest tests/test_auth.py

# Con cobertura
python -m pytest --cov=src --cov-report=html
```

### Escribir Tests
- Un test por funcionalidad
- Nombres descriptivos
- Usar fixtures para setup
- Mockear dependencias externas

### Ejemplo de Test
```python
def test_user_registration_success():
    """Test successful user registration."""
    response = client.post('/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'securepassword123'
    })
    assert response.status_code == 201
    assert 'user_id' in response.json
```

## 📖 Documentación

### Docstrings
```python
def process_message(message: str, user_id: int) -> dict:
    """
    Procesa un mensaje del usuario y genera respuesta de IA.
    
    Args:
        message (str): Mensaje del usuario
        user_id (int): ID del usuario
        
    Returns:
        dict: Respuesta procesada con metadata
        
    Raises:
        ValidationError: Si el mensaje es inválido
        APIError: Si hay error en la API de Gemini
    """
    pass
```

### Comentarios
- Explicar el "por qué", no el "qué"
- Usar comentarios para lógica compleja
- Mantener comentarios actualizados

## 🏷️ Labels de Issues

- `bug` - Algo no funciona
- `enhancement` - Nueva funcionalidad
- `documentation` - Mejoras en documentación
- `good first issue` - Bueno para principiantes
- `help wanted` - Se necesita ayuda extra
- `question` - Pregunta o discusión
- `wontfix` - No se va a arreglar

## 🎯 Roadmap de Contribuciones

### Prioridad Alta
- [ ] Mejorar tests de cobertura
- [ ] Optimizar performance de chat
- [ ] Añadir soporte para más idiomas

### Prioridad Media
- [ ] Implementar modo offline
- [ ] Añadir temas personalizables
- [ ] Mejorar accesibilidad

### Prioridad Baja
- [ ] Integración con más APIs de IA
- [ ] Modo colaborativo
- [ ] Plugins de terceros

## 📞 Contacto

- 💬 **Discusiones**: [GitHub Discussions](https://github.com/usuario/gemini-ai-chatbot/discussions)
- 📧 **Email**: contribuciones@gemini-chatbot.com
- 💬 **Discord**: [Servidor de la Comunidad](https://discord.gg/gemini-chatbot)

## 🙏 Reconocimientos

Todos los contribuidores serán reconocidos en:
- README principal
- Página de créditos en la aplicación
- Release notes

¡Gracias por hacer que Gemini AI Chatbot sea mejor! 🚀