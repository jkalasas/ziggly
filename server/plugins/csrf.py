from hashlib import sha256
from uuid import uuid4

from flask import abort, request, Response, session

class CSRFProtect:
    """Simple CSRF implementation for flask application
    ...
    Methods
    -------
    __init__(self, app=None)
        initializes the model
    init_app(self, app)
        initializes the app with CSRFProtect
    """
    def __init__(self, app=None):
        """Initializes the model
        Parameters
        ----------
        app: Flask
            the flask application
        """
        self.app = app
        if not app:
            return 
        self.init_bindings()
    
    def init_app(self, app):
        """Initializes the app with CSRFProtect
        Parameters
        ----------
        app: Flask
            the flask application
        """
        self.app = app
        self.init_bindings()

    def init_bindings(self):
        "Binds the anti csrf functions to the application"
        self.app.before_request(self.verify_token)
        self.app.jinja_env.globals['csrf_token'] = self.set_token

    def get_token(self) -> str:
        """Gets the csrf token from the current session
        Returns
        -------
        str
            the csrf token
        """
        return self.has_token(session['csrftoken'])

    def hash_token(self, token: str) -> str:
        """Hashes the token
        Parameters
        ----------
        token: str
            the hashed token
        """
        return sha256((token + self.app.config['SECRET_KEY']).encode()).hexdigest()

    def create(self) -> tuple:
        """Generates a server and client side token
        Returns
        -------
        tuple
            contains the server and client side csrf tokens
        """
        token = uuid4().hex
        return token, self.hash_token(token)
    
    def verify(self, token) -> bool:
        """Matches the token with the token in the server
        Returns
        -------
        bool
            result of the matching
        """
        return self.hash_token(session.get('csrftoken','')) == token
    
    def set_token(self) -> str:
        """Sets the csrf token in the server
        Returns
        -------
        str
            the client csrf token
        """
        server, client = self.create()
        session['csrftoken'] = server
        return client
        
    def verify_token(self):
        "Verifies the token from the client"
        if request.method == 'GET' or not self.app.config.get('CSRF_ENABLED', False):
            return
        client_token = request.form.get('csrf_token', 
            request.headers.get('X-CSRF-Token',
            request.cookies.get('csrf_token'))
        )
        if not self.verify(client_token):
            return Response('Invalid CSRF Token'), 401