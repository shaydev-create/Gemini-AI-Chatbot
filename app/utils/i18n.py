"""
Utilidad para cargar traducciones y seleccionar idioma en Gemini AI Chatbot.
"""
import json
from pathlib import Path
from flask import session, request

I18N_PATH = Path(__file__).parent.parent / "i18n"
DEFAULT_LANG = "es"

_cache = {}

def get_locale():
    lang = request.args.get("lang") or session.get("lang") or DEFAULT_LANG
    if lang not in ("es", "en"):
        lang = DEFAULT_LANG
    session["lang"] = lang
    return lang

def translate(key):
    lang = get_locale()
    if lang not in _cache:
        try:
            with open(I18N_PATH / f"{lang}.json", encoding="utf-8") as f:
                _cache[lang] = json.load(f)
        except Exception:
            _cache[lang] = {}
    return _cache[lang].get(key, key)
