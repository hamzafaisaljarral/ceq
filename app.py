import os
from flask import Flask
from ceq_user import init_app as init_ceq_app
from flask_jwt_extended import JWTManager
from ceq_user.database.db import initialize_db as initialize_db_ceq
from flask_cors import CORS

UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/ceq_main/static/consumer/')  # Default path

app = Flask(__name__)
def create_app():
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['JWT_SECRET_KEY'] = 'aSuperSecretKey'
    app.config['MONGODB_SETTINGS'] = 'mongodb://localhost:27017/'
    app.config['CEQ_DB_NAME'] = 'ceq'
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
    app.config['UPLOAD_FOLDER'] = '/ceq_main'
    # Initialize JWT, database, and CORS
    jwt = JWTManager(app)
    init_ceq_app(app)
    initialize_db_ceq(app)
    cors = CORS(app, resources={r'/*': {'origins': '*'}})
    # Debugging: Print out UPLOAD_FOLDER and check if it exists
    return app
create_app()


if __name__ == '__main__':
    app.run(debug=True)
