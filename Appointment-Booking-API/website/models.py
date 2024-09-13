from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

# User model (for both regular users and admins)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), default='user')  # role can be 'user', 'admin', or 'manager'
    business = db.relationship('Business', backref='owner', uselist=False)  # One-to-one relationship with Business
    
    # Specify the foreign_keys argument to avoid ambiguity
    appointments = db.relationship('Appointment', foreign_keys='Appointment.user_id', backref='user', lazy=True)  # One-to-many relationship with Appointment

# Business model (for manager and admin accounts)
class Business(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)  # One-to-one with User
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(150), nullable=False)

# Availability model (to track admin availability)
class Availability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # References the admin's user ID
    day = db.Column(db.String(50), nullable=False)  # e.g., "Monday"
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

# Appointment category model (to define appointment types)
class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255))

# Appointment model (to track individual appointments)
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # References the user's ID
    
    # Specify the foreign_keys argument to avoid ambiguity for admin relationship
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # References the admin's ID
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)  # References the category ID
    time_slot = db.Column(db.DateTime, nullable=False)  # The scheduled appointment time
    
    # Relationships
    category = db.relationship('Categories', backref='appointments')  # Relationship with Categories
    admin = db.relationship('User', foreign_keys=[admin_id], backref='admin_appointments')  # Relationship with Admin (as user)
