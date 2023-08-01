from .. import db
from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, PickleType
from uuid import uuid4
from .transaction import Transaction, Merchant
from ..datasets.mcc_codes import mcc_codes
from ..data_processing.models.embedding_model import model as Embedding


methods = ['item', 'category', 'merchant', 'mcc']

class Category(db.Model):
    __tablename__ = 'category'

    name = Column(String, primary_key=True)
    factor = Column(Integer, nullable=False)
    vector = Column(PickleType, nullable=False)

class Estimate(db.Model):
    """Estimate model for calculating the CO2e of a transaction."""
    __tablename__ = 'estimate'

    transaction = None

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    transaction_id = Column(String(36), ForeignKey("transaction.id"), nullable=False)
    method = Column(String, nullable=False)
    co2e = Column(Integer, nullable=False)
    datetime = Column(DateTime, nullable=False, default=db.func.now())


    def verify_method(self, method: str) -> bool:
        """Verifies that the method is valid. Returns True if valid, False if not."""

        if method in methods: return True

    
    def __init__(self, transaction: Transaction) -> None:
        """Initialises the Estimate object with a Transaction object."""

        if not isinstance(transaction, Transaction): raise TypeError('Estimate input must be a Transaction')
        self.transaction = transaction
        self.transaction_id = transaction.id

    
    def __repr__(self) -> str:
        """Returns a string representation of the Estimate in key-item pairs."""

        return '{id: ' + self.id + ', transaction_id: ' + self.transaction_id + '}'
    

    def get_estimate(self) -> dict:
        """Calculates the CO2e of the transaction. Returns a dictionary of the CO2e and the method used to calculate it."""

        # Prioritise receipts as they have the most detailed data.
        if self.transaction.receipt:

            items = self.transaction.receipt.first().items
            item_emissions = {}
            
            # First, try to look up item specific CO2e.
            try:
                if False:
                    pass
                else:
                    raise Exception('Partial or no item specific CO2e data found.')

            # If that fails, try to look up category specific CO2e.
            except:
                embedder = Embedding()
                categories = Category.query.all()

                for item in items:
                    item_vector = embedder(item[0])
                    
                    best_match = None
                    best_match_score = 0

                    for category in categories:
                        score = Embedding.get_score(item_vector, category.vector)
                        if score > best_match_score:
                            best_match = category
                            best_match_score = score
                    print(item)
                    print(best_match)
                    print(best_match_score)
                if True: pass
                else:
                    raise Exception('Partial or no category specific CO2e data found.')

        # If no receipt is available, base an estimate on the merchant.
        elif Merchant.query.get(self.transaction.merchant_id):
            
            # First, try to base an estimate on previous user transactions with this merchant.
            try:
                if False:
                    pass
                else:
                    raise Exception('No user-merchant history data found.')
            
            # If that fails, try to base an estimate on the merchant's MCC.
            except:
                mcc_code = mcc_codes[str(Merchant.query.get(self.transaction.merchant_id).mcc)]

                if bool:
                    pass
                else:
                    raise Exception('No mcc specific CO2e data found.')

        return {'method': self.method, 'co2e': self.co2e}
