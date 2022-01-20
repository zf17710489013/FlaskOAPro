from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from settings import TestConfig
from flask_wtf import CSRFProtect
from flask_restful import Api

db = SQLAlchemy() #实例化sqlalchemy
csrf = CSRFProtect() #实例化csrf

api = Api()


def make_app(config = TestConfig):

    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    csrf.init_app(app)
    api.init_app(app)

    from FlaskOAPro.OAPro import OAPrint
    app.register_blueprint(OAPrint)

    return app
