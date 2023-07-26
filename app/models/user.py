from .. import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, String, Boolean, DateTime
from uuid import uuid4


class User(UserMixin, db.Model):
    """User model for storing user related details."""
    __tablename__ = 'user'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(50), nullable=False)
    email = Column(String(320), nullable=False)
    hashed_password = Column(String(120), nullable=False)
    admin = Column(Boolean, default=False, nullable=False)

    starling_uid = Column(String(36), nullable=True)
    refresh_token = Column(String(64), nullable=True)
    refresh_token_date = Column(DateTime, nullable=True, default=db.func.now())

    feed_logs = db.relationship('FeedLog', backref='user', lazy='dynamic', cascade='all, delete')
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic', cascade='all, delete')

    @property
    def password(self):
        """Raises an error if the password is accessed."""
        raise AttributeError('Password is not readable.')

    @password.setter
    def password(self, password):
        """Generates a hash of the user's password and updates the instance."""
        self.hashed_password = generate_password_hash(password)
    
    def verify_password(self, password):
        """Verifies the user's password against the hash stored in the instance."""
        return check_password_hash(self.hashed_password, password)
    
    def __repr__(self) -> String:
        """Returns a string representation of the user in key-item pairs."""
        return '{id: ' + str(self.id) + ', name: ' + self.name + ', email: ' + self.email + '}'


@login_manager.user_loader
def load_user(user_id):
    """Returns the current user to Login Manager."""
    return User.query.get(user_id)
