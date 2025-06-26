#!/usr/bin/env python3
"""
Database management utility for DojoTracker
Handles database operations, migrations, and data management
"""

import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def create_app_context():
    """Create Flask app context for database operations"""
    try:
        from app import create_app
        app = create_app()
        return app
    except ImportError as e:
        print(f"❌ Failed to import app: {e}")
        print("Make sure you're running this from the backend directory")
        sys.exit(1)

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"🗄️ {title}")
    print('='*60)

def print_step(step, success=True, details=None):
    """Print step result"""
    status = "✅" if success else "❌"
    print(f"{status} {step}")
    if details:
        print(f"   {details}")

def reset_database():
    """Reset the database (drop all tables and recreate)"""
    print_header("RESETTING DATABASE")
    
    app = create_app_context()
    
    with app.app_context():
        from app import db
        
        try:
            # Drop all tables
            print("🗑️ Dropping all tables...")
            db.drop_all()
            print_step("All tables dropped")
            
            # Recreate all tables
            print("🏗️ Creating all tables...")
            db.create_all()
            print_step("All tables created")
            
            print("\n✅ Database reset complete!")
            print("🔄 Run 'python seed_sample_data.py' to add sample data")
            
        except Exception as e:
            print_step("Database reset failed", False, str(e))
            return False
    
    return True

def inspect_database():
    """Inspect current database state"""
    print_header("DATABASE INSPECTION")
    
    app = create_app_context()
    
    with app.app_context():
        from app import db
        
        try:
            # Check if database file exists
            db_path = backend_dir / 'dojotracker.db'
            if db_path.exists():
                size_mb = db_path.stat().st_size / (1024 * 1024)
                print_step(f"Database file exists", True, f"Size: {size_mb:.2f} MB")
            else:
                print_step("Database file not found", False)
                return False
            
            # Get table information
            print("\n📊 TABLE INFORMATION:")
            
            # Users
            User = app.User
            user_count = User.query.count()
            print_step(f"Users: {user_count}")
            
            if user_count > 0:
                latest_user = User.query.order_by(User.created_at.desc()).first()
                print(f"   Latest: {latest_user.first_name} {latest_user.last_name} ({latest_user.email})")
            
            # Training Sessions
            TrainingSession = app.TrainingSession
            session_count = TrainingSession.query.count()
            print_step(f"Training Sessions: {session_count}")
            
            if session_count > 0:
                total_duration = db.session.query(db.func.sum(TrainingSession.duration)).scalar() or 0
                print(f"   Total training time: {total_duration} minutes ({total_duration/60:.1f} hours)")
            
            # Technique Library
            TechniqueLibrary = app.TechniqueLibrary
            technique_count = TechniqueLibrary.query.count()
            print_step(f"Technique Library: {technique_count}")
            
            if technique_count > 0:
                # Count by style
                styles = db.session.query(TechniqueLibrary.style, db.func.count(TechniqueLibrary.style)).group_by(TechniqueLibrary.style).all()
                print("   Styles:")
                for style, count in styles:
                    print(f"     • {style}: {count}")
                
                # Count by category
                categories = db.session.query(TechniqueLibrary.category, db.func.count(TechniqueLibrary.category)).group_by(TechniqueLibrary.category).all()
                print("   Categories:")
                for category, count in categories:
                    if category:
                        print(f"     • {category}: {count}")
            
            # Bookmarks
            UserTechniqueBookmark = app.UserTechniqueBookmark
            bookmark_count = UserTechniqueBookmark.query.count()
            print_step(f"Technique Bookmarks: {bookmark_count}")
            
            # Technique Progress
            TechniqueProgress = app.TechniqueProgress
            progress_count = TechniqueProgress.query.count()
            print_step(f"Technique Progress Records: {progress_count}")
            
            if progress_count > 0:
                # Count by mastery status
                mastery_stats = db.session.query(TechniqueProgress.mastery_status, db.func.count(TechniqueProgress.mastery_status)).group_by(TechniqueProgress.mastery_status).all()
                print("   Mastery Status:")
                for status, count in mastery_stats:
                    print(f"     • {status}: {count}")
            
        except Exception as e:
            print_step("Database inspection failed", False, str(e))
            return False
    
    return True

def backup_database():
    """Create a backup of the database"""
    print_header("DATABASE BACKUP")
    
    import shutil
    from datetime import datetime
    
    db_path = backend_dir / 'dojotracker.db'
    
    if not db_path.exists():
        print_step("Database file not found", False)
        return False
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"dojotracker_backup_{timestamp}.db"
    backup_path = backend_dir / backup_filename
    
    try:
        shutil.copy2(db_path, backup_path)
        print_step(f"Database backed up", True, f"Saved as: {backup_filename}")
        
        # Show backup size
        size_mb = backup_path.stat().st_size / (1024 * 1024)
        print(f"   Backup size: {size_mb:.2f} MB")
        
    except Exception as e:
        print_step("Backup failed", False, str(e))
        return False
    
    return True

def restore_database():
    """Restore database from backup"""
    print_header("DATABASE RESTORE")
    
    import glob
    
    # Find backup files
    backup_pattern = str(backend_dir / "dojotracker_backup_*.db")
    backup_files = glob.glob(backup_pattern)
    
    if not backup_files:
        print_step("No backup files found", False)
        return False
    
    # Show available backups
    print("📁 Available backups:")
    for i, backup_file in enumerate(sorted(backup_files, reverse=True)):
        filename = Path(backup_file).name
        size_mb = Path(backup_file).stat().st_size / (1024 * 1024)
        print(f"   {i+1}. {filename} ({size_mb:.2f} MB)")
    
    # Get user choice
    try:
        choice = input("\nEnter backup number to restore (or 'q' to quit): ").strip()
        if choice.lower() == 'q':
            return False
        
        backup_index = int(choice) - 1
        if backup_index < 0 or backup_index >= len(backup_files):
            print_step("Invalid choice", False)
            return False
        
        selected_backup = backup_files[backup_index]
        
        # Confirm restore
        confirm = input(f"⚠️ This will replace the current database. Continue? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Restore cancelled")
            return False
        
        # Perform restore
        import shutil
        db_path = backend_dir / 'dojotracker.db'
        
        # Backup current database first
        if db_path.exists():
            current_backup = backend_dir / f"dojotracker_pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2(db_path, current_backup)
            print_step(f"Current database backed up", True, f"Saved as: {current_backup.name}")
        
        # Restore from backup
        shutil.copy2(selected_backup, db_path)
        print_step("Database restored successfully", True, f"From: {Path(selected_backup).name}")
        
    except (ValueError, KeyboardInterrupt):
        print_step("Restore cancelled", False)
        return False
    except Exception as e:
        print_step("Restore failed", False, str(e))
        return False
    
    return True

def clean_test_data():
    """Clean up test data from database"""
    print_header("CLEANING TEST DATA")
    
    app = create_app_context()
    
    with app.app_context():
        from app import db
        
        try:
            User = app.User
            TrainingSession = app.TrainingSession
            UserTechniqueBookmark = app.UserTechniqueBookmark
            TechniqueProgress = app.TechniqueProgress
            
            # Find test users (emails containing 'test' or 'demo')
            test_users = User.query.filter(
                db.or_(
                    User.email.like('%test%'),
                    User.email.like('%demo%'),
                    User.email.like('%example.com%')
                )
            ).all()
            
            if not test_users:
                print_step("No test users found", True)
                return True
            
            print(f"📋 Found {len(test_users)} test users:")
            for user in test_users:
                print(f"   • {user.email}")
            
            # Confirm deletion
            confirm = input(f"\n⚠️ Delete these {len(test_users)} test users and their data? (y/N): ").strip().lower()
            if confirm != 'y':
                print("Cleanup cancelled")
                return False
            
            # Delete associated data
            deleted_sessions = 0
            deleted_bookmarks = 0
            deleted_progress = 0
            
            for user in test_users:
                # Delete training sessions
                sessions = TrainingSession.query.filter_by(user_id=user.id).all()
                for session in sessions:
                    db.session.delete(session)
                    deleted_sessions += 1
                
                # Delete bookmarks
                bookmarks = UserTechniqueBookmark.query.filter_by(user_id=user.id).all()
                for bookmark in bookmarks:
                    db.session.delete(bookmark)
                    deleted_bookmarks += 1
                
                # Delete technique progress
                progress_records = TechniqueProgress.query.filter_by(user_id=user.id).all()
                for progress in progress_records:
                    db.session.delete(progress)
                    deleted_progress += 1
                
                # Delete user
                db.session.delete(user)
            
            db.session.commit()
            
            print_step(f"Deleted {len(test_users)} test users", True)
            print_step(f"Deleted {deleted_sessions} training sessions", True)
            print_step(f"Deleted {deleted_bookmarks} bookmarks", True)
            print_step(f"Deleted {deleted_progress} progress records", True)
            
        except Exception as e:
            db.session.rollback()
            print_step("Cleanup failed", False, str(e))
            return False
    
    return True

def export_data():
    """Export database data to JSON"""
    print_header("EXPORTING DATA")
    
    app = create_app_context()
    
    with app.app_context():
        from app import db
        import json
        from datetime import datetime
        
        try:
            export_data = {
                'export_timestamp': datetime.utcnow().isoformat(),
                'users': [],
                'techniques': [],
                'training_sessions': [],
                'bookmarks': [],
                'technique_progress': []
            }
            
            # Export users (without passwords)
            User = app.User
            users = User.query.all()
            for user in users:
                user_data = user.to_dict()
                export_data['users'].append(user_data)
            
            # Export techniques
            TechniqueLibrary = app.TechniqueLibrary
            techniques = TechniqueLibrary.query.all()
            for technique in techniques:
                export_data['techniques'].append(technique.to_dict())
            
            # Export training sessions
            TrainingSession = app.TrainingSession
            sessions = TrainingSession.query.all()
            for session in sessions:
                export_data['training_sessions'].append(session.to_dict())
            
            # Export bookmarks
            UserTechniqueBookmark = app.UserTechniqueBookmark
            bookmarks = UserTechniqueBookmark.query.all()
            for bookmark in bookmarks:
                export_data['bookmarks'].append(bookmark.to_dict())
            
            # Export technique progress
            TechniqueProgress = app.TechniqueProgress
            progress_records = TechniqueProgress.query.all()
            for progress in progress_records:
                export_data['technique_progress'].append(progress.to_dict())
            
            # Save to file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_filename = f"dojotracker_export_{timestamp}.json"
            export_path = backend_dir / export_filename
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            # Show export statistics
            print_step("Data exported successfully", True, f"Saved as: {export_filename}")
            print(f"   📊 Users: {len(export_data['users'])}")
            print(f"   📊 Techniques: {len(export_data['techniques'])}")
            print(f"   📊 Training Sessions: {len(export_data['training_sessions'])}")
            print(f"   📊 Bookmarks: {len(export_data['bookmarks'])}")
            print(f"   📊 Progress Records: {len(export_data['technique_progress'])}")
            
            # Show file size
            size_mb = export_path.stat().st_size / (1024 * 1024)
            print(f"   📁 File size: {size_mb:.2f} MB")
            
        except Exception as e:
            print_step("Export failed", False, str(e))
            return False
    
    return True

def main():
    """Main function with command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='DojoTracker Database Manager')
    parser.add_argument('command', choices=[
        'inspect', 'reset', 'backup', 'restore', 'clean-test', 'export'
    ], help='Database operation to perform')
    
    args = parser.parse_args()
    
    print("🗄️ DojoTracker Database Manager")
    print("=" * 40)
    
    if args.command == 'inspect':
        inspect_database()
    elif args.command == 'reset':
        reset_database()
    elif args.command == 'backup':
        backup_database()
    elif args.command == 'restore':
        restore_database()
    elif args.command == 'clean-test':
        clean_test_data()
    elif args.command == 'export':
        export_data()

if __name__ == "__main__":
    main()