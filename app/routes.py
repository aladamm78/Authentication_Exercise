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

        flash('Your account has been created! You are now logged in.', 'success')
        # Redirect to the user's profile page
        return redirect(url_for('main.user_profile', username=new_user.username))

    return render_template('register.html', form=form)


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('You have been logged in!', 'success')
            # Redirect to the user's profile page
            return redirect(url_for('main.user_profile', username=user.username))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.index'))  # Redirect to home instead of login page

@main.route('/users/<username>')
@login_required
def user_profile(username):
    # Get the user by username from the database
    user = User.query.filter_by(username=username).first_or_404()

    # Ensure that the logged-in user can only view their own profile
    if current_user.username != user.username:
        flash('You are not authorized to view this page.', 'danger')
        return redirect(url_for('main.index'))

    # Pass the user object to the template to display user info (except password)
    return render_template('user_profile.html', user=user)





