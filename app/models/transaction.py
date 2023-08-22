from .. import db
from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, PickleType
from uuid import uuid4


class Transaction(db.Model):
    """Transaction model for storing transaction data."""
    __tablename__ = 'transaction'
    
    id = Column(String(36), primary_key=True, nullable=False)
    amount_pence = Column(Integer, nullable=False)
    datetime = Column(DateTime, nullable=False)

    merchant_id = Column(Integer, ForeignKey("merchant.id"))

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


class FeedLog(db.Model):
    """Feed Log model for tracking pull requests that return data."""
    __tablename__ = 'feed_log'

    id = Column(String(36), primary_key=True, nullable=False)
    datetime = Column(DateTime, nullable=False, default=db.func.now())

    transactions = db.relationship('Transaction', backref='feed_log', lazy='dynamic', cascade='all, delete')
    user_id = Column(String(36), ForeignKey("user.id"))
    item_count = Column(Integer, nullable=False)
