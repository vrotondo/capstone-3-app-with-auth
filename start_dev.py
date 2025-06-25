#!/usr/bin/env python3
"""
DojoTracker Development Startup Script
This script helps you start both the frontend and backend development servers
"""

import os
import sys
import subprocess
import time
import threading
from pathlib import Path

def run_backend():
    """Start the Flask backend server"""
    print("🔧 Starting Flask backend server...")
    
    try:
        # Change to backend directory
        os.chdir('backend')
        
        # Start Flask server
        subprocess.run([sys.executable, 'app.py'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Backend server failed: {e}")
    except Exception as e:
        print(f"❌ Backend error: {e}")

def run_frontend():
    """Start the React frontend server"""
    print("⚛️ Starting React frontend server...")
    
    try:
        # Change to frontend directory
        os.chdir('frontend')
        
        # Check if node_modules exists
        if not Path('node_modules').exists():
            print("📦 Installing frontend dependencies...")
            subprocess.run(['npm', 'install'], check=True)
        
        # Start React development server
        subprocess.run(['npm', 'run', 'dev'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Frontend server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Frontend server failed: {e}")
    except Exception as e:
        print(f"❌ Frontend error: {e}")

def check_requirements():
    """Check if required tools are installed"""
    print("🔍 Checking requirements...")
    
    # Check Python
    try:
        python_version = subprocess.run([sys.executable, '--version'], 
                                      capture_output=True, text=True)
        print(f"✅ Python: {python_version.stdout.strip()}")
    except:
        print("❌ Python not found")
        return False
    
    # Check Node.js
    try:
        node_version = subprocess.run(['node', '--version'], 
                                    capture_output=True, text=True)
        print(f"✅ Node.js: {node_version.stdout.strip()}")
    except:
        print("❌ Node.js not found. Please install Node.js from https://nodejs.org/")
        return False
    
    # Check npm
    try:
        npm_version = subprocess.run(['npm', '--version'], 
                                   capture_output=True, text=True)
        print(f"✅ npm: {npm_version.stdout.strip()}")
    except:
        print("❌ npm not found")
        return False
    
    return True

def main():
    print("🥋 DojoTracker Development Server Startup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path('backend').exists() or not Path('frontend').exists():
        print("❌ Error: Please run this script from the project root directory")
        print("Expected structure:")
        print("  - backend/")
        print("  - frontend/")
        sys.exit(1)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Missing requirements. Please install the required tools.")
        sys.exit(1)
    
    print("\n🚀 Starting development servers...")
    print("Backend will run on: http://localhost:8000")
    print("Frontend will run on: http://localhost:3000")
    print("\nPress Ctrl+C to stop both servers\n")
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Give backend time to start
    time.sleep(3)
    
    # Start frontend (this will block until stopped)
    try:
        run_frontend()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down development servers...")
        print("✅ Servers stopped successfully")

if __name__ == '__main__':
    main()