from functools import wraps
from flask import g, redirect, session, url_for

from server.models import User

def login_user(user: User):
    """Sets the necessary variables in the session for a logged in user
    Parameters
    ----------
    user: User
        the user
    """
    if not user:
        return
    session['signed_in'] = True
    session['user_id'] = user.id

def logout_user():
    "Removes the user data in the session"
    if session.get('signed_in'):
        session['signed_in'] = False
        session['user_id'] = None

def login_required(fn):
    """Checks if the user is logged in
    Parameters
    ----------
    fn: function
        the route function
    Returns
    -------
    function
        the wrapper
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get('signed_in', False):
            return redirect(url_for('main.login'))
        return fn(*args, **kwargs)
    return wrapper
