import os

base_dir = os.path.dirname(os.path.abspath(__file__))


class BaseConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = "hello"


class TestConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
        base_dir, "oa.sqlite"
    )
    debug = True
    JSON_AS_ASCII = False


class workConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
        base_dir, "oa_work.sqlite"
    )
    debug = False

