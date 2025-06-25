#!/usr/bin/env python3
"""
Database reset script for DojoTracker
Run this to recreate the database with the correct schema
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

def reset_database():
    """Reset the database with fresh schema"""
    try:
        # Change to backend directory
        os.chdir('backend')
        
        # Import after changing directory
        from app import create_app, db
        from models.user import User
        from models.training import TrainingSession, TechniqueProgress
        
        print("🗄️ Resetting database...")
        
        # Create app context
        app = create_app()
        with app.app_context():
            # Drop all tables
            print("Dropping existing tables...")
            db.drop_all()
            
            # Create all tables
            print("Creating new tables...")
            db.create_all()
            
            print("✅ Database reset successfully!")
            print("\nYou can now:")
            print("1. Start your Flask server: python app.py")
            print("2. Test registration and login")
            
    except Exception as e:
        print(f"❌ Error resetting database: {str(e)}")
        print("Make sure you're in the project root directory")

if __name__ == '__main__':
    reset_database()