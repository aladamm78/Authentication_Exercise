from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.forms import RegistrationForm, LoginForm, FeedbackForm
from app.models import User, Feedback

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

# User registration route
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

# User login route
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

# Logout route
@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.index'))  # Redirect to home instead of login page

# User profile route: Shows user's profile and feedback
@main.route('/users/<username>')
@login_required
def user_profile(username):
    # Get the user by username from the database
    user = User.query.filter_by(username=username).first_or_404()

    # Ensure that the logged-in user can only view their own profile
    if current_user.username != user.username:
        flash('You are not authorized to view this page.', 'danger')
        return redirect(url_for('main.index'))

    # Get all feedback from this user
    feedbacks = Feedback.query.filter_by(user_id=user.id).all()

    return render_template('user_profile.html', user=user, feedbacks=feedbacks)

# Add new feedback route
@main.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
@login_required
def new_feedback(username):
    user = User.query.filter_by(username=username).first_or_404()

    # Ensure only the logged-in user can add feedback to their own profile
    if current_user.username != user.username:
        flash('You are not authorized to add feedback for this user.', 'danger')
        return redirect(url_for('main.index'))

    form = FeedbackForm()
    if form.validate_on_submit():
        feedback = Feedback(title=form.title.data, content=form.content.data, user_id=user.id)
        db.session.add(feedback)
        db.session.commit()
        flash('Feedback added successfully!', 'success')
        return redirect(url_for('main.user_profile', username=user.username))

    return render_template('create_feedback.html', form=form, user=user)

@main.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
@login_required
def edit_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)

    if feedback.user_id != current_user.id:
        flash('You are not authorized to edit this feedback.', 'danger')
        return redirect(url_for('main.index'))

    form = FeedbackForm()
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()
        flash('Feedback updated successfully!', 'success')
        return redirect(url_for('main.user_profile', username=current_user.username))

    # Pre-fill the form with the current feedback details
    elif request.method == 'GET':
        form.title.data = feedback.title
        form.content.data = feedback.content

    return render_template('edit_feedback.html', form=form, feedback=feedback)


# Delete feedback route
@main.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
@login_required
def delete_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)

    # Ensure that only the user who wrote the feedback can delete it
    if feedback.user_id != current_user.id:
        flash('You are not authorized to delete this feedback.', 'danger')
        return redirect(url_for('main.index'))

    db.session.delete(feedback)
    db.session.commit()
    flash('Feedback deleted successfully!', 'success')
    return redirect(url_for('main.user_profile', username=current_user.username))

# Delete user route
@main.route('/users/<username>/delete', methods=['POST'])
@login_required
def delete_user(username):
    user = User.query.filter_by(username=username).first_or_404()

    # Only allow the logged-in user to delete their account
    if current_user.username != user.username:
        flash('You are not authorized to delete this account.', 'danger')
        return redirect(url_for('main.index'))

    # Delete all feedback associated with the user
    Feedback.query.filter_by(user_id=user.id).delete()

    # Delete the user
    db.session.delete(user)
    db.session.commit()

    # Log the user out and redirect to the homepage
    logout_user()
    flash('Your account and all associated feedback have been deleted.', 'success')
    return redirect(url_for('main.index'))




