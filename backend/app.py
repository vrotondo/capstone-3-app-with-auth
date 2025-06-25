import os
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from config import config

# Import db from models
from models.user import db

# Initialize other extensions
jwt = JWTManager()
migrate = Migrate()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    
    # Configure CORS more explicitly for development
    CORS(app, 
         origins=['http://localhost:3000', 'http://127.0.0.1:3000'],
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         supports_credentials=True)
    
    migrate.init_app(app, db)
    
    # Import models (this must be after db initialization)
    from models.user import User
    from models.training import TrainingSession, TechniqueProgress
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.training import training_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(training_bp, url_prefix='/api/training')
    
    # Basic routes
    @app.route('/')
    def index():
        return jsonify({
            'message': 'DojoTracker API',
            'version': '1.0.0',
            'status': 'running'
        })
    
    @app.route('/api/health')
    def health_check():
        return jsonify({'status': 'healthy', 'database': 'connected'})
    
    # Test CORS endpoint
    @app.route('/api/test-cors', methods=['GET', 'POST', 'OPTIONS'])
    def test_cors():
        return jsonify({'message': 'CORS is working', 'method': 'success'})
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'message': 'Token has expired'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'message': 'Invalid token'}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'message': 'Authorization token is required'}), 401
    
    # Add error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'message': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'message': 'Internal server error'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        try:
            # Create tables on first run
            db.create_all()
            print("✅ Database tables created successfully")
        except Exception as e:
            print(f"❌ Database error: {str(e)}")
    
    print("🚀 Starting DojoTracker server...")
    print("📍 Server running at: http://localhost:5000")
    print("🔗 Frontend should connect from: http://localhost:3000")
    app.run(debug=True, port=5000, host='0.0.0.0')