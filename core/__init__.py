#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Archivo __init__.py para el directorio core.
Compatibilidad con estructura de archivos esperada.
"""

# Importaciones principales del core
from app.core.application import create_app
from app.core.cache import cache_manager
from app.core.metrics import metrics_manager

__all__ = ['create_app', 'cache_manager', 'metrics_manager']