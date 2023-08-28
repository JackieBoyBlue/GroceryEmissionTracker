from .. import db
from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, PickleType, desc
from uuid import uuid4
from .transaction import Transaction, Merchant
from ..models.embedding import model as Embedder
import os
from ast import literal_eval


active_methods = []
if literal_eval(os.getenv('ESTIMATE_BY_ITEM', False)): active_methods.append('item')
if literal_eval(os.getenv('ESTIMATE_BY_MERCHANT', False)): active_methods.append('merchant')
if literal_eval(os.getenv('ESTIMATE_BY_MCC', True)): active_methods.append('mcc')


class GroceryItem(db.Model):
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
        item_emissions = {}
        no_weight_items = {}

        # Prioritise receipts as they have the most detailed data.
        if self._transaction.receipt.first():

            items = self._transaction.receipt.first().items

            # Look up item specific CO2e.
            if 'item' in active_methods:
                self.method = 'item'
                categories = GroceryItem.query.all()
                category_tuples = [(category.name, category.vector) for category in categories]
                
                # Put items with no weight provided into a separate dict.
                for item in list(items.items()):
                    weightprice = literal_eval(item[1])
                    if weightprice[0] == None:
                        no_weight_items[item[0]] = items.pop(item[0])

                # Esitmate the CO2e of items with weight provided.
                for item, weightprice in items.items():

                    weight, price = literal_eval(weightprice)
                    
                    item_embedding = Embedder.get_embeddings(item)[0]
                    best_match = Embedder.get_item_from_vectors(item_embedding, *category_tuples)

                    item_emissions[item] = weight * float(GroceryItem.query.get(best_match[0]).factor)

                self.co2e = sum(item_emissions.values())

        # Use previous estimates and merchant category to estimate the transaction, or remaining items with no weight provided.
        if Merchant.query.get(self._transaction.merchant_id) and (not self.method or len(no_weight_items) != 0):
            
            # First, try to base an estimate on previous user transactions with this merchant.
            try:
                if 'merchant' in active_methods:
                    if len(no_weight_items) > 0: self.method = 'item/merchant'
                    else: self.method = 'merchant'
                    merchant_transactions = Transaction.query.filter_by(merchant_id=self._transaction.merchant_id).all()
                    if merchant_transactions:

                        total_co2e = 0
                        total_amount_pence = 0

                        for transaction in merchant_transactions:
                            if transaction.co2e and transaction.amount_pence:
                                total_co2e += transaction.co2e
                                total_amount_pence += transaction.amount_pence
                        
                        if total_amount_pence == 0: raise Exception('No previous transactions with this merchant.')

                        merchant_emission_factor =  total_co2e / total_amount_pence

                        if len(no_weight_items) > 0:
                            for item, weightprice in no_weight_items.items():
                                price = literal_eval(weightprice)[1]
                                item_emissions[item] = price * merchant_emission_factor
                                self.co2e = sum(item_emissions.values())

                        else:
                            self.co2e = merchant_emission_factor * self._transaction.amount_pence
                else: raise Exception('Merchant method inactive.')

            # If that fails, base an estimate on the merchant's MCC.
            except:
                if 'mcc' in active_methods:

                    if len(no_weight_items) > 0: self.method = 'item/mcc'
                    else: self.method = 'mcc'

                    mcc = Merchant.query.get(self._transaction.merchant_id).mcc

                    match mcc:
                        case 5411:
                            # Grocery stores and supermarkets
                            MCC_emission_factor = 0.518 # kg CO2e / £
                        case 5422:
                            # Freezer and locker meat provisioners
                            MCC_emission_factor = 1.075
                        case 5441:
                            # Candy, nut, confectionery stores
                            MCC_emission_factor = 1.057
                        case 5451:
                            # Dairy product stores
                            MCC_emission_factor = 0.659
                        case 5462:
                            # Bakeries
                            MCC_emission_factor = 0.316
                        case 5499:
                            # Convenience stores and speciality markets
                            MCC_emission_factor = 0.518
                        case _:
                            raise Exception('MCC does not sell groceries.')

                    if mcc >= 5411 and mcc <= 5499:

                        if len(no_weight_items) != 0:
                            for item, weightprice in no_weight_items.items():
                                price = literal_eval(weightprice)[1]
                                item_emissions[item] = price * MCC_emission_factor
                                self.co2e = sum(item_emissions.values())
                        else:
                            self.co2e = MCC_emission_factor * (self._transaction.amount_pence / 100)
        
        if self.method and self.co2e:
            self.co2e = round(self.co2e, 5)
            db.session.add(self)
            transaction = Transaction.query.get(self.transaction_id)
            transaction.co2e = self.co2e
            db.session.commit()
        else:
            return 'Could not produce an estimate.'

        return {'method': self.method, 'co2e': self.co2e}
    

    def get_estimate(self) -> dict:
        """Returns a dictionary of the CO2e and the method used to calculate it."""

        return {'method': self.method, 'co2e': self.co2e}
