from .. import db
from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, PickleType, desc
from uuid import uuid4
from .transaction import Transaction, Merchant
from ..datasets.mcc_codes import mcc_codes
from ..datasets.item_emission_factors import item_emission_factors
from ..models.embedding import model as Embedder
import os
from ast import literal_eval


active_methods = []
if literal_eval(os.getenv('ESTIMATE_BY_ITEM', False)): active_methods.append('item')
if literal_eval(os.getenv('ESTIMATE_BY_ITEM_CATEGORY', True)): active_methods.append('category')
if literal_eval(os.getenv('ESTIMATE_BY_MERCHANT', False)): active_methods.append('merchant')
if literal_eval(os.getenv('ESTIMATE_BY_MCC', True)): active_methods.append('mcc')


class Category(db.Model):
    __tablename__ = 'category'

    name = Column(String, primary_key=True)
    factor = Column(Integer, nullable=False)
    vector = Column(PickleType, nullable=False)

class Estimate(db.Model):
    """Estimate model for calculating the CO2e of a transaction."""
    __tablename__ = 'estimate'

    _transaction = None
    _existing_estimate = False

    id = Column(String(36), primary_key=True)
    transaction_id = Column(String(36), ForeignKey("transaction.id"), nullable=False)
    method = Column(String, nullable=False)
    co2e = Column(Integer, nullable=False)
    datetime = Column(DateTime, nullable=False, default=db.func.now())

    
    def __init__(self, transaction: Transaction) -> None:
        """Initialises the Estimate object with a Transaction object."""

        if not isinstance(transaction, Transaction): raise TypeError('Estimate input must be a Transaction')
        self._transaction = transaction
        self.id = str(uuid4())
        self.transaction_id = transaction.id

        existing_estimate = Estimate.query.filter_by(transaction_id=transaction.id).order_by(desc('datetime')).first()
        if existing_estimate:
            self._existing_estimate = True
            self.method = existing_estimate.method
            self.co2e = existing_estimate.co2e

    
    def __repr__(self) -> str:
        """Returns a string representation of the Estimate in key-item pairs."""

        if self.co2e: return '{id: ' + self.id + ', transaction_id: ' + self.transaction_id + ',' + ' method: ' + self.method + ', co2e: ' + str(self.co2e) + '}'
        return '{id: ' + self.id + ', transaction_id: ' + self.transaction_id + '}'
    

    def generate_estimate(self) -> dict:
        """Calculates the CO2e of the transaction. Returns a dictionary of the CO2e and the method used to calculate it."""

        # Prioritise receipts as they have the most detailed data.
        if self._transaction.receipt.first():

            items = self._transaction.receipt.first().items
            item_emissions = {}

            # Look up item specific CO2e.
            if 'item' in active_methods:
                self.method = 'item'
                # db_item_names = [key for key in item_emission_factors.keys()]
                # for item, price in items.items():
                #     print()
                #     print(item)
                        
                #     best_match = Embedder.get_category_from_strings(item, *db_item_names)

                #     print(best_match)
                #     print()
                pass

            # Look up item category specific CO2e.
            elif 'category' in active_methods and self.method not in ['item', 'category']:
                self.method = 'category'

                categories = Category.query.all()
                category_tuples = [(category.name, category.vector) for category in categories]

                for item, price in items.items():

                    item_embedding = Embedder.get_embeddings(item)[0]
                    best_match = Embedder.get_category_from_vectors(item_embedding, *category_tuples)

                    item_emissions[item] = float(price) * float(Category.query.get(best_match[0]).factor)

                self.co2e = sum(item_emissions.values())

        # If no receipt is available, base an estimate on the merchant.
        elif Merchant.query.get(self._transaction.merchant_id):
            
            # First, try to base an estimate on previous user transactions with this merchant.
            if 'merchant' in active_methods and self.method not in ['item', 'category', 'merchant']:
                self.method = 'merchant'
                pass
            
            # If that fails, try to base an estimate on the merchant's MCC.
            if 'mcc' in active_methods:
                self.method = 'mcc'
                mcc_code = mcc_codes[str(Merchant.query.get(self._transaction.merchant_id).mcc)]
                pass
        
        if self.method and self.co2e:
            transaction = Transaction.query.get(self.transaction_id)
            transaction.co2e = self.co2e
            db.session.add(self)
            db.session.commit()
        else:
            return 'Could not produce an estimate.'

        return {'method': self.method, 'co2e': self.co2e}
    

    def get_estimate(self) -> dict:
        """Returns a dictionary of the CO2e and the method used to calculate it."""

        return {'method': self.method, 'co2e': self.co2e}
