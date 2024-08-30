import uuid, os, binascii
from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    role = db.Column(db.String(10), default='user')
    business_id = db.Column(db.String(36), db.ForeignKey('business.id'))
    business = db.relationship('Business', backref='users', lazy=True)

class Availability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    available_days = db.Column(db.String(255))
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text) 
    interval = db.Column(db.Integer, nullable=False)
    
class Business(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(150))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(150))
    invite_code = db.Column(db.String(64), unique=True, default=lambda: binascii.hexlify(os.urandom(24)).decode())
    invite_code_used = db.Column(db.Boolean, default=False)
