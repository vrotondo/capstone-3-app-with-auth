# Create this file: backend/reset_database.py

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def reset_database():
    """Reset the database with the new schema"""
    
    # Initialize Flask app and database
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dojotracker.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db = SQLAlchemy()
    db.init_app(app)
    
    with app.app_context():
        print("🗑️ Removing old database...")
        
        # Remove the old database file
        db_path = 'dojotracker.db'
        if os.path.exists(db_path):
            os.remove(db_path)
            print("✅ Old database removed")
        else:
            print("ℹ️ No existing database found")
        
        # Import models to register them with SQLAlchemy
        print("📦 Loading models...")
        from models.user import create_models
        from models.technique_library import create_technique_models
        
        # Create user models
        User, TrainingSession, TechniqueProgress, UserPreferences = create_models(db)
        
        # Create technique models  
        TechniqueLibrary, UserTechniqueBookmark, TechniqueCategory = create_technique_models(db)
        
        print("🔨 Creating new database with updated schema...")
        
        # Create all tables with the new schema
        db.create_all()
        
        print("✅ Database reset complete!")
        print("🎯 New schema includes:")
        print("   - User: bio, location, date_of_birth, primary_style, belt_rank, years_training, instructor, dojo, goals")
        print("   - TrainingSession: enhanced training tracking")
        print("   - TechniqueProgress: technique mastery tracking")
        print("   - UserPreferences: user preferences")
        print("   - TechniqueLibrary: technique database")
        print("")
        print("🔄 You can now restart your app with: python app.py")

if __name__ == '__main__':
    reset_database()