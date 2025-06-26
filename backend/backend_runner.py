#!/usr/bin/env python3
"""
Fixed backend-only runner for DojoTracker
Handles setup, seeding, testing, and running just the backend API
"""

import os
import sys
import subprocess
import time
import requests
import json
from pathlib import Path

class DojoTrackerBackendRunner:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.backend_url = 'http://localhost:8000'
    
    def print_header(self, title):
        """Print formatted header"""
        print(f"\n{'='*60}")
        print(f"🥋 {title}")
        print('='*60)
    
    def print_step(self, step, success=True, details=None):
        """Print step result"""
        status = "✅" if success else "❌"
        print(f"{status} {step}")
        if details:
            print(f"   {details}")
    
    def run_command(self, command, cwd=None, shell=False):
        """Run a system command"""
        try:
            if isinstance(command, str) and not shell:
                command = command.split()
            
            result = subprocess.run(
                command,
                cwd=cwd or self.base_dir,
                capture_output=True,
                text=True,
                shell=shell
            )
            
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def check_requirements(self):
        """Check if required tools are installed (Python only)"""
        self.print_header("CHECKING BACKEND REQUIREMENTS")
        
        # Check Python
        success, stdout, stderr = self.run_command("python --version")
        if success:
            version = stdout.strip()
            self.print_step(f"Python: {version}", True)
        else:
            self.print_step("Python not found", False)
            return False
        
        # Check pip
        success, stdout, stderr = self.run_command("python -m pip --version")
        if success:
            version = stdout.strip().split()[1]
            self.print_step(f"pip: {version}", True)
        else:
            self.print_step("pip not found", False)
            return False
        
        return True
    
    def setup_backend(self):
        """Set up backend environment"""
        self.print_header("BACKEND SETUP")
        
        # Check if virtual environment exists
        venv_dir = self.base_dir / 'venv'
        if not venv_dir.exists():
            self.print_step("Creating virtual environment...")
            success, stdout, stderr = self.run_command("python -m venv venv")
            if not success:
                self.print_step("Failed to create virtual environment", False, stderr)
                return False
            self.print_step("Virtual environment created", True)
        else:
            self.print_step("Virtual environment exists", True)
        
        # Install requirements
        if os.name == 'nt':  # Windows
            pip_cmd = str(venv_dir / 'Scripts' / 'pip')
            python_cmd = str(venv_dir / 'Scripts' / 'python')
        else:  # Unix/Linux/Mac
            pip_cmd = str(venv_dir / 'bin' / 'pip')
            python_cmd = str(venv_dir / 'bin' / 'python')
        
        self.print_step("Installing Python dependencies...")
        success, stdout, stderr = self.run_command(f'"{pip_cmd}" install -r requirements.txt')
        if success:
            self.print_step("Python dependencies installed", True)
        else:
            self.print_step("Failed to install Python dependencies", False, stderr)
            return False
        
        return True
    
    def setup_database(self):
        """Set up and seed database"""
        self.print_header("DATABASE SETUP")
        
        # Get Python command from virtual environment
        venv_dir = self.base_dir / 'venv'
        if os.name == 'nt':  # Windows
            python_cmd = str(venv_dir / 'Scripts' / 'python')
        else:  # Unix/Linux/Mac
            python_cmd = str(venv_dir / 'bin' / 'python')
        
        self.print_step("Seeding database with sample data...")
        success, stdout, stderr = self.run_command(f'"{python_cmd}" seed_sample_data.py')
        if success:
            self.print_step("Database seeded successfully", True)
            if stdout:
                print(stdout)
        else:
            self.print_step("Database seeding failed", False, stderr)
            return False
        
        return True
    
    def start_backend(self):
        """Start the backend server"""
        self.print_header("STARTING BACKEND SERVER")
        
        venv_dir = self.base_dir / 'venv'
        if os.name == 'nt':  # Windows
            python_cmd = str(venv_dir / 'Scripts' / 'python')
        else:  # Unix/Linux/Mac
            python_cmd = str(venv_dir / 'bin' / 'python')
        
        print("🚀 Starting backend server...")
        print(f"📍 Backend will be available at: {self.backend_url}")
        print("📍 API endpoints at: {self.backend_url}/api")
        print("⚠️ Press Ctrl+C to stop the server")
        
        try:
            # Start backend server
            result = subprocess.run(
                f'"{python_cmd}" app.py',
                shell=True
            )
        except KeyboardInterrupt:
            print("\n⏹️ Backend server stopped")
        
        return True
    
    def test_backend_health(self):
        """Test if backend is healthy"""
        try:
            response = requests.get(f"{self.backend_url}/api/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def run_api_tests(self):
        """Run comprehensive API tests"""
        self.print_header("RUNNING API TESTS")
        
        # Wait for backend to be ready
        print("⏳ Waiting for backend to be ready...")
        for i in range(30):
            if self.test_backend_health():
                self.print_step("Backend is ready", True)
                break
            time.sleep(1)
        else:
            self.print_step("Backend not responding", False)
            print("💡 Make sure the backend is running with: python backend_runner.py start")
            return False
        
        # Run test script
        venv_dir = self.base_dir / 'venv'
        if os.name == 'nt':  # Windows
            python_cmd = str(venv_dir / 'Scripts' / 'python')
        else:  # Unix/Linux/Mac
            python_cmd = str(venv_dir / 'bin' / 'python')
        
        self.print_step("Running comprehensive API tests...")
        success, stdout, stderr = self.run_command(f'"{python_cmd}" comprehensive_api_test.py')
        
        if success:
            self.print_step("API tests completed", True)
            print(stdout)
        else:
            self.print_step("API tests failed", False, stderr)
        
        return success
    
    def import_sample_techniques(self):
        """Import sample techniques from BlackBeltWiki"""
        self.print_header("IMPORTING SAMPLE TECHNIQUES")
        
        # Wait for backend to be ready
        if not self.test_backend_health():
            self.print_step("Backend not ready", False)
            print("💡 Start the backend first with: python backend_runner.py start")
            return False
        
        # Create a test user first (for import permissions)
        try:
            # Register test user
            user_data = {
                'email': 'admin@dojotracker.test',
                'password': 'admin123',
                'first_name': 'Admin',
                'last_name': 'User',
                'martial_art': 'Mixed',
                'current_belt': 'Black Belt'
            }
            
            register_response = requests.post(f"{self.backend_url}/api/auth/register", json=user_data)
            if register_response.status_code == 201:
                token = register_response.json().get('token')
                
                # Import techniques
                import_data = {
                    'source': 'blackbeltwiki',
                    'max_techniques': 10
                }
                
                headers = {'Authorization': f'Bearer {token}'}
                import_response = requests.post(
                    f"{self.backend_url}/api/techniques/import",
                    json=import_data,
                    headers=headers
                )
                
                if import_response.status_code == 200:
                    result = import_response.json()
                    import_result = result.get('import_result', {})
                    self.print_step("Techniques imported successfully", True,
                                  f"Imported: {import_result.get('imported', 0)}, Updated: {import_result.get('updated', 0)}")
                else:
                    self.print_step("Technique import failed", False, f"Status: {import_response.status_code}")
            else:
                self.print_step("Failed to create admin user", False, f"Status: {register_response.status_code}")
                
        except Exception as e:
            self.print_step("Import failed", False, str(e))
            return False
        
        return True
    
    def show_status(self):
        """Show current status of backend service"""
        self.print_header("BACKEND STATUS")
        
        # Check backend
        if self.test_backend_health():
            self.print_step(f"Backend running at {self.backend_url}", True)
            
            # Get some stats
            try:
                response = requests.get(f"{self.backend_url}/api/techniques/stats")
                if response.status_code == 200:
                    stats = response.json().get('stats', {})
                    print(f"   📊 Techniques: {stats.get('total_techniques', 0)}")
                    print(f"   🥋 Styles: {stats.get('total_styles', 0)}")
                    print(f"   📚 Categories: {stats.get('total_categories', 0)}")
            except:
                pass
        else:
            self.print_step("Backend not running", False)
            print("💡 Start with: python backend_runner.py start")
    
    def full_setup(self):
        """Complete backend setup from scratch"""
        self.print_header("FULL BACKEND SETUP")
        
        # Check requirements
        if not self.check_requirements():
            print("❌ Requirements check failed. Please install missing dependencies.")
            return False
        
        # Setup backend
        if not self.setup_backend():
            print("❌ Backend setup failed.")
            return False
        
        # Setup database
        if not self.setup_database():
            print("❌ Database setup failed.")
            return False
        
        self.print_header("BACKEND SETUP COMPLETE")
        print("✅ DojoTracker Backend is ready!")
        print("\n📋 Next steps:")
        print("   1. python backend_runner.py start      # Start the API server")
        print("   2. python backend_runner.py test       # Run API tests")
        print("   3. python backend_runner.py import     # Import sample techniques")
        print("   4. python backend_runner.py status     # Check status")
        print(f"\n🌐 API will be available at: {self.backend_url}/api")
        
        return True
    
    def run_quick_demo(self):
        """Run a quick demonstration of the backend"""
        self.print_header("QUICK BACKEND DEMO")
        
        if not self.test_backend_health():
            print("❌ Backend not running. Start backend first with: python backend_runner.py start")
            return False
        
        try:
            # Test basic functionality
            print("🧪 Testing basic API functionality...")
            
            # Get technique stats
            response = requests.get(f"{self.backend_url}/api/techniques/stats")
            if response.status_code == 200:
                stats = response.json().get('stats', {})
                print(f"📊 Technique Library: {stats.get('total_techniques', 0)} techniques, {stats.get('total_styles', 0)} styles")
            
            # Search for kicks
            response = requests.get(f"{self.backend_url}/api/techniques/search?q=kick&limit=3")
            if response.status_code == 200:
                techniques = response.json().get('techniques', [])
                print(f"🦵 Found {len(techniques)} kick techniques:")
                for tech in techniques:
                    print(f"   • {tech['name']} ({tech['style']})")
            
            # Test registration
            print("\n👤 Testing user registration...")
            user_data = {
                'email': f'demo_user_{int(time.time())}@example.com',
                'password': 'demo123',
                'first_name': 'Demo',
                'last_name': 'User',
                'martial_art': 'Karate',
                'current_belt': 'Green Belt'
            }
            
            response = requests.post(f"{self.backend_url}/api/auth/register", json=user_data)
            if response.status_code == 201:
                print("✅ User registration successful!")
                token = response.json().get('token')
                
                # Test creating a training session
                session_data = {
                    'duration': 45,
                    'style': 'Karate',
                    'techniques_practiced': ['Front Kick', 'Reverse Punch'],
                    'intensity_level': 7,
                    'notes': 'Demo training session'
                }
                
                headers = {'Authorization': f'Bearer {token}'}
                response = requests.post(f"{self.backend_url}/api/training/sessions", json=session_data, headers=headers)
                if response.status_code == 201:
                    print("✅ Training session created successfully!")
                
                # Test getting stats
                response = requests.get(f"{self.backend_url}/api/training/stats", headers=headers)
                if response.status_code == 200:
                    stats = response.json()
                    print(f"📈 Training stats: {stats.get('total_sessions', 0)} sessions, {stats.get('total_hours', 0)} hours")
            
            print("\n🎉 Backend demo completed successfully!")
            print(f"🌐 API is ready at: {self.backend_url}/api")
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            return False
        
        return True

def main():
    """Main function with command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='DojoTracker Backend Runner')
    parser.add_argument('command', choices=[
        'setup', 'start', 'test', 'import', 'status', 'demo'
    ], help='Command to run')
    
    args = parser.parse_args()
    
    runner = DojoTrackerBackendRunner()
    
    if args.command == 'setup':
        runner.full_setup()
    elif args.command == 'start':
        runner.start_backend()
    elif args.command == 'test':
        runner.run_api_tests()
    elif args.command == 'import':
        runner.import_sample_techniques()
    elif args.command == 'status':
        runner.show_status()
    elif args.command == 'demo':
        runner.run_quick_demo()

if __name__ == "__main__":
    main()