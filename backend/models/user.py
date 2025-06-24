from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from app import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    primary_style = db.Column(db.String(50), nullable=True)
    belt_rank = db.Column(db.String(30), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    training_sessions = db.relationship('TrainingSession', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    technique_progress = db.relationship('TechniqueProgress', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, email, password, first_name, last_name, primary_style=None, belt_rank=None):
        self.email = email.lower().strip()
        self.password_hash = generate_password_hash(password)
        self.first_name = first_name.strip()
        self.last_name = last_name.strip()
        self.primary_style = primary_style
        self.belt_rank = belt_rank
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def set_password(self, password):
        """Set new password"""
        self.password_hash = generate_password_hash(password)
        self.updated_at = datetime.utcnow()
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'primary_style': self.primary_style,
            'belt_rank': self.belt_rank,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_sensitive:
            # Add any sensitive data that should only be included in specific contexts
            pass
            
        return data
    
    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        return User.query.filter_by(email=email.lower().strip()).first()
    
    def save(self):
        """Save user to database"""
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """Delete user from database"""
        db.session.delete(self)
        db.session.commit()
    
    def __repr__(self):
        return f'<User {self.email}>'