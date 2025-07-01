from datetime import datetime
import json

def create_workout_models(db):
    """Factory function to create workout models with provided db instance"""
    
    class FavoriteExercise(db.Model):
        """User's favorite exercises"""
        __tablename__ = 'favorite_exercises'
        
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
        exercise_id = db.Column(db.Integer, nullable=False)  # WGER exercise ID
        exercise_name = db.Column(db.String(255))  # Cached exercise name
        exercise_category = db.Column(db.String(100))  # Cached category
        exercise_muscles = db.Column(db.Text)  # JSON string of muscles
        exercise_equipment = db.Column(db.Text)  # JSON string of equipment
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        # Relationship
        user = db.relationship('User', backref='favorite_exercises')
        
        # Unique constraint - user can only favorite an exercise once
        __table_args__ = (db.UniqueConstraint('user_id', 'exercise_id', name='unique_user_exercise'),)
        
        def to_dict(self):
            return {
                'id': self.id,
                'exercise_id': self.exercise_id,
                'exercise_name': self.exercise_name,
                'exercise_category': self.exercise_category,
                'exercise_muscles': json.loads(self.exercise_muscles) if self.exercise_muscles else [],
                'exercise_equipment': json.loads(self.exercise_equipment) if self.exercise_equipment else [],
                'created_at': self.created_at.isoformat()
            }

    class WorkoutPlan(db.Model):
        """User's workout plans"""
        __tablename__ = 'workout_plans'
        
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
        name = db.Column(db.String(255), nullable=False)
        description = db.Column(db.Text)
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        # Relationships
        user = db.relationship('User', backref='workout_plans')
        exercises = db.relationship('WorkoutPlanExercise', backref='workout_plan', cascade='all, delete-orphan')
        
        def to_dict(self):
            return {
                'id': self.id,
                'name': self.name,
                'description': self.description,
                'is_active': self.is_active,
                'exercise_count': len(self.exercises),
                'exercises': [exercise.to_dict() for exercise in self.exercises],
                'created_at': self.created_at.isoformat(),
                'updated_at': self.updated_at.isoformat()
            }

    class WorkoutPlanExercise(db.Model):
        """Exercises within a workout plan"""
        __tablename__ = 'workout_plan_exercises'
        
        id = db.Column(db.Integer, primary_key=True)
        workout_plan_id = db.Column(db.Integer, db.ForeignKey('workout_plans.id'), nullable=False)
        exercise_id = db.Column(db.Integer, nullable=False)  # WGER exercise ID
        exercise_name = db.Column(db.String(255))  # Cached exercise name
        exercise_category = db.Column(db.String(100))  # Cached category
        exercise_muscles = db.Column(db.Text)  # JSON string of muscles
        exercise_equipment = db.Column(db.Text)  # JSON string of equipment
        
        # Workout-specific data
        sets = db.Column(db.Integer, default=3)
        reps = db.Column(db.String(50), default='10-12')  # Can be "10-12" or "30 seconds" etc
        rest_seconds = db.Column(db.Integer, default=60)
        notes = db.Column(db.Text)
        order_in_workout = db.Column(db.Integer, default=0)  # Order of exercise in workout
        
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        def to_dict(self):
            return {
                'id': self.id,
                'exercise_id': self.exercise_id,
                'exercise_name': self.exercise_name,
                'exercise_category': self.exercise_category,
                'exercise_muscles': json.loads(self.exercise_muscles) if self.exercise_muscles else [],
                'exercise_equipment': json.loads(self.exercise_equipment) if self.exercise_equipment else [],
                'sets': self.sets,
                'reps': self.reps,
                'rest_seconds': self.rest_seconds,
                'notes': self.notes,
                'order_in_workout': self.order_in_workout,
                'created_at': self.created_at.isoformat()
            }
    
    return FavoriteExercise, WorkoutPlan, WorkoutPlanExercise