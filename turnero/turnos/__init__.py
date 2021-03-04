from flask import Blueprint
from flask_restx import Api

turnos = Blueprint("turnos", __name__)

# Init Api (flask_restx)
authorizations = {
    "apikey": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "description": "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token",
    }
}
api_turnos = Api(turnos, doc="/doc", authorizations=authorizations)

from . import views
