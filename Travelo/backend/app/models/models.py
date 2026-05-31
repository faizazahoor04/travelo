from datetime import datetime
from app import db
import bcrypt

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    preferences = db.relationship('UserPreference', back_populates='user', uselist=False)
    travel_history = db.relationship('TravelHistory', back_populates='user', lazy=True)

    def set_password(self, password):
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))


class UserPreference(db.Model):
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    preferred_destination_type = db.Column(db.String(50), nullable=True)
    max_budget = db.Column(db.Integer, nullable=True, default=100)
    travel_style = db.Column(db.String(50), nullable=True)
    preferred_region = db.Column(db.String(100), nullable=True)

    user = db.relationship('User', back_populates='preferences')


class TravelHistory(db.Model):
    __tablename__ = 'travel_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    destination_name = db.Column(db.String(100), nullable=False)
    user_rating = db.Column(db.Integer, nullable=True)
    visit_date = db.Column(db.Date, nullable=True)

    user = db.relationship('User', back_populates='travel_history')