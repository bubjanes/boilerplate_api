from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager
import logging

# Init logger

# configure root logger
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s",
)

# Init Flask
app = Flask(__name__)
# CORS(app, origins="*")
# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "barrerarrarra"
jwt = JWTManager(app)

# Load Blueprints
from .turnos import turnos

app.register_blueprint(turnos, url_prefix="/turno")
from .auth import auth

app.register_blueprint(auth, url_prefix="/auth")

# Init Api (flask_restx)
api_app = Api(
    app,
    appversion="1.0",
    title="Google Calendar Turnero API",
    description="API template. "
    + "\nDocs URLs: "
    + " \n1- /turno/doc"
    + " \n2- /auth/doc",
)
