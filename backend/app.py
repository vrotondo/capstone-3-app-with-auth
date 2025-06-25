import os
import sys
from flask import Flask, jsonify
from flask_cors import CORS

print("=" * 50)
print("🥋 DojoTracker Starting...")
print("📁 Current directory:", os.getcwd())
print("🐍 Python version:", sys.version)

app = Flask(__name__)

# Simple CORS setup for Windows
CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])

@app.route('/')
def index():
    return jsonify({
        'message': 'DojoTracker API is running!',
        'version': '1.0.0',
        'status': 'healthy'
    })

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'message': 'API is working'
    })

@app.route('/api/test')
def test():
    return jsonify({
        'message': 'Test endpoint working',
        'cors': 'enabled'
    })

# Simple auth test endpoint
@app.route('/api/auth/test', methods=['GET', 'POST'])
def auth_test():
    return jsonify({
        'message': 'Auth endpoint accessible',
        'method': 'working'
    })

if __name__ == '__main__':
    print("🚀 Starting server...")
    print("📍 Access at: http://localhost:8000")
    print("🔗 Frontend should use: http://localhost:8000/api")
    print("=" * 50)
    
    try:
        app.run(debug=True, port=8000, host='127.0.0.1')
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        input("Press Enter to exit...")