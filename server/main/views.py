from datetime import datetime

from flask import g, redirect, render_template, request, session, url_for

from server.models import db, User
from server.plugins.login_manager import login_required, login_user, logout_user
from . import bp

@bp.before_app_request
def before_app_request():
    if session.get('signed_in'):
        g.user = User.query.get(session.get('user_id'))
        if g.user:
            g.user.last_access = datetime.utcnow()
            db.session.commit()

@bp.get('/')
@login_required
def index():
    context = {
        'title': 'Home'
    }
    return render_template('main/index.html', **context)

@bp.get('/login')
def login_page():
    context = {
        'title': 'Login'
    }
    return render_template('main/login.html', **context)

@bp.post('/login')
def login():
    user = User.verify(
        request.form.get('username', ''),
        request.form.get('password', ''),
    )
    if user:
        login_user(user)
        return redirect(url_for('main.index'))
    return redirect(url_for('main.login'))

@bp.get('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@bp.post('/csrf-test')
def csrf_test():
    return 'Success'