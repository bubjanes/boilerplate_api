from flask_restx import Resource, fields, abort
from flask import Flask, jsonify, request, current_app
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
)
import bcrypt

from . import api_auth

auth_user_model = api_auth.model(
    "AuthUser",
    {
        "username": fields.String(required=True, description="The user name"),
        "password": fields.String(
            required=True, readOnly=True, description="The user password"
        ),
    },
)

users = {
    "": "",
}


@api_auth.route("/")
class Login(Resource):
    @api_auth.doc(
        "auth_login",
        description="Lets you login and it grant you read and write permissions.",
        responses={
            400: "Missing username parameter / Missing password parameter",
            401: "Bad username or password",
            200: "access_token: <access_token>, refresh_token: <refresh_token>",
        },
    )
    @api_auth.expect(auth_user_model)
    def post(self):
        """
        Login with username and password
        """
        username = api_auth.payload.get("username")
        password = api_auth.payload.get("password")
        if not username:
            abort(400, "Missing username parameter")
        if not password:
            abort(400, "Missing password parameter")

        # Check password
        if not bcrypt.checkpw(
            password.encode("utf-8"), users.get(username).encode("utf-8")
        ):
            return "Invalid Login Info!", 400

        # Check username
        if username not in users:
            abort(401, "Bad username or password")
        # Create access token (JWT)
        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)

        # current_app.logger.info(f'Check password: {users.get(username)}')

        return {"access_token": access_token, "refresh_token": refresh_token}, 200

    @api_auth.expect(auth_user_model)
    def put(self):
        """
        Register a new password and return a hash for storage.
        """
        try:
            username = api_auth.payload.get("username")
            password = api_auth.payload.get("password")

            if not username:
                return "Missing username", 400
            if not password:
                return "Missing password", 400
            hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            return f"Welcome {username}! Your hashed password: {hashed}", 200
        except AttributeError:
            return (
                "Provide an Username and Password in JSON format in the request body",
                400,
            )
