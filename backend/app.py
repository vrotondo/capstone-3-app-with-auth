import os
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

print("=" * 50)
print("🥋 DojoTracker Starting...")
print("📁 Current directory:", os.getcwd())
print("🐍 Python version:", sys.version)

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dojotracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'jwt-secret-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)

# CORS setup for Windows
CORS(app, 
     origins=['http://localhost:3000', 'http://127.0.0.1:3000'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization'],
     supports_credentials=True)

# User Model
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    primary_style = db.Column(db.String(50), nullable=True)
    belt_rank = db.Column(db.String(30), nullable=True)
    dojo = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, email, password, first_name, last_name, primary_style=None, belt_rank=None, dojo=None):
        self.email = email.lower().strip()
        self.password_hash = generate_password_hash(password)
        self.first_name = first_name.strip()
        self.last_name = last_name.strip()
        self.primary_style = primary_style
        self.belt_rank = belt_rank
        self.dojo = dojo
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'martial_art': self.primary_style,  # Frontend expects 'martial_art'
            'current_belt': self.belt_rank,     # Frontend expects 'current_belt'
            'dojo': self.dojo
        }
    
    @staticmethod
    def find_by_email(email):
        return User.query.filter_by(email=email.lower().strip()).first()

# Routes
@app.route('/')
def index():
    return jsonify({
        'message': 'DojoTracker API is running!',
        'version': '1.0.0',
        'status': 'healthy'
    })

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'message': 'API is working'})

# Auth Routes
@app.route('/api/auth/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        print(f"📝 Registration attempt: {data.get('email')}")
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name', 'martial_art']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} is required'}), 400
        
        # Check if user exists
        if User.find_by_email(data['email']):
            return jsonify({'message': 'User already exists'}), 409
        
        # Create user
        user = User(
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            primary_style=data['martial_art'],
            belt_rank=data.get('current_belt'),
            dojo=data.get('dojo')
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Create token
        token = create_access_token(identity=user.id)
        
        print(f"✅ User registered successfully: {user.email}")
        
        return jsonify({
            'message': 'Registration successful',
            'token': token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        print(f"❌ Registration error: {str(e)}")
        db.session.rollback()
        return jsonify({'message': f'Registration failed: {str(e)}'}), 500

@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        print(f"🔐 Login attempt: {data.get('email')}")
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Email and password required'}), 400
        
        user = User.find_by_email(data['email'])
        if not user or not user.check_password(data['password']):
            print(f"❌ Invalid credentials for: {data.get('email')}")
            return jsonify({'message': 'Invalid email or password'}), 401
        
        token = create_access_token(identity=user.id)
        
        print(f"✅ Login successful: {user.email}")
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return jsonify({'message': f'Login failed: {str(e)}'}), 500

@app.route('/api/auth/test', methods=['GET', 'POST'])
def auth_test():
    return jsonify({'message': 'Auth endpoints working', 'status': 'ok'})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'message': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🗄️ Setting up database...")
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully")
        except Exception as e:
            print(f"❌ Database error: {str(e)}")
    
    print("🚀 Starting server...")
    print("📍 Access at: http://localhost:8000")
    print("🔗 Frontend should use: http://localhost:8000/api")
    print("🧪 Test auth at: http://localhost:8000/api/auth/test")
    print("=" * 50)
    
    try:
        app.run(debug=True, port=8000, host='127.0.0.1')
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        input("Press Enter to exit...")