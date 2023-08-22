from flask_wtf import FlaskForm
from wtforms.validators import InputRequired
from wtforms import StringField, SubmitField, HiddenField
from uuid import uuid4



class ReceiptForm(FlaskForm):
    """A form for listing the items in a receipt."""
    
    id = HiddenField(default=str(uuid4()))
    transaction_id = HiddenField(InputRequired())
    item = StringField('Item', validators=[InputRequired()], name='i1')
    price = StringField('Price', validators=[InputRequired()], name='p1')
    weight = StringField('Weight', name='w1')

    submit = SubmitField('Save receipt')
