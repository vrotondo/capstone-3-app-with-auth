# Create this file: backend/models/exercise.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Text, JSON
import json

def create_exercise_models(db):
    """Create exercise-related database models"""
    
    class ExerciseCategory(db.Model):
        """Exercise categories from wger (Cardio, Strength, etc.)"""
        __tablename__ = 'exercise_categories'
        __table_args__ = {'extend_existing': True}
        
        id = db.Column(db.Integer, primary_key=True)
        wger_id = db.Column(db.Integer, unique=True, nullable=False)  # wger API ID
        name = db.Column(db.String(100), nullable=False)
        description = db.Column(Text)
        
        # Relationships
        exercises = db.relationship('Exercise', backref='category_ref', lazy='dynamic')
        
        def to_dict(self):
            return {
                'id': self.id,
                'wger_id': self.wger_id,
                'name': self.name,
                'description': self.description
            }
    
    class MuscleGroup(db.Model):
        """Muscle groups from wger"""
        __tablename__ = 'muscle_groups'
        __table_args__ = {'extend_existing': True}
        
        id = db.Column(db.Integer, primary_key=True)
        wger_id = db.Column(db.Integer, unique=True, nullable=False)
        name = db.Column(db.String(100), nullable=False)
        name_en = db.Column(db.String(100))  # English name
        is_front = db.Column(db.Boolean, default=True)  # Front or back of body
        
        def to_dict(self):
            return {
                'id': self.id,
                'wger_id': self.wger_id,
                'name': self.name,
                'name_en': self.name_en,
                'is_front': self.is_front
            }
    
    class Equipment(db.Model):
        """Exercise equipment from wger"""
        __tablename__ = 'equipment'
        __table_args__ = {'extend_existing': True}
        
        id = db.Column(db.Integer, primary_key=True)
        wger_id = db.Column(db.Integer, unique=True, nullable=False)
        name = db.Column(db.String(100), nullable=False)
        
        def to_dict(self):
            return {
                'id': self.id,
                'wger_id': self.wger_id,
                'name': self.name
            }
    
    class Exercise(db.Model):
        """Enhanced exercise model with wger integration"""
        __tablename__ = 'exercises'
        __table_args__ = {'extend_existing': True}
        
        id = db.Column(db.Integer, primary_key=True)
        wger_id = db.Column(db.Integer, unique=True, nullable=True)  # From wger API
        
        # Basic exercise info
        name = db.Column(db.String(200), nullable=False)
        description = db.Column(Text)
        category_id = db.Column(db.Integer, db.ForeignKey('exercise_categories.id'))
        
        # Exercise details
        instructions = db.Column(JSON)  # Step-by-step instructions as JSON array
        primary_muscles = db.Column(JSON)  # Primary muscle groups as JSON array
        secondary_muscles = db.Column(JSON)  # Secondary muscle groups as JSON array
        equipment_needed = db.Column(JSON)  # Required equipment as JSON array
        
        # Martial arts specific
        martial_arts_relevant = db.Column(db.Boolean, default=False)
        difficulty_level = db.Column(db.String(20))  # beginner, intermediate, advanced
        
        # Meta information
        license_author = db.Column(db.String(200))
        creation_date = db.Column(db.DateTime, default=datetime.utcnow)
        last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        # Custom exercises (not from wger)
        is_custom = db.Column(db.Boolean, default=False)
        created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
        
        # Relationships
        workout_exercises = db.relationship('WorkoutExercise', backref='exercise_ref', lazy='dynamic', cascade='all, delete-orphan')
        
        def to_dict(self):
            return {
                'id': self.id,
                'wger_id': self.wger_id,
                'name': self.name,
                'description': self.description,
                'category': self.category_ref.to_dict() if self.category_ref else None,
                'instructions': self.get_instructions(),
                'primary_muscles': self.get_primary_muscles(),
                'secondary_muscles': self.get_secondary_muscles(),
                'equipment_needed': self.get_equipment_needed(),
                'martial_arts_relevant': self.martial_arts_relevant,
                'difficulty_level': self.difficulty_level,
                'is_custom': self.is_custom,
                'license_author': self.license_author,
                'creation_date': self.creation_date.isoformat() if self.creation_date else None,
                'last_updated': self.last_updated.isoformat() if self.last_updated else None
            }
        
        def get_instructions(self):
            """Get instructions as a list"""
            if isinstance(self.instructions, str):
                try:
                    return json.loads(self.instructions)
                except:
                    return [self.instructions] if self.instructions else []
            return self.instructions or []
        
        def set_instructions(self, instructions_list):
            """Set instructions from a list"""
            self.instructions = json.dumps(instructions_list) if instructions_list else None
        
        def get_primary_muscles(self):
            """Get primary muscles as a list"""
            if isinstance(self.primary_muscles, str):
                try:
                    return json.loads(self.primary_muscles)
                except:
                    return [self.primary_muscles] if self.primary_muscles else []
            return self.primary_muscles or []
        
        def set_primary_muscles(self, muscles_list):
            """Set primary muscles from a list"""
            self.primary_muscles = json.dumps(muscles_list) if muscles_list else None
        
        def get_secondary_muscles(self):
            """Get secondary muscles as a list"""
            if isinstance(self.secondary_muscles, str):
                try:
                    return json.loads(self.secondary_muscles)
                except:
                    return [self.secondary_muscles] if self.secondary_muscles else []
            return self.secondary_muscles or []
        
        def set_secondary_muscles(self, muscles_list):
            """Set secondary muscles from a list"""
            self.secondary_muscles = json.dumps(muscles_list) if muscles_list else None
        
        def get_equipment_needed(self):
            """Get equipment needed as a list"""
            if isinstance(self.equipment_needed, str):
                try:
                    return json.loads(self.equipment_needed)
                except:
                    return [self.equipment_needed] if self.equipment_needed else []
            return self.equipment_needed or []
        
        def set_equipment_needed(self, equipment_list):
            """Set equipment needed from a list"""
            self.equipment_needed = json.dumps(equipment_list) if equipment_list else None
    
    class WorkoutExercise(db.Model):
        """Junction table for exercises in training sessions with tracking data"""
        __tablename__ = 'workout_exercises'
        __table_args__ = {'extend_existing': True}
        
        id = db.Column(db.Integer, primary_key=True)
        training_session_id = db.Column(db.Integer, db.ForeignKey('training_sessions.id'), nullable=False)
        exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
        
        # Exercise tracking data
        sets = db.Column(db.Integer, default=0)
        reps = db.Column(db.Integer, default=0)
        weight = db.Column(db.Float, default=0.0)  # in kg or lbs
        duration = db.Column(db.Integer, default=0)  # in seconds
        distance = db.Column(db.Float, default=0.0)  # in meters/km
        rest_time = db.Column(db.Integer, default=0)  # rest between sets in seconds
        
        # Performance tracking
        difficulty_rating = db.Column(db.Integer)  # 1-10 scale
        form_rating = db.Column(db.Integer)  # 1-10 scale for form quality
        notes = db.Column(Text)
        
        # Exercise order in the workout
        order_in_workout = db.Column(db.Integer, default=0)
        
        # Timestamps
        started_at = db.Column(db.DateTime)
        completed_at = db.Column(db.DateTime)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        def to_dict(self):
            return {
                'id': self.id,
                'training_session_id': self.training_session_id,
                'exercise': self.exercise_ref.to_dict() if self.exercise_ref else None,
                'sets': self.sets,
                'reps': self.reps,
                'weight': self.weight,
                'duration': self.duration,
                'distance': self.distance,
                'rest_time': self.rest_time,
                'difficulty_rating': self.difficulty_rating,
                'form_rating': self.form_rating,
                'notes': self.notes,
                'order_in_workout': self.order_in_workout,
                'started_at': self.started_at.isoformat() if self.started_at else None,
                'completed_at': self.completed_at.isoformat() if self.completed_at else None,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }
        
        def calculate_volume(self):
            """Calculate training volume (sets x reps x weight)"""
            return self.sets * self.reps * self.weight if all([self.sets, self.reps, self.weight]) else 0
        
        def get_duration_formatted(self):
            """Get duration in readable format"""
            if not self.duration:
                return "0:00"
            
            minutes = self.duration // 60
            seconds = self.duration % 60
            return f"{minutes}:{seconds:02d}"
    
    return ExerciseCategory, MuscleGroup, Equipment, Exercise, WorkoutExercise