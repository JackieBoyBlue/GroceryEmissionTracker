from .. import app, db
from ..models.user import User, load_user
from ..forms.auth import RegistrationForm, LoginForm
from flask_login import login_user, logout_user, current_user
from flask import redirect, render_template, flash
from .starling import Starling



@app.route('/register', methods=['GET', 'POST'])
def register():
    """Allows users to create an account."""
    if current_user.is_authenticated:
        flash('Cannot access register page while logged in.')
        return redirect('/')
    else:
        registration_form = RegistrationForm()
        if registration_form.validate_on_submit():
            user_check = User.query.filter_by(email=registration_form.email.data).first()
            if user_check is None:
                user = User(name=registration_form.name.data, email=registration_form.email.data, password=registration_form.password.data)
                db.session.add(user)
                db.session.commit()
                return redirect('/')
        return render_template('auth/register.html', title='Register', registration_form=registration_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        login_user(user, remember=login_form.remember_me.data)
        return redirect('/starling')
    return render_template('auth/login.html', title='Login', login_form=login_form)


@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        Starling.logout()
        user = load_user(current_user.id)
        user.refresh_token = None
        user.refresh_token_date = None
        db.session.commit()
        logout_user()
    return redirect('/')


