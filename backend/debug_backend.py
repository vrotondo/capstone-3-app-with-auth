#!/usr/bin/env python3
"""
Debug server to test if Flask is working at all
Run this from the backend directory to test basic functionality
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os

# Create a simple Flask app
app = Flask(__name__)
CORS(app, origins=['*'])  # Allow all origins for testing

@app.route('/')
def home():
    return jsonify({
        'message': 'Debug server is working!',
        'status': 'success'
    })

@app.route('/test', methods=['GET', 'POST', 'OPTIONS'])
def test():
    return jsonify({
        'message': 'Test endpoint working',
        'method': request.method,
        'data': request.get_json() if request.is_json else None
    })

@app.route('/api/auth/test', methods=['POST'])
def test_auth():
    return jsonify({
        'message': 'Auth test endpoint working',
        'received_data': request.get_json()
    })

if __name__ == '__main__':
    print("🔍 Starting debug server...")
    print("Python version:", sys.version)
    print("Current directory:", os.getcwd())
    print("Flask app:", app)
    
    try:
        print("🚀 Server starting on http://localhost:5000")
        app.run(debug=True, port=5000, host='0.0.0.0')
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        import traceback
        traceback.print_exc()