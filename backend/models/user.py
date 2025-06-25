from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

# This will be imported from app.py
db = None

def get_db():
    """Get the db instance from the current app"""
    from flask import current_app
    return current_app.extensions['sqlalchemy']

class User(db.Model if db else object):
    __tablename__ = 'users'
    
    def __init_subclass__(cls, **kwargs):
        # This ensures the model works even when db is None initially
        super().__init_subclass__(**kwargs)
    
    id = db.Column(db.Integer, primary_key=True) if db else None
    email = db.Column(db.String(120), unique=True, nullable=False, index=True) if db else None
    password_hash = db.Column(db.String(255), nullable=False) if db else None
    first_name = db.Column(db.String(50), nullable=False) if db else None
    last_name = db.Column(db.String(50), nullable=False) if db else None
    primary_style = db.Column(db.String(50), nullable=True) if db else None
    belt_rank = db.Column(db.String(30), nullable=True) if db else None
    dojo = db.Column(db.String(100), nullable=True) if db else None
    created_at = db.Column(db.DateTime, default=datetime.utcnow) if db else None
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) if db else None
    
    def __init__(self, email, password, first_name, last_name, primary_style=None, belt_rank=None, dojo=None):
        self.email = email.lower().strip()
        self.password_hash = generate_password_hash(password)
        self.first_name = first_name.strip()
        self.last_name = last_name.strip()
        self.primary_style = primary_style
        self.belt_rank = belt_rank
        self.dojo = dojo
    
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
            'martial_art': self.primary_style,  # Frontend expects 'martial_art'
            'current_belt': self.belt_rank,     # Frontend expects 'current_belt'
            'dojo': self.dojo,
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
        try:
            from flask import current_app
            db = current_app.extensions['sqlalchemy']
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            from flask import current_app
            db = current_app.extensions['sqlalchemy']
            db.session.rollback()
            raise e
    
    def delete(self):
        """Delete user from database"""
        try:
            from flask import current_app
            db = current_app.extensions['sqlalchemy']
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            from flask import current_app
            db = current_app.extensions['sqlalchemy']
            db.session.rollback()
            raise e
    
    def __repr__(self):
        return f'<User {self.email}>'

# Dynamic model creation function
def create_user_model(db_instance):
    """Create User model with the provided db instance"""
    global db
    db = db_instance
    
    class User(db_instance.Model):
        __tablename__ = 'users'
        
        id = db_instance.Column(db_instance.Integer, primary_key=True)
        email = db_instance.Column(db_instance.String(120), unique=True, nullable=False, index=True)
        password_hash = db_instance.Column(db_instance.String(255), nullable=False)
        first_name = db_instance.Column(db_instance.String(50), nullable=False)
        last_name = db_instance.Column(db_instance.String(50), nullable=False)
        primary_style = db_instance.Column(db_instance.String(50), nullable=True)
        belt_rank = db_instance.Column(db_instance.String(30), nullable=True)
        dojo = db_instance.Column(db_instance.String(100), nullable=True)
        created_at = db_instance.Column(db_instance.DateTime, default=datetime.utcnow)
        updated_at = db_instance.Column(db_instance.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        # Relationships
        training_sessions = db_instance.relationship('TrainingSession', backref='user', lazy='dynamic', cascade='all, delete-orphan')
        technique_progress = db_instance.relationship('TechniqueProgress', backref='user', lazy='dynamic', cascade='all, delete-orphan')
        
        def __init__(self, email, password, first_name, last_name, primary_style=None, belt_rank=None, dojo=None):
            self.email = email.lower().strip()
            self.password_hash = generate_password_hash(password)
            self.first_name = first_name.strip()
            self.last_name = last_name.strip()
            self.primary_style = primary_style
            self.belt_rank = belt_rank
            self.dojo = dojo
        
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
                'martial_art': self.primary_style,  # Frontend expects 'martial_art'
                'current_belt': self.belt_rank,     # Frontend expects 'current_belt'
                'dojo': self.dojo,
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
            try:
                db_instance.session.add(self)
                db_instance.session.commit()
                return True
            except Exception as e:
                db_instance.session.rollback()
                raise e
        
        def delete(self):
            """Delete user from database"""
            try:
                db_instance.session.delete(self)
                db_instance.session.commit()
                return True
            except Exception as e:
                db_instance.session.rollback()
                raise e
        
        def __repr__(self):
            return f'<User {self.email}>'
    
    return User