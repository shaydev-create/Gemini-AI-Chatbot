from flask import Blueprint

# Importar las rutas para que se registren en el blueprint
from . import routes as routes

main = Blueprint("main", __name__)
