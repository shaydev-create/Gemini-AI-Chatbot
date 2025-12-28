# GitHub Copilot Instructions for Chrome AI Hackathon Project

## Project Overview

This is a **Chrome Built-in AI Hackathon 2025** submission featuring a Flask web application with comprehensive integration of all 6 Chrome Built-in AI APIs. The project combines server-side Google Gemini AI with client-side Chrome AI for a hybrid intelligence experience.

## Core Architecture

### Technology Stack
- **Backend**: Flask 3.0+ with Blueprint architecture
- **Frontend**: Modern HTML5/CSS3/JavaScript with futuristic UI
- **AI Integration**: Dual-mode (Chrome Built-in AI + Google Gemini)
- **Package Management**: Poetry with pyproject.toml
- **Containerization**: Docker with multi-environment support
- **Testing**: pytest with 71% coverage
- **Quality**: ruff, black, mypy, bandit

### Key File Structure
```
app/
├── core/application.py        # Flask app factory with blueprint registration
├── services/gemini_service.py # Google Gemini AI integration with multimodal support
├── templates/chat.html        # 5877-line comprehensive Chrome AI interface
├── static/js/chrome-ai-manager.js # Chrome Built-in AI APIs manager
├── main/routes.py            # Main Flask routes with chat endpoints
└── api/routes.py             # REST API endpoints

chrome_extension/
├── manifest.json             # Chrome Extension v3 manifest
├── popup.html/popup.js       # Extension popup with localhost:3000 redirect
└── content.js               # Content script for web page integration

pyproject.toml               # Poetry configuration with dependencies
run.py                      # Main launcher with Docker detection
```

## Chrome Built-in AI Integration

### 6 APIs Implemented
1. **Prompt API** (LanguageModel) - Primary conversational AI
2. **Summarizer API** - Text summarization
3. **Writer API** - Content generation
4. **Rewriter API** - Text improvement
5. **Translator API** - Language translation
6. **Proofreader API** - Grammar and style correction

### Critical Implementation Details
- Chrome AI requires user gesture activation (no auto-initialization)
- Located in `app/static/js/chrome-ai-manager.js` (705 lines)
- Fallback system: Chrome AI → Google Gemini API
- Session management with caching for performance
- Full offline capability when Chrome AI is available

## Development Patterns

### Flask Application Factory
```python
# app/core/application.py
def get_flask_app(env: str = "development") -> Flask:
    app = Flask(__name__)
    # Blueprint registration pattern
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
```

### Environment Configuration
- Development: localhost:3000 with auto-reload
- Production: Gunicorn with SSL support
- Docker: Multi-stage builds with health checks
- Environment detection in `run.py` with automatic service management

### Testing Strategy
- Unit tests: `tests/unit/` - Component isolation
- Integration tests: `tests/integration/` - API endpoints
- E2E tests: `tests/e2e/` - Full user workflows
- Mock pattern for Gemini API to avoid API costs

## Chrome Extension Architecture

### Manifest V3 Implementation
```json
{
  "manifest_version": 3,
  "name": "Chrome AI Assistant",
  "version": "2.0.2",
  "permissions": ["activeTab"],
  "host_permissions": ["http://localhost:3000/*"]
}
```

### Popup Strategy
Extension popup redirects to localhost:3000 for full functionality due to Chrome extension popup limitations. This design pattern ensures access to all Chrome Built-in AI APIs and complete UI.

## Critical Development Guidelines

### Chrome AI API Patterns
```javascript
// Always check availability first
const availability = await LanguageModel.availability();
if (availability !== 'unavailable') {
    // Require user gesture for initialization
    const session = await LanguageModel.create();
}
```

### Error Handling
- Chrome AI availability checks with graceful fallbacks
- Comprehensive logging with emoji indicators for status
- User-friendly notifications for API state changes

### Code Quality Standards
- **Linting**: `ruff check .` - Modern Python linter
- **Formatting**: `ruff format .` - Fast code formatter
- **Type Checking**: `mypy .` - Static type analysis
- **Security**: `bandit -r .` - Security vulnerability scanner

## Task Configuration

### VS Code Tasks (.vscode/tasks.json)
- **Run Flask Development Server**: `python run_development.py`
- **Run Tests**: `pytest -v --cov=src --cov=app`
- **Lint Code**: `ruff check .`
- **Format Code**: `ruff format .`
- **Type Check**: `mypy .`
- **Security Check**: `bandit -r .`

### Poetry Commands
```bash
poetry install              # Install dependencies
poetry run python run.py   # Run application
poetry run pytest          # Run tests
poetry shell               # Activate virtual environment
```

## Deployment Considerations

### Docker Strategy
- Multi-stage builds for optimization
- Health checks for service reliability
- Environment-specific compose files
- SSL certificate management

### Chrome Web Store
- Extension submitted as v2.0.2
- Privacy policy required for AI functionality
- Screenshots demonstrate Chrome AI integration
- Detailed store description with hackathon context

## AI-Specific Development Notes

### Gemini Service Configuration
- Supports multimodal input (text + images)
- Temperature: 0.7, max_output_tokens: 2048
- Language detection and response localization
- Error recovery with detailed logging

### Chrome AI Session Management
- Lazy initialization to avoid startup delays
- Response caching for improved performance
- Capability detection for feature availability
- User preference storage for AI mode selection

### Security Implementation
- API key management through environment variables
- CSRF protection for all forms
- Input validation and sanitization
- Rate limiting for API endpoints

## Common Development Tasks

### Adding New AI Features
1. Update `chrome-ai-manager.js` for new Chrome AI capabilities
2. Add corresponding backend endpoints in `app/api/routes.py`
3. Update UI components in `chat.html`
4. Add tests in appropriate test directories
5. Update documentation

### Debugging Chrome AI Issues
- Check browser console for API availability messages
- Verify user gesture requirements are met
- Test fallback to Gemini API when Chrome AI unavailable
- Use emoji-coded logging for quick status identification

### Performance Optimization
- Monitor Chrome AI session initialization time
- Implement response caching where appropriate
- Use lazy loading for heavy UI components
- Profile API response times for bottleneck identification

## Hackathon-Specific Context

This project was developed for **Chrome AI Hackathon 2025** with focus on:
- Complete integration of all 6 Chrome Built-in AI APIs
- Innovative hybrid AI approach (local + cloud)
- Professional UI/UX with futuristic design
- Real-world deployment readiness
- Comprehensive testing and documentation

The submission demonstrates practical implementation of Chrome's experimental AI APIs in a production-ready application architecture.