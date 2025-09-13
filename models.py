# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default='customer')  # 'customer' or 'admin'
    wallet_address = db.Column(db.String(200), unique=True, nullable=True)
    kyc_verified = db.Column(db.Boolean, default=False)  # Admin-approved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    policies = db.relationship('Policy', backref='user', lazy=True)

    def is_admin(self):
        return self.role == 'admin'


class Policy(db.Model):
    __tablename__ = 'policies'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # User input fields
    income = db.Column(db.Float, nullable=False)
    coverage_amount = db.Column(db.Float, nullable=False)
    premium_amount = db.Column(db.Float, nullable=False)
    deductible = db.Column(db.Float, nullable=False)
    occupation = db.Column(db.String(100), nullable=True)
    geographic_info = db.Column(db.String(100), nullable=True)
    insurance_products = db.Column(db.String(200), nullable=True)
    
    # Prediction results
    risk_score = db.Column(db.Float, nullable=False)  
    risk_level = db.Column(db.String(20), nullable=False)  
    
    # Blockchain
   
    blockchain_txn = db.Column(db.String(200), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
