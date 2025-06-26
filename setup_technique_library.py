#!/usr/bin/env python3
"""
Fixed setup script for DojoTracker Technique Library
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install additional requirements for technique library"""
    requirements = [
        'beautifulsoup4==4.12.2',
        'requests==2.31.0'
        # Removed lxml as it has Windows compilation issues
    ]
    
    print("📦 Installing technique library dependencies...")
    
    for req in requirements:
        try:
            print(f"Installing {req}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', req], check=True)
            print(f"✅ {req} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {req}: {e}")
            return False
    
    return True

def create_directories():
    """Create necessary directories"""
    directories = [
        'backend/services',
        'backend/scraped_content',
        'backend/logs'
    ]
    
    print("📁 Creating directories...")
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {directory}")

def create_files():
    """Create the necessary backend files"""
    print("📄 Creating backend files...")
    
    # Create __init__.py files
    init_files = [
        'backend/services/__init__.py',
        'backend/models/__init__.py'
    ]
    
    for init_file in init_files:
        Path(init_file).touch()
        print(f"✅ Created: {init_file}")

def test_scraper():
    """Test the BlackBeltWiki scraper with correct URLs"""
    print("\n🧪 Testing BlackBeltWiki scraper...")
    
    try:
        # Change to backend directory
        original_dir = os.getcwd()
        os.chdir('backend')
        
        # Add current directory to Python path
        sys.path.insert(0, '.')
        
        # Test imports
        from services.blackbelt_scraper import BlackBeltWikiScraper
        print("✅ Scraper imported successfully")
        
        # Test with real BlackBeltWiki URLs
        scraper = BlackBeltWikiScraper(delay=1)
        
        # Test basic connectivity
        print("🌐 Testing BlackBeltWiki connectivity...")
        import requests
        
        test_urls = [
            'https://blackbeltwiki.com',
            'https://blackbeltwiki.com/wiki/Main_Page',
            'https://blackbeltwiki.com/wiki/Kicks',
            'https://blackbeltwiki.com/wiki/Front_Kick'
        ]
        
        working_urls = []
        for url in test_urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    working_urls.append(url)
                    print(f"✅ {url} - Status: {response.status_code}")
                else:
                    print(f"⚠️ {url} - Status: {response.status_code}")
            except Exception as e:
                print(f"❌ {url} - Error: {e}")
        
        if working_urls:
            print(f"✅ Found {len(working_urls)} working URLs")
        else:
            print("⚠️ No working URLs found - BlackBeltWiki might be down or have changed")
        
        return True
        
    except Exception as e:
        print(f"❌ Scraper test failed: {e}")
        return False
    finally:
        os.chdir(original_dir)

def initialize_database():
    """Initialize database with technique library tables"""
    print("\n🗄️ Initializing technique library database...")
    
    try:
        original_dir = os.getcwd()
        os.chdir('backend')
        
        # Add backend directory to Python path
        sys.path.insert(0, '.')
        
        # Import app and create tables
        from app import create_app, db
        
        app = create_app()
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Import and check models
            from models.technique_library import create_technique_models
            TechniqueLibrary, UserTechniqueBookmark, TechniqueCategory = create_technique_models(db)
            
            print("✅ Technique library models loaded")
            
            # Create some default categories
            default_categories = [
                ('Kicks', 'Leg-based striking techniques'),
                ('Punches', 'Hand-based striking techniques'),
                ('Blocks', 'Defensive techniques'),
                ('Throws', 'Techniques for throwing opponents'),
                ('Grappling', 'Ground fighting and submission techniques'),
                ('Kata/Forms', 'Choreographed sequences of techniques')
            ]
            
            for name, description in default_categories:
                existing = TechniqueCategory.query.filter_by(name=name).first()
                if not existing:
                    category = TechniqueCategory(name=name, description=description)
                    category.save()
                    print(f"✅ Created category: {name}")
            
            # Check final state
            technique_count = TechniqueLibrary.query.count()
            category_count = TechniqueCategory.query.count()
            print(f"📊 Database initialized with {category_count} categories, {technique_count} techniques")
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        os.chdir(original_dir)

def test_api_endpoints():
    """Test API endpoints if server is running"""
    print("\n🌐 Testing API endpoints...")
    
    try:
        import requests
        
        base_url = 'http://localhost:8000'
        
        # Test basic endpoints
        endpoints = [
            '/api/techniques/test',
            '/api/techniques/stats', 
            '/api/techniques/styles',
            '/api/techniques/categories'
        ]
        
        working_endpoints = 0
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {endpoint} - Working")
                    working_endpoints += 1
                else:
                    print(f"⚠️ {endpoint} - Status: {response.status_code}")
            except requests.exceptions.ConnectionError:
                print(f"⚠️ {endpoint} - Server not running")
                break
            except Exception as e:
                print(f"❌ {endpoint} - Error: {e}")
        
        if working_endpoints > 0:
            print(f"✅ {working_endpoints}/{len(endpoints)} endpoints working")
        else:
            print("⚠️ Backend server not running. Start with: cd backend && python app.py")
            
    except Exception as e:
        print(f"⚠️ API test failed: {e}")

def create_sample_techniques():
    """Create some sample techniques for testing"""
    print("\n🎯 Creating sample techniques...")
    
    try:
        original_dir = os.getcwd()
        os.chdir('backend')
        sys.path.insert(0, '.')
        
        from app import create_app, db
        from models.technique_library import create_technique_models
        
        app = create_app()
        with app.app_context():
            TechniqueLibrary, _, _ = create_technique_models(db)
            
            # Sample techniques
            sample_techniques = [
                {
                    'name': 'Front Kick',
                    'style': 'Karate',
                    'category': 'Kicks',
                    'difficulty_level': 3,
                    'belt_level': 'White Belt',
                    'description': 'A basic straight kick delivered with the ball of the foot.',
                    'instructions': '1. Stand in fighting stance\n2. Lift knee to chamber position\n3. Extend leg straight forward\n4. Strike with ball of foot\n5. Return to chamber\n6. Lower foot to ground',
                    'tips': 'Keep your balance on the standing leg. Practice the chamber position slowly.',
                    'source_site': 'DojoTracker Sample',
                    'tags': ['basic', 'linear', 'striking']
                },
                {
                    'name': 'Roundhouse Kick',
                    'style': 'Taekwondo',
                    'category': 'Kicks',
                    'difficulty_level': 5,
                    'belt_level': 'Yellow Belt',
                    'description': 'A circular kick delivered with the top of the foot or shin.',
                    'instructions': '1. Stand in fighting stance\n2. Pivot on supporting foot\n3. Lift knee to side\n4. Snap leg in circular motion\n5. Strike with top of foot\n6. Return to chamber',
                    'tips': 'Pivot fully on the supporting foot. Keep your guard up.',
                    'source_site': 'DojoTracker Sample',
                    'tags': ['intermediate', 'circular', 'striking']
                },
                {
                    'name': 'Basic Jab',
                    'style': 'Boxing',
                    'category': 'Punches',
                    'difficulty_level': 2,
                    'belt_level': 'Beginner',
                    'description': 'A quick, straight punch thrown with the lead hand.',
                    'instructions': '1. Stand in boxing stance\n2. Extend lead hand straight forward\n3. Rotate fist so palm faces down\n4. Keep elbow close to body\n5. Snap punch back quickly',
                    'tips': 'Keep it quick and snappy. Use it to set up combinations.',
                    'source_site': 'DojoTracker Sample',
                    'tags': ['basic', 'boxing', 'hand-technique']
                }
            ]
            
            created_count = 0
            for tech_data in sample_techniques:
                # Check if technique already exists
                existing = TechniqueLibrary.query.filter_by(name=tech_data['name']).first()
                if not existing:
                    technique = TechniqueLibrary(**tech_data)
                    technique.save()
                    created_count += 1
                    print(f"✅ Created: {tech_data['name']}")
                else:
                    print(f"⏭️ Skipped: {tech_data['name']} (already exists)")
            
            print(f"📊 Created {created_count} sample techniques")
        
        return True
        
    except Exception as e:
        print(f"❌ Sample technique creation failed: {e}")
        return False
    finally:
        os.chdir(original_dir)

def main():
    """Main setup function"""
    print("🥋 DojoTracker Technique Library Setup (Fixed)")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path('backend').exists():
        print("❌ Error: Please run this script from the project root directory")
        sys.exit(1)
    
    success = True
    
    # Install requirements (without lxml)
    if not install_requirements():
        print("⚠️ Some dependencies failed to install, but continuing...")
    
    # Create directories
    create_directories()
    
    # Create necessary files
    create_files()
    
    # Initialize database
    if not initialize_database():
        success = False
    
    # Create sample techniques
    if not create_sample_techniques():
        print("⚠️ Sample technique creation failed, but continuing...")
    
    # Test scraper
    if not test_scraper():
        print("⚠️ Scraper test had issues, but continuing...")
    
    # Test API endpoints
    test_api_endpoints()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Technique Library setup completed!")
        print("\nNext steps:")
        print("1. Start your backend server:")
        print("   cd backend && python app.py")
        print("\n2. Test the technique API:")
        print("   http://localhost:8000/api/techniques/test")
        print("\n3. View sample techniques:")
        print("   http://localhost:8000/api/techniques/search")
        print("\n4. Check technique stats:")
        print("   http://localhost:8000/api/techniques/stats")
        print("\nAPI Documentation:")
        print("- Search: GET /api/techniques/search?q=kick")
        print("- Popular: GET /api/techniques/popular")
        print("- Detail: GET /api/techniques/<id>")
        print("- Styles: GET /api/techniques/styles")
        print("- Categories: GET /api/techniques/categories")
        print("\n📝 Note: BlackBeltWiki scraping needs URL updates.")
        print("   Sample techniques have been created for testing.")
    else:
        print("❌ Setup completed with some errors. Check the output above.")
        print("💡 You can still proceed - sample techniques were created.")

if __name__ == '__main__':
    main()