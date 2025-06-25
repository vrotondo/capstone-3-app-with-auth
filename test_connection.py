#!/usr/bin/env python3
"""
Test script to verify DojoTracker backend is working
Run this to test your API endpoints
"""

import requests
import json
import sys
import time

BASE_URL = 'http://localhost:8000'

def test_endpoint(method, endpoint, data=None, headers=None, expected_status=200):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    print(f"\n🧪 Testing: {method} {endpoint}")
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=5)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers, timeout=5)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers, timeout=5)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=5)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == expected_status:
            print("✅ Test passed")
        else:
            print(f"❌ Test failed - Expected {expected_status}, got {response.status_code}")
        
        # Try to parse JSON response
        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
            return response_data
        except:
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - Make sure the Flask server is running on port 8000")
        print("💡 Start the backend with: cd backend && python app.py")
        return None
    except requests.exceptions.Timeout:
        print("❌ Request timeout - Server might be slow or unresponsive")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def wait_for_server():
    """Wait for the server to be ready"""
    print("⏳ Waiting for server to be ready...")
    for i in range(10):
        try:
            response = requests.get(f"{BASE_URL}/", timeout=2)
            if response.status_code == 200:
                print("✅ Server is ready!")
                return True
        except:
            time.sleep(1)
            print(f"   Attempt {i+1}/10...")
    
    print("❌ Server not responding after 10 attempts")
    return False

def run_comprehensive_tests():
    """Run comprehensive API tests"""
    print("🥋 DojoTracker Backend API Tests")
    print("=" * 50)
    
    # Wait for server
    if not wait_for_server():
        return False
    
    # Test basic endpoints
    print("\n📋 Testing Basic Endpoints")
    test_endpoint('GET', '/')
    test_endpoint('GET', '/api/health')
    
    # Test auth endpoints
    print("\n🔐 Testing Auth Endpoints")
    test_endpoint('GET', '/api/auth/test')
    
    # Test training endpoints
    print("\n🥋 Testing Training Endpoints")
    test_endpoint('GET', '/api/training/test')
    
    # Test user registration and authentication flow
    print("\n👤 Testing User Registration & Authentication")
    user_data = {
        'email': f'test{int(time.time())}@example.com',  # Unique email
        'password': 'password123',
        'first_name': 'Test',
        'last_name': 'User',
        'martial_art': 'Karate',
        'current_belt': 'White Belt',
        'dojo': 'Test Dojo'
    }
    
    # Register user
    register_response = test_endpoint('POST', '/api/auth/register', data=user_data, expected_status=201)
    
    if register_response and 'token' in register_response:
        token = register_response['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        print("\n🔒 Testing Authenticated Endpoints")
        
        # Test get current user
        test_endpoint('GET', '/api/auth/me', headers=headers)
        
        # Test training session creation
        session_data = {
            'duration': 60,
            'style': 'Karate',
            'intensity_level': 7,
            'techniques_practiced': ['Front kick', 'Roundhouse kick'],
            'notes': 'Great training session!',
            'energy_before': 6,
            'energy_after': 8,
            'mood': 'Focused'
        }
        
        session_response = test_endpoint('POST', '/api/training/sessions', 
                                       data=session_data, headers=headers, expected_status=201)
        
        # Test get training sessions
        test_endpoint('GET', '/api/training/sessions', headers=headers)
        
        # Test training stats
        test_endpoint('GET', '/api/training/stats', headers=headers)
        
        # Test create technique progress
        technique_data = {
            'technique_name': 'Front Kick',
            'style': 'Karate',
            'proficiency_level': 5,
            'notes': 'Working on form and power'
        }
        
        test_endpoint('POST', '/api/training/techniques', 
                     data=technique_data, headers=headers, expected_status=201)
        
        # Test get techniques
        test_endpoint('GET', '/api/training/techniques', headers=headers)
        
        # Test get user styles
        test_endpoint('GET', '/api/training/styles', headers=headers)
        
        print("\n🎉 All tests completed successfully!")
        print("\nYour backend is working correctly. You can now:")
        print("1. Start the React frontend: cd frontend && npm run dev")
        print("2. Open http://localhost:3000 in your browser")
        print("3. Register a new account and start using DojoTracker!")
        
        return True
    else:
        print("\n❌ Registration test failed - cannot continue with authenticated tests")
        return False

def main():
    """Main function to run tests"""
    try:
        success = run_comprehensive_tests()
        if success:
            print("\n✅ All tests passed! Your DojoTracker backend is ready.")
        else:
            print("\n❌ Some tests failed. Please check the backend server.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()