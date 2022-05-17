import os
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()

def configure_logging(app: Flask) -> None:
    """Initialize file logging
    Parameters
    ----------
    app: Flask
        the flask application
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
    "Creates the application and binds its necessary dependencies"
    app = Flask(__name__)
    app.config.from_object(os.getenv('CONFIG_TYPE', 'config.DevelopmentConfig'))
    configure_logging(app)
    init_db(app)
    init_plugins(app)
    register_app_events(app)
    register_blueprints(app)
    return app

def init_db(app: Flask) -> None:
    """Bind database modules to the Flask application
    Parameters
    ----------
    app: Flask
        the flask application
    """
    from . import models
    db.init_app(app)
    migrate.init_app(app, db)

def init_plugins(app: Flask) -> None:
    """Initializes and binds the plugins in the flask application
    Parameters
    ----------
    app: Flask
        the flask application
    """
    from .plugins.currency import format_currency
    from .plugins.flask_session import Session
    from .plugins.csrf import CSRFProtect
    from .plugins.momentjs import momentjs
    app.config['SESSION_SQLALCHEMY'] = db
    app.jinja_env.globals['momentjs'] = momentjs
    app.jinja_env.globals['format_currency'] = format_currency
    Session(app)
    CSRFProtect(app)

def register_blueprints(app: Flask) -> None:
    """Bind blueprints to its respected paths
    Parameters
    ----------
    app: Flask
        the flask application
    """
    from .api import bp as api_bp
    from .main import bp as main_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api/v1')

def register_app_events(app: Flask) -> None:
    """Initialize global app events
    Parameters
    ----------
    app: Flask
        the flask application
    """
    from .models import User
    @app.before_first_request
    def initialize_default_user(*args, **kwargs):
        "Initializes default user"
        username = os.getenv('ADMIN_USERNAME', 'admin')
        password = os.getenv('ADMIN_PASSWORD', 'admin')
        if User.query.count() > 0:
            return
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()