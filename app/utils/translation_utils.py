import json
import os
from typing import Any

from flask import current_app


# Cargar traducciones desde un archivo JSON
def load_translations(lang) -> None:
    """Carga los archivos de traducción para un idioma específico."""
    path = os.path.join(os.path.dirname(__file__), "..", "i18n", f"{lang}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def translate(key) -> None:
    """
    Traduce una clave dada al idioma actual de la aplicación.
    """
    # 'g' es el objeto de contexto global de Flask. Usamos 'es' como predeterminado.
    lang = getattr(current_app, "language", "es")

    if not hasattr(current_app, "translations"):
        current_app.translations = {}

    if lang not in current_app.translations:
        current_app.translations[lang] = load_translations(lang)

    return current_app.translations[lang].get(key, key)


def register_translation_functions(app) -> None:
    """
    Registra la función de traducción en el contexto de la plantilla Jinja2.
    """

    @app.context_processor
    def inject_translate() -> dict[str, Any]:
        return {"translate": translate}
