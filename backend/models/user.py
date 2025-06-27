from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_models(db):
    """Create all models with the provided db instance"""
    
    class User(db.Model):
        __tablename__ = 'users'
        __table_args__ = {'extend_existing': True}  # ADDED: This fixes the duplicate table error
        
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(120), unique=True, nullable=False, index=True)
        password_hash = db.Column(db.String(255), nullable=False)
        first_name = db.Column(db.String(50), nullable=False)
        last_name = db.Column(db.String(50), nullable=False)
        
        # Enhanced profile fields
        bio = db.Column(db.Text, nullable=True)
        location = db.Column(db.String(100), nullable=True)
        date_of_birth = db.Column(db.Date, nullable=True)
        
        # Martial arts information
        primary_style = db.Column(db.String(50), nullable=True)
        belt_rank = db.Column(db.String(30), nullable=True)
        years_training = db.Column(db.Integer, default=0)
        instructor = db.Column(db.String(100), nullable=True)
        dojo = db.Column(db.String(100), nullable=True)
        goals = db.Column(db.Text, nullable=True)
        
        # Timestamps
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        def __init__(self, email, password, first_name, last_name, **kwargs):
            self.email = email.lower().strip()
            self.password_hash = generate_password_hash(password)
            self.first_name = first_name.strip()
            self.last_name = last_name.strip()
            
            # Enhanced profile fields
            self.bio = kwargs.get('bio')
            self.location = kwargs.get('location')
            self.date_of_birth = kwargs.get('date_of_birth')
            
            # Martial arts fields
            self.primary_style = kwargs.get('primary_style')
            self.belt_rank = kwargs.get('belt_rank')
            self.years_training = kwargs.get('years_training', 0)
            self.instructor = kwargs.get('instructor')
            self.dojo = kwargs.get('dojo')
            self.goals = kwargs.get('goals')
        
        def check_password(self, password):
            """Check if provided password matches hash"""
            return check_password_hash(self.password_hash, password)
        
        def set_password(self, password):
            """Set new password"""
            self.password_hash = generate_password_hash(password)
            self.updated_at = datetime.utcnow()
        
        def update_profile(self, **kwargs):
            """Update user profile fields"""
            # Personal information
            if 'first_name' in kwargs:
                self.first_name = kwargs['first_name'].strip()
            if 'last_name' in kwargs:
                self.last_name = kwargs['last_name'].strip()
            if 'bio' in kwargs:
                self.bio = kwargs['bio']
            if 'location' in kwargs:
                self.location = kwargs['location']
            if 'date_of_birth' in kwargs:
                self.date_of_birth = kwargs['date_of_birth']
            
            # Martial arts information
            if 'primary_style' in kwargs:
                self.primary_style = kwargs['primary_style']
            if 'belt_rank' in kwargs:
                self.belt_rank = kwargs['belt_rank']
            if 'years_training' in kwargs:
                self.years_training = kwargs['years_training']
            if 'instructor' in kwargs:
                self.instructor = kwargs['instructor']
            if 'dojo' in kwargs:
                self.dojo = kwargs['dojo']
            if 'goals' in kwargs:
                self.goals = kwargs['goals']
            
            self.updated_at = datetime.utcnow()
        
        def get_training_stats(self):
            """Get user's training statistics"""
            from sqlalchemy import func
            
            # Get session count and total hours
            session_stats = db.session.query(
                func.count(TrainingSession.id).label('session_count'),
                func.coalesce(func.sum(TrainingSession.duration), 0).label('total_minutes')
            ).filter_by(user_id=self.id).first()
            
            # Get technique count
            technique_count = TechniqueProgress.query.filter_by(user_id=self.id).count()
            
            return {
                'session_count': session_stats.session_count if session_stats else 0,
                'total_hours': round((session_stats.total_minutes or 0) / 60, 1) if session_stats else 0,
                'technique_count': technique_count
            }
        
        def to_dict(self, include_sensitive=False, include_stats=False):
            """Convert user to dictionary"""
            data = {
                'id': self.id,
                'email': self.email,
                'name': f"{self.first_name} {self.last_name}".strip(),
                'first_name': self.first_name,
                'last_name': self.last_name,
                'bio': self.bio,
                'location': self.location,
                'dateOfBirth': self.date_of_birth.isoformat() if self.date_of_birth else None,
                'primaryStyle': self.primary_style,
                'currentBelt': self.belt_rank,
                'yearsTraining': self.years_training or 0,
                'instructor': self.instructor,
                'dojo': self.dojo,
                'goals': self.goals,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            }
            
            if include_stats:
                stats = self.get_training_stats()
                data.update(stats)
            
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
                db.session.add(self)
                db.session.commit()
                return True
            except Exception as e:
                db.session.rollback()
                raise e
        
        def delete(self):
            """Delete user from database"""
            try:
                # Delete related records first
                UserPreferences.query.filter_by(user_id=self.id).delete()
                TechniqueProgress.query.filter_by(user_id=self.id).delete()
                TrainingSession.query.filter_by(user_id=self.id).delete()
                
                # Delete user
                db.session.delete(self)
                db.session.commit()
                return True
            except Exception as e:
                db.session.rollback()
                raise e
        
        def __repr__(self):
            return f'<User {self.email}>'

    class UserPreferences(db.Model):
        __tablename__ = 'user_preferences'
        __table_args__ = {'extend_existing': True}  # ADDED: This fixes the duplicate table error
        
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
        
        # Notification preferences
        email_notifications = db.Column(db.Boolean, default=True)
        weekly_digest = db.Column(db.Boolean, default=True)
        
        # Privacy preferences
        public_profile = db.Column(db.Boolean, default=False)
        show_progress = db.Column(db.Boolean, default=True)
        
        # App preferences
        theme = db.Column(db.String(20), default='light')  # light, dark, auto
        language = db.Column(db.String(10), default='en')
        
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        # Relationship
        user = db.relationship('User', backref=db.backref('preferences', uselist=False))
        
        def __init__(self, user_id, **kwargs):
            self.user_id = user_id
            self.email_notifications = kwargs.get('email_notifications', True)
            self.weekly_digest = kwargs.get('weekly_digest', True)
            self.public_profile = kwargs.get('public_profile', False)
            self.show_progress = kwargs.get('show_progress', True)
            self.theme = kwargs.get('theme', 'light')
            self.language = kwargs.get('language', 'en')
        
        def update_preferences(self, **kwargs):
            """Update user preferences"""
            if 'email_notifications' in kwargs:
                self.email_notifications = kwargs['email_notifications']
            if 'weekly_digest' in kwargs:
                self.weekly_digest = kwargs['weekly_digest']
            if 'public_profile' in kwargs:
                self.public_profile = kwargs['public_profile']
            if 'show_progress' in kwargs:
                self.show_progress = kwargs['show_progress']
            if 'theme' in kwargs:
                self.theme = kwargs['theme']
            if 'language' in kwargs:
                self.language = kwargs['language']
            
            self.updated_at = datetime.utcnow()
        
        def to_dict(self):
            """Convert preferences to dictionary"""
            return {
                'emailNotifications': self.email_notifications,
                'weeklyDigest': self.weekly_digest,
                'publicProfile': self.public_profile,
                'showProgress': self.show_progress,
                'theme': self.theme,
                'language': self.language
            }
        
        def save(self):
            """Save preferences to database"""
            db.session.add(self)
            db.session.commit()
        
        @staticmethod
        def get_or_create(user_id):
            """Get user preferences or create default ones"""
            prefs = UserPreferences.query.filter_by(user_id=user_id).first()
            if not prefs:
                prefs = UserPreferences(user_id=user_id)
                prefs.save()
            return prefs
        
        def __repr__(self):
            return f'<UserPreferences for user {self.user_id}>'

    class TrainingSession(db.Model):
        __tablename__ = 'training_sessions'
        __table_args__ = {'extend_existing': True}  # ADDED: This fixes the duplicate table error
        
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
        date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
        duration = db.Column(db.Integer, nullable=False)  # Duration in minutes
        style = db.Column(db.String(50), nullable=False)
        techniques_practiced = db.Column(db.JSON, nullable=True)  # List of technique names
        notes = db.Column(db.Text, nullable=True)
        intensity_level = db.Column(db.Integer, nullable=False, default=5)  # 1-10 scale
        energy_before = db.Column(db.Integer, nullable=True)  # 1-10 scale
        energy_after = db.Column(db.Integer, nullable=True)  # 1-10 scale
        mood = db.Column(db.String(50), nullable=True)
        
        # Fitness tracking integration
        calories_burned = db.Column(db.Integer, nullable=True)
        avg_heart_rate = db.Column(db.Integer, nullable=True)
        max_heart_rate = db.Column(db.Integer, nullable=True)
        fitbit_activity_id = db.Column(db.String(100), nullable=True)
        
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        # Relationship
        user = db.relationship('User', backref='training_sessions')
        
        def __init__(self, user_id, duration, style, date=None, **kwargs):
            self.user_id = user_id
            self.duration = duration
            self.style = style
            self.date = date or datetime.utcnow().date()
            
            # Set optional fields
            self.techniques_practiced = kwargs.get('techniques_practiced', [])
            self.notes = kwargs.get('notes')
            self.intensity_level = kwargs.get('intensity_level', 5)
            self.energy_before = kwargs.get('energy_before')
            self.energy_after = kwargs.get('energy_after')
            self.mood = kwargs.get('mood')
            self.calories_burned = kwargs.get('calories_burned')
            self.avg_heart_rate = kwargs.get('avg_heart_rate')
            self.max_heart_rate = kwargs.get('max_heart_rate')
            self.fitbit_activity_id = kwargs.get('fitbit_activity_id')
        
        def to_dict(self):
            """Convert training session to dictionary"""
            return {
                'id': self.id,
                'user_id': self.user_id,
                'date': self.date.isoformat() if self.date else None,
                'duration': self.duration,
                'style': self.style,
                'techniques_practiced': self.techniques_practiced or [],
                'notes': self.notes,
                'intensity_level': self.intensity_level,
                'energy_before': self.energy_before,
                'energy_after': self.energy_after,
                'mood': self.mood,
                'calories_burned': self.calories_burned,
                'avg_heart_rate': self.avg_heart_rate,
                'max_heart_rate': self.max_heart_rate,
                'fitbit_activity_id': self.fitbit_activity_id,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            }
        
        def save(self):
            """Save training session to database"""
            db.session.add(self)
            db.session.commit()
        
        def delete(self):
            """Delete training session from database"""
            db.session.delete(self)
            db.session.commit()
        
        @staticmethod
        def get_user_sessions(user_id, limit=None):
            """Get training sessions for a user"""
            query = TrainingSession.query.filter_by(user_id=user_id).order_by(TrainingSession.date.desc())
            if limit:
                query = query.limit(limit)
            return query.all()
        
        def __repr__(self):
            return f'<TrainingSession {self.id}: {self.style} on {self.date}>'

    class TechniqueProgress(db.Model):
        __tablename__ = 'technique_progress'
        
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
        technique_name = db.Column(db.String(100), nullable=False)
        style = db.Column(db.String(50), nullable=False)
        proficiency_level = db.Column(db.Integer, nullable=False, default=1)  # 1-10 scale
        last_practiced = db.Column(db.Date, nullable=True)
        notes = db.Column(db.Text, nullable=True)
        video_url = db.Column(db.String(255), nullable=True)
        practice_count = db.Column(db.Integer, nullable=False, default=0)
        mastery_status = db.Column(db.String(20), nullable=False, default='learning')  # learning, practicing, competent, mastery
        
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        # FIXED: Ensure unique technique per user per style AND allow extending table
        __table_args__ = (
            db.UniqueConstraint('user_id', 'technique_name', 'style', name='unique_user_technique_style'),
            {'extend_existing': True}  # ADDED: This fixes the duplicate table error
        )
        
        # Relationship
        user = db.relationship('User', backref='technique_progress')
        
        def __init__(self, user_id, technique_name, style, **kwargs):
            self.user_id = user_id
            self.technique_name = technique_name
            self.style = style
            self.proficiency_level = kwargs.get('proficiency_level', 1)
            self.last_practiced = kwargs.get('last_practiced')
            self.notes = kwargs.get('notes')
            self.video_url = kwargs.get('video_url')
            self.practice_count = kwargs.get('practice_count', 0)
            self.mastery_status = kwargs.get('mastery_status', 'learning')
        
        def update_practice(self, proficiency_level=None, notes=None):
            """Update practice information"""
            self.practice_count += 1
            self.last_practiced = datetime.utcnow().date()
            
            if proficiency_level:
                self.proficiency_level = proficiency_level
                
            if notes:
                self.notes = notes
                
            # Auto-update mastery status based on proficiency
            if self.proficiency_level >= 9:
                self.mastery_status = 'mastery'
            elif self.proficiency_level >= 7:
                self.mastery_status = 'competent'
            elif self.proficiency_level >= 4:
                self.mastery_status = 'practicing'
            else:
                self.mastery_status = 'learning'
                
            self.updated_at = datetime.utcnow()
        
        def to_dict(self):
            """Convert technique progress to dictionary"""
            return {
                'id': self.id,
                'user_id': self.user_id,
                'technique_name': self.technique_name,
                'style': self.style,
                'proficiency_level': self.proficiency_level,
                'last_practiced': self.last_practiced.isoformat() if self.last_practiced else None,
                'notes': self.notes,
                'video_url': self.video_url,
                'practice_count': self.practice_count,
                'mastery_status': self.mastery_status,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            }
        
        def save(self):
            """Save technique progress to database"""
            db.session.add(self)
            db.session.commit()
        
        def delete(self):
            """Delete technique progress from database"""
            db.session.delete(self)
            db.session.commit()
        
        @staticmethod
        def get_user_techniques(user_id, style=None):
            """Get technique progress for a user, optionally filtered by style"""
            query = TechniqueProgress.query.filter_by(user_id=user_id)
            if style:
                query = query.filter_by(style=style)
            return query.order_by(TechniqueProgress.technique_name).all()
        
        def __repr__(self):
            return f'<TechniqueProgress {self.technique_name} ({self.style}): {self.proficiency_level}/10>'

    return User, TrainingSession, TechniqueProgress, UserPreferences