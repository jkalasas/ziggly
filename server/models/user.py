from datetime import datetime
from hashlib import sha256

from sqlalchemy import or_
from sqlalchemy.orm import validates

from . import db

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=True, unique=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(64), nullable=False)
    last_access = db.Column(db.DateTime, default=datetime.utcnow)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)

    @validates('email')
    def validate_email(self, key, email: str):
        if '@' not in email:
            raise ValueError('Invalid email address')
        return email

    @validates('password')
    def hash_password(self, key, password: str):
        return sha256(password.encode()).hexdigest()
    
    def __repr__(self) -> str:
        return f'<User {self.id}>'

    @classmethod
    def verify(cls, identifier: str, password: str):
        user = cls.query.filter(
            or_(cls.username==identifier, cls.email==identifier),
            cls.password==sha256(password.encode()).hexdigest()
        ).first()
        return user