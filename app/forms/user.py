from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Regexp, EqualTo, ValidationError
from wtforms import StringField, SubmitField, HiddenField
from ..models.user import Receipt
from uuid import uuid4



class ReceiptForm(FlaskForm):
    """A form for listing the items in a receipt."""
    
    id = HiddenField(default=str(uuid4()))
    transaction_id = HiddenField(InputRequired())
    item = StringField('Item', validators=[InputRequired()])
    price = StringField('Price', validators=[InputRequired()])

    submit = SubmitField('Save receipt')
