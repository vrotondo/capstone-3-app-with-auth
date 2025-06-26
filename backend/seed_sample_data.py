#!/usr/bin/env python3
"""
Fixed seed script for DojoTracker database.
Run this from the backend directory: python seed_sample_data.py
"""

import sys
import os
from datetime import datetime

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def seed_database():
    """Seed the database with sample techniques"""
    
    try:
        # Import Flask app
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            # Use the models that are already attached to the app
            TechniqueLibrary = app.TechniqueLibrary
            TechniqueCategory = app.TechniqueCategory
            
            # Get the database instance
            from app import db
            
            print("🥋 Starting to seed DojoTracker database...")
            
            # Clear existing data (optional)
            print("🗑️ Clearing existing techniques...")
            try:
                db.session.execute(db.text("DELETE FROM technique_library"))
                db.session.execute(db.text("DELETE FROM technique_categories"))
                db.session.commit()
                print("✅ Cleared existing data")
            except Exception as e:
                print(f"⚠️ Warning clearing data: {e}")
                db.session.rollback()
            
            # Create categories
            categories_data = [
                {'name': 'Kicks', 'description': 'Leg-based striking techniques'},
                {'name': 'Punches', 'description': 'Hand-based striking techniques'},
                {'name': 'Blocks', 'description': 'Defensive techniques'},
                {'name': 'Throws', 'description': 'Grappling and throwing techniques'},
                {'name': 'Strikes', 'description': 'Various striking techniques'}
            ]
            
            print("📂 Creating categories...")
            for cat_data in categories_data:
                try:
                    category = TechniqueCategory(
                        name=cat_data['name'],
                        description=cat_data['description']
                    )
                    db.session.add(category)
                except Exception as e:
                    print(f"⚠️ Error creating category {cat_data['name']}: {e}")
            
            db.session.commit()
            print(f"✅ Created categories")
            
            # Sample techniques with simpler structure
            techniques_data = [
                {
                    'name': 'Front Kick',
                    'style': 'Karate',
                    'category': 'Kicks',
                    'difficulty_level': 3,
                    'belt_level': 'White Belt',
                    'description': 'A basic straight kick delivered with the ball of the foot directly forward.',
                    'instructions': 'Start in fighting stance. Lift knee to chest height. Extend leg straight forward. Strike with ball of foot. Retract leg quickly.',
                    'tips': 'Keep your balance on the standing leg. Point your toes up to avoid injury.',
                    'source_site': 'DojoTracker',
                    'tags': ['basic', 'linear', 'striking'],
                    'view_count': 245,
                    'bookmark_count': 18
                },
                {
                    'name': 'Roundhouse Kick',
                    'style': 'Taekwondo',
                    'category': 'Kicks',
                    'difficulty_level': 5,
                    'belt_level': 'Yellow Belt',
                    'description': 'A circular kick delivered with the top of the foot in a sweeping motion.',
                    'instructions': 'Start in fighting stance. Pivot on supporting foot. Lift knee to the side. Snap leg in circular motion. Strike with top of foot.',
                    'tips': 'Pivot fully on the supporting foot for maximum power. Keep your guard up.',
                    'source_site': 'DojoTracker',
                    'tags': ['intermediate', 'circular', 'striking'],
                    'view_count': 189,
                    'bookmark_count': 25
                },
                {
                    'name': 'Jab',
                    'style': 'Boxing',
                    'category': 'Punches',
                    'difficulty_level': 2,
                    'belt_level': 'Beginner',
                    'description': 'A quick, straight punch thrown with the lead hand.',
                    'instructions': 'Start in boxing stance. Extend lead hand straight forward. Rotate fist palm down. Snap back to guard.',
                    'tips': 'Keep it quick and snappy. Don\'t overextend.',
                    'source_site': 'DojoTracker',
                    'tags': ['basic', 'boxing', 'fast'],
                    'view_count': 156,
                    'bookmark_count': 12
                },
                {
                    'name': 'Cross Punch',
                    'style': 'Boxing',
                    'category': 'Punches',
                    'difficulty_level': 3,
                    'belt_level': 'Beginner',
                    'description': 'A straight power punch thrown with the rear hand.',
                    'instructions': 'Start in boxing stance. Rotate hips and shoulders. Extend rear hand straight forward. Return to guard.',
                    'tips': 'Generate power from hips and legs. Keep front hand up.',
                    'source_site': 'DojoTracker',
                    'tags': ['power', 'boxing', 'straight'],
                    'view_count': 134,
                    'bookmark_count': 15
                },
                {
                    'name': 'Side Kick',
                    'style': 'Taekwondo',
                    'category': 'Kicks',
                    'difficulty_level': 6,
                    'belt_level': 'Green Belt',
                    'description': 'A powerful linear kick delivered with the edge of the foot to the side.',
                    'instructions': 'Turn body sideways to target. Lift knee up toward chest. Extend leg sideways. Strike with heel or blade of foot.',
                    'tips': 'Keep supporting leg slightly bent. Use hip thrust for power.',
                    'source_site': 'DojoTracker',
                    'tags': ['power', 'linear', 'side'],
                    'view_count': 167,
                    'bookmark_count': 22
                },
                {
                    'name': 'Rising Block',
                    'style': 'Karate',
                    'category': 'Blocks',
                    'difficulty_level': 3,
                    'belt_level': 'White Belt',
                    'description': 'An upward blocking motion to defend against overhead attacks.',
                    'instructions': 'Start with blocking arm down. Bring arm up in circular motion. End with forearm horizontal above forehead.',
                    'tips': 'Block with the outer edge of forearm. Don\'t lift shoulder.',
                    'source_site': 'DojoTracker',
                    'tags': ['defense', 'basic', 'upward'],
                    'view_count': 98,
                    'bookmark_count': 8
                },
                {
                    'name': 'Back Kick',
                    'style': 'Taekwondo',
                    'category': 'Kicks',
                    'difficulty_level': 7,
                    'belt_level': 'Blue Belt',
                    'description': 'A powerful kick delivered backwards with the heel.',
                    'instructions': 'Face away from target. Look over shoulder. Lift knee up. Drive heel straight back.',
                    'tips': 'Look over shoulder to aim. Drive with hip. Most powerful kick.',
                    'source_site': 'DojoTracker',
                    'tags': ['power', 'backward', 'heel'],
                    'view_count': 143,
                    'bookmark_count': 19
                },
                {
                    'name': 'Hook Punch',
                    'style': 'Boxing',
                    'category': 'Punches',
                    'difficulty_level': 4,
                    'belt_level': 'Intermediate',
                    'description': 'A circular punch targeting the side of the opponent.',
                    'instructions': 'Keep elbow bent at 90 degrees. Rotate body and hips. Swing arm in horizontal arc.',
                    'tips': 'Power comes from hip rotation. Keep elbow level with fist.',
                    'source_site': 'DojoTracker',
                    'tags': ['circular', 'power', 'boxing'],
                    'view_count': 121,
                    'bookmark_count': 14
                },
                {
                    'name': 'Uppercut',
                    'style': 'Boxing',
                    'category': 'Punches',
                    'difficulty_level': 5,
                    'belt_level': 'Intermediate',
                    'description': 'An upward punch targeting the chin or solar plexus.',
                    'instructions': 'Drop punching hand slightly. Bend knees and drop body level. Drive up with legs. Punch upward.',
                    'tips': 'Power comes from legs and hips. Stay close to opponent.',
                    'source_site': 'DojoTracker',
                    'tags': ['upward', 'close-range', 'power'],
                    'view_count': 109,
                    'bookmark_count': 11
                },
                {
                    'name': 'Hip Throw',
                    'style': 'Judo',
                    'category': 'Throws',
                    'difficulty_level': 8,
                    'belt_level': 'Brown Belt',
                    'description': 'A fundamental throwing technique using hip placement and leverage.',
                    'instructions': 'Grip opponent properly. Step in close. Turn and place hip under opponent center. Lift and rotate.',
                    'tips': 'Get close before attempting. Use proper grips. Practice with experienced partner.',
                    'source_site': 'DojoTracker',
                    'tags': ['grappling', 'leverage', 'advanced'],
                    'view_count': 87,
                    'bookmark_count': 16
                }
            ]
            
            print("🥋 Creating sample techniques...")
            created_count = 0
            
            for tech_data in techniques_data:
                try:
                    technique = TechniqueLibrary(
                        name=tech_data['name'],
                        style=tech_data['style'],
                        category=tech_data.get('category'),
                        difficulty_level=tech_data.get('difficulty_level'),
                        belt_level=tech_data.get('belt_level'),
                        description=tech_data.get('description'),
                        instructions=tech_data.get('instructions'),
                        tips=tech_data.get('tips'),
                        source_site=tech_data.get('source_site', 'DojoTracker'),
                        tags=tech_data.get('tags', []),
                        view_count=tech_data.get('view_count', 0),
                        bookmark_count=tech_data.get('bookmark_count', 0)
                    )
                    db.session.add(technique)
                    created_count += 1
                    print(f"  ✅ Added: {tech_data['name']} ({tech_data['style']})")
                except Exception as e:
                    print(f"  ❌ Error adding {tech_data['name']}: {e}")
            
            # Commit all techniques
            db.session.commit()
            
            print(f"\n🎉 Successfully created {created_count} sample techniques!")
            
            # Verify the data
            try:
                total_techniques = db.session.execute(db.text("SELECT COUNT(*) FROM technique_library")).scalar()
                total_categories = db.session.execute(db.text("SELECT COUNT(*) FROM technique_categories")).scalar()
                
                print(f"\n📊 Database Summary:")
                print(f"   • Total techniques: {total_techniques}")
                print(f"   • Categories: {total_categories}")
                
                if total_techniques > 0:
                    print("\n🚀 Success! Your database now has sample techniques.")
                    print("   You can test the technique library at: http://localhost:3000/techniques")
                else:
                    print("\n⚠️ Warning: No techniques were created.")
                    
            except Exception as e:
                print(f"⚠️ Could not verify data: {e}")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the backend directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    print("🥋 DojoTracker Database Seeder (Fixed Version)")
    print("=" * 50)
    seed_database()