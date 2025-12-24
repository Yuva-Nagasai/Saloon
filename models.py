from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy.sql import func

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False) # stored in cents
    duration = db.Column(db.Integer, nullable=False) # in minutes
    image = db.Column(db.String(512), nullable=False)
    is_featured = db.Column(db.Boolean, default=False)

class Stylist(db.Model):
    __tablename__ = 'stylists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(512), nullable=False)
    specialties = db.Column(db.Text) # Storing as comma-separated string or JSON if preferred, simple string for now to match basic SQLite array behavior usually mocked

    def get_specialties_list(self):
        if self.specialties:
            return self.specialties.split(',')
        return []

class Testimonial(db.Model):
    __tablename__ = 'testimonials'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(100))
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    avatar = db.Column(db.String(512))

class Offer(db.Model):
    __tablename__ = 'offers'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    code = db.Column(db.String(50))
    discount = db.Column(db.String(50), nullable=False)
    expiry = db.Column(db.String(50)) # Keeping as string to match schema.ts simplicity, but DateTime is better usually.

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    stylist_id = db.Column(db.Integer, db.ForeignKey('stylists.id'))
    date = db.Column(db.String(50), nullable=False) # Simplified date string
    time = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    service = db.relationship('Service', backref='bookings')
    stylist = db.relationship('Stylist', backref='bookings')

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
