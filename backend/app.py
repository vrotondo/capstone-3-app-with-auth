import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from config import config

# Initialize extensions
db = SQLAlchemy()
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
    CORS(app, origins=app.config['CORS_ORIGINS'])
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
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()  # Create tables on first run
    app.run(debug=True, port=5000)