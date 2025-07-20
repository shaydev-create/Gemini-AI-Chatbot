#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Archivo __init__.py para el directorio src.
Compatibilidad con estructura de archivos esperada.
"""

# Importaciones principales
from app.core.application import create_app
from app.main import app

__all__ = ['create_app', 'app']