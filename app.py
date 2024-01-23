import os
from flask import Flask
from ceq_user import init_app as init_ceq_app
from flask_jwt_extended import JWTManager
from ceq_user.database.db import initialize_db as initialize_db_ceq


def create_app():
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = 'aSuperSecretKey'
    app.config['MONGODB_SETTINGS'] = 'mongodb://localhost:27017/'
    app.config['CEQ_DB_NAME'] = 'ceq'
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']

    jwt = JWTManager(app)

    init_ceq_app(app)

    initialize_db_ceq(app)

    return app
