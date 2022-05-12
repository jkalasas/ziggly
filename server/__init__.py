import os
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()

def configure_logging(app: Flask) -> None:
    """
    Initialize file logging
    """
    import logging
    from flask.logging import default_handler
    from logging.handlers import RotatingFileHandler
    app.logger.removeHandler(default_handler)
    file_handler = RotatingFileHandler('flaskserver.log', maxBytes=16384, backupCount=20)

    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(filename)s: %(lineno)d]')
    file_handler.setFormatter(file_formatter)

    app.logger.addHandler(file_handler)

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(os.getenv('CONFIG_TYPE', 'config.DevelopmentConfig'))
    configure_logging(app)
    init_db(app)
    init_plugins(app)
    register_error_handlers(app)
    register_blueprints(app)
    return app

def init_db(app: Flask) -> None:
    """
    Bind database modules to the Flask application
    """
    from . import models
    db.init_app(app)
    migrate.init_app(app, db)

def init_plugins(app: Flask) -> None:
    from .plugins.flask_session import Session
    from .plugins.csrf import CSRFProtect
    app.config['SESSION_SQLALCHEMY'] = db
    Session(app)
    CSRFProtect(app)

def register_blueprints(app: Flask) -> None:
    """
    Bind blueprints to its respected paths
    """
    from .api import bp as api_bp
    from .main import bp as main_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api/v1')

def register_error_handlers(app: Flask) -> None:
    """
    Initialize global error handlers
    """
    pass