import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Basic Flask config
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database config
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///dojotracker.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # JWT config
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # External API keys
    FITBIT_CLIENT_ID = os.getenv('FITBIT_CLIENT_ID')
    FITBIT_CLIENT_SECRET = os.getenv('FITBIT_CLIENT_SECRET')
    WGER_API_KEY = os.getenv('WGER_API_KEY')
    
    # CORS settings - allow both localhost and 127.0.0.1
    CORS_ORIGINS = [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:5173',  # Vite's default port
        'http://127.0.0.1:5173'
    ]

class DevelopmentConfig(Config):
    DEBUG = True
    FLASK_ENV = 'development'
    # More permissive CORS for development
    CORS_ORIGINS = ['*']  # Allow all origins in development

class ProductionConfig(Config):
    DEBUG = False
    FLASK_ENV = 'production'
    # Strict CORS for production
    CORS_ORIGINS = ['https://yourdomain.com']  # Replace with your actual domain

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}