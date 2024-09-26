from app import db  # Import the db instance from app/__init__.py
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    # Define columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Primary key
    username = db.Column(db.String(20), unique=True, nullable=False)  # Username (max 20 chars, unique)
    password = db.Column(db.Text, nullable=False)  # Password (hashed later, not nullable)
    email = db.Column(db.String(50), unique=True, nullable=False)  # Email (max 50 chars, unique)
    first_name = db.Column(db.String(30), nullable=False)  # First name (max 30 chars, not nullable)
    last_name = db.Column(db.String(30), nullable=False)  # Last name (max 30 chars, not nullable)

    feedbacks = db.relationship('Feedback', backref='user', lazy=True)
    # Define a method to represent the user object in a readable format
    def __repr__(self):
        return f"<User {self.username}>"

class Feedback(db.Model):
    __tablename__ = 'feedbacks'

    # Define columns
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)  # Title with max 100 chars, not nullable
    content = db.Column(db.Text, nullable=False)  # Content of feedback, not nullable
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key linking to User

    def __repr__(self):
        return f"Feedback('{self.title}', by {self.user.username})"