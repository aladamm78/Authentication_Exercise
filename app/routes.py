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
        # Check if the username or email already exists in the database
        existing_user = User.query.filter_by(username=form.username.data).first()
        existing_email = User.query.filter_by(email=form.email.data).first()

        if existing_user:
            flash('Username already exists. Please choose another.', 'danger')
            return redirect(url_for('main.register'))

        if existing_email:
            flash('Email is already registered. Please use a different email.', 'danger')
            return redirect(url_for('main.register'))

        # Hash the password and create the new user
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, email=form.email.data,
                        password=hashed_password, first_name=form.first_name.data,
                        last_name=form.last_name.data)
        db.session.add(new_user)
        db.session.commit()

        # Automatically log the user in after successful registration
        login_user(new_user)

        print(f"User {new_user.username} registered and logged in. Redirecting to /secret")

        flash('Your account has been created! You are now logged in.', 'success')
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
            print(f"User {user.username} logged in. Redirecting to /secret")

            flash('You have been logged in!', 'success')

            # Redirect to the secret page after successful login
            return redirect(url_for('main.secret'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    
    return render_template('login.html', form=form)

# Logout route
@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.login'))

# Secret page: Only accessible to logged-in users
@main.route('/secret')
@login_required
def secret():
    return "You made it!"


