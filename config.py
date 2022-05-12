import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    FLASK_ENV = 'development'
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'MEOWMEOW')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SESSION_TYPE = 'sqlalchemy'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, 'dev.db')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, 'test.db')

class ProductionConfig(Config):
    FLASK_ENV = 'production'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI') or "sqlite:///" + os.path.join(basedir, 'prod.db')