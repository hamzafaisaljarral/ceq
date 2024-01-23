from mongoengine import connect,disconnect


def initialize_db(app):
    if app.config.get('MONGODB_SETTINGS'):
        disconnect(alias='default')
        print(app.config['CEQ_DB_NAME'])
        connect(db=app.config['CEQ_DB_NAME'], host=app.config['MONGODB_SETTINGS'], alias='default')