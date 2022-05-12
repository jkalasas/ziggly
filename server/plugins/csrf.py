from hashlib import sha256
from uuid import uuid4

from flask import abort, request, Response, session

class CSRFProtect:
    def __init__(self, app=None):
        self.app = app
        if not app:
            return 
        self.init_bindings()
    
    def init_app(self, app):
        self.app = app
        self.init_bindings()

    def init_bindings(self):
        self.app.before_request(self.verify_token)
        self.app.jinja_env.globals['csrf_token'] = self.set_token

    def get_token(self) -> str:
        return sha256((session['csrftoken'] + self.app.config['SECRET_KEY']).encode()).hexdigest()

    def hash_token(self, token) -> str:
        return sha256((token + self.app.config['SECRET_KEY']).encode()).hexdigest()

    def create(self) -> str:
        token = uuid4().hex
        return token, self.hash_token(token)
    
    def verify(self, token) -> bool:
        return self.hash_token(session.get('csrftoken','')) == token
    
    def set_token(self):
        server, client = self.create()
        session['csrftoken'] = server
        return client
        
    def verify_token(self):
        if request.method == 'GET' or not self.app.config.get('CSRF_ENABLED', False):
            return
        client_token = request.form.get('csrf_token', 
            request.headers.get('X-CSRF-Token',
            request.cookies.get('csrf_token'))
        )
        if not self.verify(client_token):
            return Response('Invalid CSRF Token'), 401