#!/usr/bin/env python3
"""
Quick script to restart the DojoTracker backend with database reset
Windows compatible version
"""

import os
import sys
import subprocess
from pathlib import Path

def restart_backend():
    """Restart the backend with a fresh database"""
    print("🥋 DojoTracker Backend Restart")
    print("=" * 40)
    
    # Change to backend directory
    if not Path('backend').exists():
        print("❌ Error: Run this from the project root directory")
        sys.exit(1)
    
    os.chdir('backend')
    
    # Remove old database file
    db_file = Path('dojotracker.db')
    if db_file.exists():
        print("🗑️ Removing old database...")
        try:
            db_file.unlink()
            print("✅ Old database removed")
        except Exception as e:
            print(f"⚠️ Could not remove database: {e}")
    
    # Remove old training.py if it exists
    old_training = Path('models/training.py')
    if old_training.exists():
        print("🗑️ Removing old training.py...")
        try:
            old_training.unlink()
            print("✅ Old training.py removed")
        except Exception as e:
            print(f"⚠️ Could not remove training.py: {e}")
    
    print("\n🚀 Starting fresh backend server...")
    print("📍 Backend will run on: http://localhost:8000")
    print("🔗 Frontend should connect to: http://localhost:8000/api")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 40)
    
    # Start the backend
    try:
        subprocess.run([sys.executable, 'app.py'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Backend failed to start: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    restart_backend()