#!/usr/bin/env python3
"""
Simple API testing script for DojoTracker
Run this after starting your Flask server to test basic functionality
"""

import requests
import json
import sys

BASE_URL = 'http://localhost:5000'

def test_endpoint(method, endpoint, data=None, headers=None, expected_status=200):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    print(f"\n🧪 Testing: {method} {endpoint}")
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
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
        print("❌ Connection failed - Make sure the Flask server is running")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def run_tests():
    """Run basic API tests"""
    print("🥋 DojoTracker API Tests")
    print("=" * 40)
    
    # Test basic endpoints
    test_endpoint('GET', '/')
    test_endpoint('GET', '/api/health')
    
    # Test auth endpoints
    test_endpoint('GET', '/api/auth/test')
    test_endpoint('GET', '/api/training/test')
    
    # Test user registration
    user_data = {
        'email': 'test@example.com',
        'password': 'password123',
        'first_name': 'Test',
        'last_name': 'User',
        'primary_style': 'Karate',
        'belt_rank': 'White'
    }
    
    print("\n🔐 Testing User Registration")
    register_response = test_endpoint('POST', '/api/auth/register', data=user_data, expected_status=201)
    
    if register_response and 'access_token' in register_response:
        access_token = register_response['access_token']
        headers = {'Authorization': f'Bearer {access_token}'}
        
        print("\n👤 Testing Authenticated Endpoints")
        
        # Test get current user
        test_endpoint('GET', '/api/auth/me', headers=headers)
        
        # Test create training session
        session_data = {
            'duration': 60,
            'style': 'Karate',
            'intensity_level': 7,
            'techniques_practiced': ['Front kick', 'Roundhouse kick'],
            'notes': 'Great training session!'
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
            'notes': 'Working on form'
        }
        
        test_endpoint('POST', '/api/training/techniques', 
                     data=technique_data, headers=headers, expected_status=201)
        
        # Test get techniques
        test_endpoint('GET', '/api/training/techniques', headers=headers)
        
    print("\n🎉 Tests completed!")
    print("\nNext steps:")
    print("1. All tests should pass if the backend is working correctly")
    print("2. You can now start building the React frontend")
    print("3. Use the endpoints tested above in your frontend app")

if __name__ == '__main__':
    run_tests()