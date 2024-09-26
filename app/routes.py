from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.forms import RegistrationForm, LoginForm
from app.models import User

# Create a blueprint instance
main = Blueprint('main', __name__)

# Home route that redirects to /register
@main.route('/')
def index():
    return redirect(url_for('main.register'))

# About page route
@main.route('/about')
def about():
    return render_template('about.html')

# GET: Show registration form
# POST: Process registration form
@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, email=form.email.data,
                        password=hashed_password, first_name=form.first_name.data,
                        last_name=form.last_name.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created! You can now log in', 'success')
        return redirect(url_for('main.secret'))
    return render_template('register.html', form=form)

# GET: Show login form
# POST: Process login form
@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('You have been logged in!', 'success')
            return redirect(url_for('main.secret'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)

# Secret page: Only accessible to logged-in users
@main.route('/secret')
@login_required
def secret():
    return "You made it!"
