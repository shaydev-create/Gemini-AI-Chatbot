from flask import Blueprint

__all__ = ['main', 'routes']

main = Blueprint("main", __name__)

# Import routes after blueprint definition to avoid circular import
from . import routes  # noqa: E402, F401
