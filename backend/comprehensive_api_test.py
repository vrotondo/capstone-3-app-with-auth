#!/usr/bin/env python3
"""
Comprehensive API test script for DojoTracker
Tests all endpoints including the new technique library features
"""

import requests
import json
import time
from datetime import datetime, date

class DojoTrackerAPITester:
    def __init__(self, base_url='http://localhost:8000'):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        self.test_user_id = None
        
        # Test data
        self.test_user = {
            'email': f'test_user_{int(time.time())}@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'martial_art': 'Karate',
            'current_belt': 'Green Belt',
            'dojo': 'Test Dojo'
        }
    
    def print_section(self, title):
        """Print a formatted section header"""
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
        print('='*60)
    
    def print_test(self, test_name, success=True, details=None):
        """Print test result"""
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
    
    def make_request(self, method, endpoint, data=None, auth=True):
        """Make API request with optional authentication"""
        url = f"{self.base_url}/api{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if auth and self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, headers=headers)
            elif method.upper() == 'POST':
                response = self.session.post(url, headers=headers, json=data)
            elif method.upper() == 'PUT':
                response = self.session.put(url, headers=headers, json=data)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, headers=headers)
            
            return response
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def test_basic_connectivity(self):
        """Test basic API connectivity"""
        self.print_section("BASIC CONNECTIVITY")
        
        # Test root endpoint
        try:
            response = requests.get(f"{self.base_url}")
            if response.status_code == 200:
                data = response.json()
                self.print_test("Root endpoint", True, f"Status: {data.get('status', 'unknown')}")
            else:
                self.print_test("Root endpoint", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("Root endpoint", False, str(e))
        
        # Test health endpoint
        try:
            response = requests.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                self.print_test("Health endpoint", True)
            else:
                self.print_test("Health endpoint", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("Health endpoint", False, str(e))
    
    def test_authentication(self):
        """Test authentication endpoints"""
        self.print_section("AUTHENTICATION")
        
        # Test registration
        response = self.make_request('POST', '/auth/register', self.test_user, auth=False)
        if response and response.status_code == 201:
            data = response.json()
            self.auth_token = data.get('token')
            self.test_user_id = data.get('user', {}).get('id')
            self.print_test("User registration", True, f"User ID: {self.test_user_id}")
        else:
            self.print_test("User registration", False, f"Status: {response.status_code if response else 'No response'}")
            return False
        
        # Test login
        login_data = {
            'email': self.test_user['email'],
            'password': self.test_user['password']
        }
        response = self.make_request('POST', '/auth/login', login_data, auth=False)
        if response and response.status_code == 200:
            data = response.json()
            self.auth_token = data.get('token')  # Update token
            self.print_test("User login", True)
        else:
            self.print_test("User login", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test get current user
        response = self.make_request('GET', '/auth/me')
        if response and response.status_code == 200:
            data = response.json()
            user = data.get('user', {})
            self.print_test("Get current user", True, f"Email: {user.get('email')}")
        else:
            self.print_test("Get current user", False, f"Status: {response.status_code if response else 'No response'}")
        
        return True
    
    def test_technique_library(self):
        """Test technique library endpoints"""
        self.print_section("TECHNIQUE LIBRARY")
        
        # Test technique stats
        response = self.make_request('GET', '/techniques/stats', auth=False)
        if response and response.status_code == 200:
            data = response.json()
            stats = data.get('stats', {})
            self.print_test("Get technique stats", True, 
                          f"Techniques: {stats.get('total_techniques', 0)}, Styles: {stats.get('total_styles', 0)}")
        else:
            self.print_test("Get technique stats", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test get styles
        response = self.make_request('GET', '/techniques/styles', auth=False)
        if response and response.status_code == 200:
            data = response.json()
            styles = data.get('styles', [])
            self.print_test("Get available styles", True, f"Found {len(styles)} styles: {', '.join(styles[:3])}")
        else:
            self.print_test("Get available styles", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test get categories
        response = self.make_request('GET', '/techniques/categories', auth=False)
        if response and response.status_code == 200:
            data = response.json()
            categories = data.get('categories', [])
            self.print_test("Get available categories", True, f"Found {len(categories)} categories: {', '.join(categories[:3])}")
        else:
            self.print_test("Get available categories", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test search techniques
        response = self.make_request('GET', '/techniques/search?q=kick&limit=5', auth=False)
        if response and response.status_code == 200:
            data = response.json()
            techniques = data.get('techniques', [])
            self.print_test("Search techniques", True, f"Found {len(techniques)} techniques")
            
            # Store first technique ID for detailed testing
            if techniques:
                self.test_technique_id = techniques[0]['id']
                print(f"   Sample: {techniques[0]['name']} ({techniques[0]['style']})")
        else:
            self.print_test("Search techniques", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test popular techniques
        response = self.make_request('GET', '/techniques/popular?limit=5', auth=False)
        if response and response.status_code == 200:
            data = response.json()
            techniques = data.get('techniques', [])
            self.print_test("Get popular techniques", True, f"Found {len(techniques)} popular techniques")
        else:
            self.print_test("Get popular techniques", False, f"Status: {response.status_code if response else 'No response'}")
    
    def test_technique_details(self):
        """Test technique detail endpoints"""
        self.print_section("TECHNIQUE DETAILS")
        
        if not hasattr(self, 'test_technique_id'):
            print("⚠️ No technique ID available for testing")
            return
        
        technique_id = self.test_technique_id
        
        # Test get technique detail (unauthenticated)
        response = self.make_request('GET', f'/techniques/{technique_id}', auth=False)
        if response and response.status_code == 200:
            data = response.json()
            technique = data.get('technique', {})
            self.print_test("Get technique detail (public)", True, f"Name: {technique.get('name')}")
        else:
            self.print_test("Get technique detail (public)", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test get technique detail (authenticated)
        response = self.make_request('GET', f'/techniques/{technique_id}')
        if response and response.status_code == 200:
            data = response.json()
            technique = data.get('technique', {})
            self.print_test("Get technique detail (authenticated)", True, 
                          f"Name: {technique.get('name')}, Bookmarked: {technique.get('is_bookmarked', False)}")
        else:
            self.print_test("Get technique detail (authenticated)", False, f"Status: {response.status_code if response else 'No response'}")
    
    def test_bookmarks(self):
        """Test bookmark functionality"""
        self.print_section("BOOKMARKS")
        
        if not hasattr(self, 'test_technique_id'):
            print("⚠️ No technique ID available for testing")
            return
        
        technique_id = self.test_technique_id
        
        # Test bookmark technique
        bookmark_data = {'notes': 'This is a test bookmark note'}
        response = self.make_request('POST', f'/techniques/{technique_id}/bookmark', bookmark_data)
        if response and response.status_code == 201:
            data = response.json()
            bookmark = data.get('bookmark', {})
            self.print_test("Bookmark technique", True, f"Bookmark ID: {bookmark.get('id')}")
        else:
            self.print_test("Bookmark technique", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test get user bookmarks
        response = self.make_request('GET', '/techniques/bookmarks')
        if response and response.status_code == 200:
            data = response.json()
            bookmarks = data.get('bookmarks', [])
            self.print_test("Get user bookmarks", True, f"Found {len(bookmarks)} bookmarks")
        else:
            self.print_test("Get user bookmarks", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test update technique progress
        progress_data = {
            'mastery_level': 7,
            'notes': 'Updated practice notes'
        }
        response = self.make_request('PUT', f'/techniques/{technique_id}/progress', progress_data)
        if response and response.status_code == 200:
            data = response.json()
            bookmark = data.get('bookmark', {})
            self.print_test("Update technique progress", True, f"Mastery level: {bookmark.get('mastery_level')}")
        else:
            self.print_test("Update technique progress", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test remove bookmark
        response = self.make_request('DELETE', f'/techniques/{technique_id}/bookmark')
        if response and response.status_code == 200:
            self.print_test("Remove bookmark", True)
        else:
            self.print_test("Remove bookmark", False, f"Status: {response.status_code if response else 'No response'}")
    
    def test_training_sessions(self):
        """Test training session endpoints"""
        self.print_section("TRAINING SESSIONS")
        
        # Test create training session
        session_data = {
            'duration': 60,
            'style': 'Karate',
            'date': date.today().isoformat(),
            'techniques_practiced': ['Front Kick', 'Reverse Punch'],
            'intensity_level': 7,
            'notes': 'Great training session today!',
            'energy_before': 6,
            'energy_after': 8
        }
        
        response = self.make_request('POST', '/training/sessions', session_data)
        if response and response.status_code == 201:
            data = response.json()
            session = data.get('session', {})
            session_id = session.get('id')
            self.print_test("Create training session", True, f"Session ID: {session_id}")
            self.test_session_id = session_id
        else:
            self.print_test("Create training session", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test get training sessions
        response = self.make_request('GET', '/training/sessions')
        if response and response.status_code == 200:
            data = response.json()
            sessions = data.get('sessions', [])
            self.print_test("Get training sessions", True, f"Found {len(sessions)} sessions")
        else:
            self.print_test("Get training sessions", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test get specific session
        if hasattr(self, 'test_session_id'):
            response = self.make_request('GET', f'/training/sessions/{self.test_session_id}')
            if response and response.status_code == 200:
                data = response.json()
                session = data.get('session', {})
                self.print_test("Get specific session", True, f"Duration: {session.get('duration')} min")
            else:
                self.print_test("Get specific session", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test training statistics
        response = self.make_request('GET', '/training/stats')
        if response and response.status_code == 200:
            data = response.json()
            self.print_test("Get training statistics", True, 
                          f"Total sessions: {data.get('total_sessions', 0)}, Total hours: {data.get('total_hours', 0)}")
        else:
            self.print_test("Get training statistics", False, f"Status: {response.status_code if response else 'No response'}")
    
    def test_technique_progress(self):
        """Test technique progress endpoints"""
        self.print_section("TECHNIQUE PROGRESS")
        
        # Test create technique progress
        technique_data = {
            'technique_name': 'Test Roundhouse Kick',
            'style': 'Karate',
            'proficiency_level': 5,
            'notes': 'Working on balance and form'
        }
        
        response = self.make_request('POST', '/training/techniques', technique_data)
        if response and response.status_code == 201:
            data = response.json()
            technique = data.get('technique', {})
            technique_progress_id = technique.get('id')
            self.print_test("Create technique progress", True, f"Technique ID: {technique_progress_id}")
            self.test_technique_progress_id = technique_progress_id
        else:
            self.print_test("Create technique progress", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test get technique progress
        response = self.make_request('GET', '/training/techniques')
        if response and response.status_code == 200:
            data = response.json()
            techniques = data.get('techniques', [])
            self.print_test("Get technique progress", True, f"Found {len(techniques)} techniques in progress")
        else:
            self.print_test("Get technique progress", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test update technique progress
        if hasattr(self, 'test_technique_progress_id'):
            update_data = {
                'proficiency_level': 7,
                'notes': 'Improved significantly!'
            }
            response = self.make_request('PUT', f'/training/techniques/{self.test_technique_progress_id}', update_data)
            if response and response.status_code == 200:
                data = response.json()
                technique = data.get('technique', {})
                self.print_test("Update technique progress", True, f"New proficiency: {technique.get('proficiency_level')}")
            else:
                self.print_test("Update technique progress", False, f"Status: {response.status_code if response else 'No response'}")
    
    def test_import_functionality(self):
        """Test technique import functionality"""
        self.print_section("IMPORT FUNCTIONALITY")
        
        # Test scraper
        response = self.make_request('POST', '/techniques/test-scraper', auth=False)
        if response and response.status_code == 200:
            data = response.json()
            techniques_found = data.get('techniques_found', 0)
            self.print_test("Test scraper", True, f"Found {techniques_found} techniques")
        else:
            self.print_test("Test scraper", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test import (small batch)
        import_data = {
            'source': 'blackbeltwiki',
            'max_techniques': 3
        }
        response = self.make_request('POST', '/techniques/import', import_data)
        if response and response.status_code == 200:
            data = response.json()
            result = data.get('import_result', {})
            imported = result.get('imported', 0)
            updated = result.get('updated', 0)
            self.print_test("Import techniques", True, f"Imported: {imported}, Updated: {updated}")
        else:
            self.print_test("Import techniques", False, f"Status: {response.status_code if response else 'No response'}")
    
    def test_error_handling(self):
        """Test error handling"""
        self.print_section("ERROR HANDLING")
        
        # Test invalid technique ID
        response = self.make_request('GET', '/techniques/99999', auth=False)
        if response and response.status_code == 404:
            self.print_test("Invalid technique ID", True, "Returns 404 as expected")
        else:
            self.print_test("Invalid technique ID", False, f"Expected 404, got {response.status_code if response else 'No response'}")
        
        # Test unauthorized access
        response = self.make_request('GET', '/techniques/bookmarks', auth=False)
        if response and response.status_code == 401:
            self.print_test("Unauthorized bookmark access", True, "Returns 401 as expected")
        else:
            self.print_test("Unauthorized bookmark access", False, f"Expected 401, got {response.status_code if response else 'No response'}")
        
        # Test invalid training session data
        invalid_session = {
            'duration': -10,  # Invalid duration
            'style': '',      # Empty style
            'intensity_level': 15  # Invalid intensity
        }
        response = self.make_request('POST', '/training/sessions', invalid_session)
        if response and response.status_code == 400:
            self.print_test("Invalid session data", True, "Returns 400 as expected")
        else:
            self.print_test("Invalid session data", False, f"Expected 400, got {response.status_code if response else 'No response'}")
    
    def cleanup_test_data(self):
        """Clean up test data"""
        self.print_section("CLEANUP")
        
        # Delete test session if created
        if hasattr(self, 'test_session_id'):
            response = self.make_request('DELETE', f'/training/sessions/{self.test_session_id}')
            if response and response.status_code == 200:
                self.print_test("Delete test session", True)
            else:
                self.print_test("Delete test session", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Delete test technique progress if created
        if hasattr(self, 'test_technique_progress_id'):
            response = self.make_request('DELETE', f'/training/techniques/{self.test_technique_progress_id}')
            if response and response.status_code == 200:
                self.print_test("Delete test technique progress", True)
            else:
                self.print_test("Delete test technique progress", False, f"Status: {response.status_code if response else 'No response'}")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🧪 DojoTracker API Comprehensive Test Suite")
        print(f"📅 Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Testing: {self.base_url}")
        
        try:
            # Run tests in logical order
            self.test_basic_connectivity()
            
            if self.test_authentication():
                self.test_technique_library()
                self.test_technique_details()
                self.test_bookmarks()
                self.test_training_sessions()
                self.test_technique_progress()
                self.test_import_functionality()
                self.test_error_handling()
                self.cleanup_test_data()
            else:
                print("❌ Authentication failed, skipping authenticated tests")
            
            self.print_section("TEST SUMMARY")
            print("✅ Comprehensive API test completed!")
            print("📊 Check the results above for any failing tests")
            print("🚀 If all tests pass, your API is ready for production!")
            
        except KeyboardInterrupt:
            print("\n⚠️ Tests interrupted by user")
        except Exception as e:
            print(f"\n❌ Test suite failed with error: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main function to run tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description='DojoTracker API Test Suite')
    parser.add_argument('--url', default='http://localhost:8000',
                       help='Base URL for the API (default: http://localhost:8000)')
    parser.add_argument('--test', choices=[
        'all', 'auth', 'techniques', 'training', 'import', 'bookmarks'
    ], default='all', help='Specific test to run (default: all)')
    
    args = parser.parse_args()
    
    tester = DojoTrackerAPITester(args.url)
    
    if args.test == 'all':
        tester.run_all_tests()
    elif args.test == 'auth':
        tester.test_basic_connectivity()
        tester.test_authentication()
    elif args.test == 'techniques':
        tester.test_technique_library()
    elif args.test == 'training':
        tester.test_authentication()
        tester.test_training_sessions()
        tester.test_technique_progress()
    elif args.test == 'import':
        tester.test_authentication()
        tester.test_import_functionality()
    elif args.test == 'bookmarks':
        tester.test_authentication()
        tester.test_bookmarks()

if __name__ == "__main__":
    main()