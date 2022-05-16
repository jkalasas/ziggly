from datetime import datetime
from hashlib import sha256

from sqlalchemy import or_
from sqlalchemy.orm import validates

from . import db

class User(db.Model):
    """Model storing user information

    ...
    Attributes
    ----------
    id: int
        id of the user
    email: str
        email of the user
    username: str
        username of the user
    password: str
        password of the user
    last_access: datetime.datetime
        record of the time the user was accessed
    created_on: datetime.datetime
        creation time of the user
    
    Methods
    -------
    validate_email(self, key: str, email: str) -> str
        validates the email

    hash_password(self, key: str, email: str) -> str
        hashes the password
    
    verify(cls, identifier: str, password: str) -> User | None:
        verifies the credentials
    """
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=True, unique=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(64), nullable=False)
    last_access = db.Column(db.DateTime, default=datetime.utcnow)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)

    @validates('email')
    def validate_email(self, key, email: str) -> str:
        """Validates the email after setting
        Parameters
        ----------
        self: User
            the user
        key: str
            name of the field
        email: str
            email of the user
        
        Raises
        ------
        ValueError
            raised when the email is invalid
        
        Returns
        -------
        str
            the email of the user
        """
        if '@' not in email:
            raise ValueError('Invalid email address')
        return email

    @validates('password')
    def hash_password(self, key, password: str):
        """Hashes the password after setting
        Parameters
        ----------
        self: User
            the user
        key: str
            the name of the field
        password: str
            the unhashed password
        
        Returns
        -------
        str
            the hashed password of the user
        """
        return sha256(password.encode()).hexdigest()
    
    def __repr__(self) -> str:
        return f'<User {self.id}>'

    @classmethod
    def verify(cls, identifier: str, password: str):
        """Verifies the credentials
        Parameters
        cls: User
            the User object
        identifier: str
            the username of email of the user
        password: str
            the password of the user
        
        Returns
        -------
        User
            the corresponding user from the credentials
        """
        user = cls.query.filter(
            or_(cls.username==identifier, cls.email==identifier),
            cls.password==sha256(password.encode()).hexdigest()
        ).first()
        return user