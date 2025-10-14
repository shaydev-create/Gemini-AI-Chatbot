from flask import Blueprint

main = Blueprint("main", __name__)

# Importar las rutas DESPUÉS de crear el blueprint para que se registren correctamente
from . import routes
