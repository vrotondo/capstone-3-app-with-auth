import os
import sys
from flask import Flask, jsonify, request  # Added request import
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from datetime import timedelta

print("=" * 50)
print("🥋 DojoTracker Starting...")
print("📁 Current directory:", os.getcwd())
print("🐍 Python version:", sys.version)

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dojotracker.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-change-in-production'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['JWT_ALGORITHM'] = 'HS256'
    
    # Important: These settings help with JWT token handling
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'

    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)

    # Debug middleware to inspect JWT tokens
    @app.before_request
    def debug_jwt_token():
        """Debug JWT token in requests"""
        if request.endpoint and 'training' in str(request.endpoint):
            print(f"\n🔍 JWT Debug for {request.method} {request.path}")
            print(f"Endpoint: {request.endpoint}")
            
            auth_header = request.headers.get('Authorization')
            if auth_header:
                print(f"✅ Authorization header found: {auth_header[:50]}...")
                if auth_header.startswith('Bearer '):
                    token = auth_header[7:]  # Remove 'Bearer ' prefix
                    print(f"🔑 Token (first 30 chars): {token[:30]}...")
                    
                    # Try to decode the token to see if it's valid
                    try:
                        from flask_jwt_extended import decode_token
                        decoded = decode_token(token)
                        print(f"✅ Token decoded successfully: user_id = {decoded['sub']}")
                    except Exception as e:
                        print(f"❌ Token decode error: {str(e)}")
                else:
                    print("❌ Authorization header doesn't start with 'Bearer '")
            else:
                print("❌ No Authorization header found")
            print("---")

    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        print("❌ JWT: Token has expired")
        return jsonify({'message': 'Token has expired'}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        print(f"❌ JWT: Invalid token - {error}")
        return jsonify({'message': 'Invalid token'}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        print(f"❌ JWT: Missing token - {error}")
        return jsonify({'message': 'Authorization token is required'}), 401

    # Add token verification error handler
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        print("❌ JWT: Token has been revoked")
        return jsonify({'message': 'Token has been revoked'}), 401

    # CORS setup with more permissive settings for development
    CORS(app, 
         origins=['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:5173', 'http://127.0.0.1:5173'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
         supports_credentials=True,
         expose_headers=['Authorization'])

    # Create models
    from models.user import create_models
    User, TrainingSession, TechniqueProgress = create_models(db)
    
    # Make models available globally in the app
    app.User = User
    app.TrainingSession = TrainingSession
    app.TechniqueProgress = TechniqueProgress

    # Register blueprints
    from routes.auth import auth_bp
    from routes.training import training_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(training_bp, url_prefix='/api/training')

    # Basic routes
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

    # Enhanced error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'message': 'Endpoint not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'message': 'Internal server error'}), 500

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({'message': 'Unprocessable entity - check your request data'}), 422

    # Add debug route to check JWT configuration
    @app.route('/api/debug/jwt')
    def debug_jwt():
        return jsonify({
            'jwt_locations': app.config.get('JWT_TOKEN_LOCATION'),
            'jwt_header_name': app.config.get('JWT_HEADER_NAME'),
            'jwt_header_type': app.config.get('JWT_HEADER_TYPE'),
            'jwt_algorithm': app.config.get('JWT_ALGORITHM')
        })

    return app

if __name__ == '__main__':
    app = create_app()
    
    print("🗄️ Setting up database...")
    with app.app_context():
        try:
            # Create tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Check if we have any existing users
            from models.user import create_models
            User, TrainingSession, TechniqueProgress = create_models(db)
            user_count = User.query.count()
            session_count = TrainingSession.query.count()
            print(f"📊 Current database state:")
            print(f"   Users: {user_count}")
            print(f"   Training Sessions: {session_count}")
            
        except Exception as e:
            print(f"❌ Database error: {str(e)}")
    
    print("🚀 Starting server...")
    print("📍 Access at: http://localhost:8000")
    print("🔗 Frontend should use: http://localhost:8000/api")
    print("🧪 Test auth at: http://localhost:8000/api/auth/test")
    print("🔍 JWT debug at: http://localhost:8000/api/debug/jwt")
    print("=" * 50)
    
    try:
        app.run(debug=True, port=8000, host='127.0.0.1')
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        input("Press Enter to exit...")