#!/usr/bin/env python3
"""
DojoTracker Development Setup Script
Run this script to set up your development environment
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a shell command and print the result"""
    print(f"\n📋 {description}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ Success: {description}")
        if result.stdout:
            print(f"Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {description}")
        print(f"Error output: {e.stderr}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists():
        if env_example.exists():
            print("\n📄 Creating .env file from .env.example")
            env_file.write_text(env_example.read_text())
            print("✅ .env file created")
            print("🔧 Please edit .env file with your actual configuration values")
        else:
            print("\n📄 Creating basic .env file")
            env_content = """# Flask Configuration
FLASK_APP=backend/app.py
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production

# Database (SQLite for development)
SQLALCHEMY_DATABASE_URI=sqlite:///dojotracker.db

# JWT
JWT_SECRET_KEY=jwt-secret-change-in-production

# External APIs (add your keys here)
FITBIT_CLIENT_ID=your-fitbit-client-id
FITBIT_CLIENT_SECRET=your-fitbit-client-secret
WGER_API_KEY=your-wger-api-key
"""
            env_file.write_text(env_content)
            print("✅ Basic .env file created")
    else:
        print("✅ .env file already exists")

def main():
    print("🥋 DojoTracker Development Setup")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path('backend').exists():
        print("❌ Error: backend directory not found")
        print("Please run this script from the project root directory")
        sys.exit(1)
    
    # Change to backend directory
    os.chdir('backend')
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Error: Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {python_version.major}.{python_version.minor} detected")
    
    # Create virtual environment
    if not Path('venv').exists():
        success = run_command('python -m venv venv', 'Creating virtual environment')
        if not success:
            sys.exit(1)
    else:
        print("✅ Virtual environment already exists")
    
    # Determine activation command based on OS
    if os.name == 'nt':  # Windows
        activate_cmd = 'venv\\Scripts\\activate'
        pip_cmd = 'venv\\Scripts\\pip'
        python_cmd = 'venv\\Scripts\\python'
    else:  # Mac/Linux
        activate_cmd = 'source venv/bin/activate'
        pip_cmd = 'venv/bin/pip'
        python_cmd = 'venv/bin/python'
    
    # Install requirements
    success = run_command(f'{pip_cmd} install -r requirements.txt', 'Installing Python dependencies')
    if not success:
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Go back to project root
    os.chdir('..')
    
    # Create .env file
    create_env_file()
    
    # Initialize database
    os.chdir('backend')
    success = run_command(f'{python_cmd} -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print(\'Database initialized\')"', 'Initializing database')
    
    if success:
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit the .env file with your API keys")
        print("2. Start the development server:")
        print(f"   cd backend")
        if os.name == 'nt':
            print(f"   venv\\Scripts\\activate")
        else:
            print(f"   source venv/bin/activate")
        print(f"   python app.py")
        print("\n3. Test the API at http://localhost:5000")
        print("4. Create the React frontend")
    else:
        print("❌ Setup encountered errors. Please check the output above.")

if __name__ == '__main__':
    main()