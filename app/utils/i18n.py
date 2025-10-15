from typing import Any, Optional
"""
Utilidad para cargar traducciones y seleccionar idioma en Gemini AI Chatbot.
"""

import json
import logging
from pathlib import Path
from typing import Dict

from flask import request, session

logger=logging.getLogger(__name__)

# Constantes
I18N_DIR = Path(__file__).parent.parent / "i18n"
DEFAULT_LANG = "es"
SUPPORTED_LANGS = ["es", "en"]

# Caché en memoria para las traducciones
_translations_cache: Dict[str, Dict[str, str]] = {}


def get_locale() -> Any:
    """
    Determina el idioma a utilizar para la solicitud actual.
    El orden de precedencia es:
    1. Parámetro 'lang' en la URL.
    2. Valor 'lang' en la sesión del usuario.
    3. Idioma por defecto ('es').
    """
    # Intenta obtener el idioma desde los argumentos de la solicitud o la sesión
    lang=request.args.get("lang") or session.get("lang")

    if lang and lang in SUPPORTED_LANGS:
        # Si el idioma está soportado, lo usamos y lo guardamos en la sesión
        if session.get("lang") != lang:
            session["lang"] = lang
        return lang

    # Si no hay idioma o no está soportado, usamos el idioma por defecto
    if "lang" not in session:
        session["lang"] = DEFAULT_LANG

    return session.get("lang", DEFAULT_LANG)


def _load_translations(lang: str) -> Dict[str, str]:
    """
    Carga el archivo de traducción para un idioma específico en la caché.
    """
    if lang not in _translations_cache:
        lang_file=I18N_DIR / f"{lang}.json"
        try:
            with open(lang_file, "r", encoding="utf-8") as f:
                _translations_cache[lang] = json.load(f)
                logger.info("Traducciones para '%s' cargadas en caché.", lang)
        except (FileNotFoundError, json.JSONDecodeError):
            logger.exception(
                "No se pudo cargar o parsear el archivo de traducción para '%s'.", lang
            )
            _translations_cache[
                lang
            ] = {}  # Guardar un diccionario vacío para evitar reintentos

    return _translations_cache[lang]


def translate(key: str, **kwargs) -> Any:
    """
    Traduce una clave al idioma actual y formatea la cadena con los argumentos proporcionados.
    Si la clave no se encuentra, devuelve la propia clave.
    """
    lang=get_locale()
    translations=_load_translations(lang)

    translated_string=translations.get(key, key)

    # Si se proporcionan argumentos, intenta formatear la cadena
    if kwargs:
        try:
            return translated_string.format(**kwargs)
        except (KeyError, IndexError):
            logger.warning(
                "Error al formatear la clave de traducción '%s' para el idioma '%s'. "
                "Asegúrese de que los placeholders coincidan.",
                key,
                lang,
            )
            return key  # Devolver la clave original si el formato falla

    return translated_string