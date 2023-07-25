from .. import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, ForeignKey, String, Boolean, Integer, DateTime, PickleType
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
    


class FeedLog(db.Model):
    """Feed Log model for tracking pull requests that return data."""
    __tablename__ = 'feed_log'

    id = Column(String(36), primary_key=True, nullable=False)
    datetime = Column(DateTime, nullable=False, default=db.func.now())

    transactions = db.relationship('Transaction', backref='feed_log', lazy='dynamic', cascade='all, delete')
    user_id = Column(String(36), ForeignKey("user.id"))
    item_count = Column(Integer, nullable=False)



class Transaction(db.Model):
    """Transaction model for storing transaction data."""
    __tablename__ = 'transaction'
    
    id = Column(String(36), primary_key=True, nullable=False)
    amount_pence = Column(Integer, nullable=False)
    datetime = Column(DateTime, nullable=False)

    merchant_id = Column(Integer, ForeignKey("merchant.id"))
    merchant_mcc = Column(Integer, nullable=True)

    receipt = db.relationship('Receipt', backref='receipt', lazy='dynamic', cascade='all, delete')

    user_id = Column(String(36), ForeignKey("user.id"))
    feed_log_id = Column(String(36), ForeignKey("feed_log.id"))

    co2e = Column(Integer, nullable=True)
    estimate = db.relationship('Estimate', backref='estimate', lazy='select')



class Receipt(db.Model):
    """Receipt model for storing receipt data."""
    __tablename__ = 'receipt'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    transaction_id = Column(String(36), ForeignKey("transaction.id"), nullable=False, unique=True)
    items = Column(PickleType, nullable=False)
    


class Merchant(db.Model):
    """Merchant model for storing merchant data."""
    __tablename__ = 'merchant'

    id = Column(String(36), primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    mcc = Column(Integer, nullable=False)

    transaction_id = db.relationship('Transaction', backref='merchant', lazy='select')



@login_manager.user_loader
def load_user(user_id):
    """Returns the current user to Login Manager."""
    return User.query.get(user_id)
