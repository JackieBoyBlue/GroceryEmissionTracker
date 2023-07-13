from flask_wtf import FlaskForm
from ..models.user import User
from wtforms.validators import InputRequired, Regexp, EqualTo, ValidationError
from wtforms import EmailField, StringField, PasswordField, SubmitField, BooleanField


# Regex checks for forms.
password_regex = '^(?=.*[A-Za-z])(?=.*\d)(?=.*[!£$%^&*-_=:;@~#?])[A-Za-z\d!£$%^&*-_=:;@~#?]{8,50}$'
password_regex_explain = 'Minimum eight characters; at least one letter, one number and one special character (excluding brackets, quotation marks and slashes).'


class RegistrationForm(FlaskForm):
    """A form used for registering a new user."""
    name = StringField('Name', validators=[InputRequired()])
    email = EmailField('Email', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired(), Regexp(password_regex, message=password_regex_explain)])
    confirm = PasswordField('Repeat password', validators=[EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('An account already exists for this email address.')

    def validate_password(self, password):
        if len(password.data) > 50:
            raise ValidationError("Arer you sure you'll remember such a long password? Please use 50 or fewer characters..")


class LoginForm(FlaskForm):
    """Used to let the user log in."""
    email = StringField('Email', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Login')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Unable to find an account with this email address.')

    def validate_password(self, password):
        user = User.query.filter_by(email=self.email.data).first()
        if user is not None and not user.verify_password(password.data):
            raise ValidationError('Incorrect password.')