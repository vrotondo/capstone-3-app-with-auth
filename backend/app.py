import os
import sys
import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from datetime import timedelta, datetime
from dotenv import load_dotenv

load_dotenv()

print("=" * 50)
print("🥋 DojoTracker Starting...")
print("📁 Current directory:", os.getcwd())
print("🐍 Python version:", sys.version)
print(f"🔍 Loaded WGER_API_KEY: {'YES' if os.getenv('WGER_API_KEY') else 'NO'}")
print(f"🔍 Loaded GEMINI_API_KEY: {'YES' if os.getenv('GEMINI_API_KEY') else 'NO'}")

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

    # Database Configuration - Support both PostgreSQL and SQLite
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        print(f"✅ Using database from environment: {database_url.split('@')[0]}@****")
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dojotracker.db'
        print("ℹ️ Using default SQLite database")

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-change-in-production'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7) 
    app.config['JWT_ALGORITHM'] = 'HS256'

    # Important: These settings help with JWT token handling
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'

    print("📦 Loading AI analysis models...")
    try:
        from models.ai_analysis import create_ai_analysis_models
        VideoAnalysis, AnalysisFeedback, AnalysisProgress = create_ai_analysis_models(db)
        print("✅ AI analysis models loaded: VideoAnalysis, AnalysisFeedback, AnalysisProgress")
        
        # Make models available globally in the app
        app.VideoAnalysis = VideoAnalysis
        app.AnalysisFeedback = AnalysisFeedback
        app.AnalysisProgress = AnalysisProgress
        
    except Exception as e:
        print(f"❌ Error loading AI analysis models: {e}")
        # Don't raise - allow app to continue without AI features
        VideoAnalysis = None
        AnalysisFeedback = None
        AnalysisProgress = None

    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)

    # Debug middleware to inspect JWT tokens
    @app.before_request
    def debug_jwt_token():
        """Debug JWT token in requests - exclude video streaming"""
        
        # Skip debug for video streaming routes (they use token in URL)
        if request.endpoint and 'stream' in str(request.endpoint):
            return
        
        # Skip debug for static file requests
        if request.path.startswith('/static/') or request.path.endswith(('.css', '.js', '.png', '.jpg')):
            return
        
        # Only debug API routes that need JWT
        if request.endpoint and ('training' in str(request.endpoint) or 'techniques' in str(request.endpoint)):
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

    print("🔍 Attempting to import AI video analysis blueprint...")
    try:
        from routes.ai_analysis import video_analysis_bp  # Note: different name!
        print("✅ AI video analysis blueprint imported successfully")
        print(f"🔍 AI blueprint type: {type(video_analysis_bp)}")
        print(f"🔍 AI blueprint name: {video_analysis_bp.name}")
    except ImportError as import_error:
        print(f"❌ Import error: {import_error}")
        video_analysis_bp = None
    except Exception as e:
        print(f"❌ Failed to import AI video analysis blueprint: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        video_analysis_bp = None

    if video_analysis_bp:
        print(f"🔍 Registering AI video analysis blueprint: {video_analysis_bp}")
        app.register_blueprint(video_analysis_bp, url_prefix='/api/video-analysis')  # Different prefix!
        print("✅ AI video analysis blueprint registered at /api/video-analysis")
    else:
        print("❌ AI video analysis blueprint is None - cannot register")

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

    # Create user models
    print("📦 Loading user models...")
    try:
        from models.user import create_models
        models = create_models(db)
        print(f"🔍 create_models returned {len(models)} models")
        
        # Handle the correct number of models returned
        if len(models) == 3:
            User, TrainingSession, TechniqueProgress = models
            UserPreferences = None
            TrainingVideo = None
        elif len(models) == 4:
            User, TrainingSession, TechniqueProgress, UserPreferences = models
            TrainingVideo = None
        elif len(models) == 5:
            User, TrainingSession, TechniqueProgress, UserPreferences, TrainingVideo = models
        else:
            # Safe fallback - use positional indexing
            User = models[0]
            TrainingSession = models[1] 
            TechniqueProgress = models[2]
            UserPreferences = models[3] if len(models) > 3 else None
            TrainingVideo = models[4] if len(models) > 4 else None
            
        print(f"✅ User models loaded: User, TrainingSession, TechniqueProgress" + 
            (", UserPreferences" if UserPreferences else "") +
            (", TrainingVideo" if TrainingVideo else ""))
            
    except Exception as e:
        print(f"❌ Error loading user models: {e}")
        raise

    # Create technique library models
    print("📦 Loading technique library models...")
    try:
        from models.technique_library import create_technique_models
        TechniqueLibrary, UserTechniqueBookmark, TechniqueCategory = create_technique_models(db)
        print("✅ Technique library models loaded: TechniqueLibrary, UserTechniqueBookmark, TechniqueCategory")
    except Exception as e:
        print(f"❌ Error loading technique library models: {e}")
        raise

    # Create exercise models
    print("📦 Loading exercise models...")
    try:
        from models.exercise import create_exercise_models
        ExerciseCategory, MuscleGroup, Equipment, Exercise, WorkoutExercise = create_exercise_models(db)
        print("✅ Exercise models loaded: ExerciseCategory, MuscleGroup, Equipment, Exercise, WorkoutExercise")
    except Exception as e:
        print(f"❌ Error loading exercise models: {e}")
        raise

    # Create workout models
    print("📦 Loading workout models...")
    try:
        from models.workout import create_workout_models
        FavoriteExercise, WorkoutPlan, WorkoutPlanExercise = create_workout_models(db)
        print("✅ Workout models loaded: FavoriteExercise, WorkoutPlan, WorkoutExercise")
    except Exception as e:
        print(f"❌ Error loading workout models: {e}")
        raise

    # Make models available globally in the app
    app.User = User
    app.TrainingSession = TrainingSession
    app.TechniqueProgress = TechniqueProgress
    app.TechniqueLibrary = TechniqueLibrary
    app.UserTechniqueBookmark = UserTechniqueBookmark
    app.TechniqueCategory = TechniqueCategory
    app.ExerciseCategory = ExerciseCategory
    app.MuscleGroup = MuscleGroup
    app.Equipment = Equipment
    app.Exercise = Exercise
    app.WorkoutPlanExercise = WorkoutPlanExercise
    app.FavoriteExercise = FavoriteExercise
    app.WorkoutPlan = WorkoutPlan
    
    # Add UserPreferences if it exists
    if UserPreferences:
        app.UserPreferences = UserPreferences

    # Add TrainingVideo if it exists
    if TrainingVideo:
        app.TrainingVideo = TrainingVideo

    # Register blueprints - SINGLE REGISTRATION ONLY
    print("🔗 Registering blueprints...")
    
    # Import all blueprints with error handling
    try:
        print("🔍 Attempting to import auth blueprint...")
        from routes.auth import auth_bp
        print("✅ Auth blueprint imported successfully")
        print(f"🔍 Auth blueprint type: {type(auth_bp)}")
        print(f"🔍 Auth blueprint name: {auth_bp.name}")
    except Exception as e:
        print(f"❌ Failed to import auth blueprint: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        auth_bp = None
    
    try:
        from routes.training import training_bp
        print("✅ Training blueprint imported")
    except Exception as e:
        print(f"❌ Failed to import training blueprint: {e}")
        training_bp = None
    
    try:
        from routes.wger import wger_bp
        print("✅ wger blueprint imported")
    except Exception as e:
        print(f"❌ Failed to import wger blueprint: {e}")
        wger_bp = None

    try:
        from routes.workout import workout_bp
        print("✅ Workout blueprint imported")
    except Exception as e:
        print(f"❌ Failed to import workout blueprint: {e}")
        workout_bp = None
    
    try:
        from routes.techniques import techniques_bp
        print("✅ Techniques blueprint imported")
    except Exception as e:
        print(f"❌ Failed to import techniques blueprint: {e}")
        techniques_bp = None
    
    try:
        from routes.user import user_bp
        print("✅ User blueprint imported")
    except Exception as e:
        print(f"❌ Failed to import user blueprint: {e}")
        print("❌ Make sure you created backend/routes/user.py")
        user_bp = None
    
    try:
        from routes.exercises import exercises_bp
        print("✅ Exercises blueprint imported")
    except Exception as e:
        print(f"❌ Failed to import exercises blueprint: {e}")
        print("❌ Make sure you created backend/routes/exercises.py")
        exercises_bp = None
    
    if training_bp:
        app.register_blueprint(training_bp, url_prefix='/api/training')
        print("✅ Training blueprint registered at /api/training")
    else:
        print("❌ Training blueprint not registered")
    
    if techniques_bp:
        app.register_blueprint(techniques_bp, url_prefix='/api/techniques')
        print("✅ Techniques blueprint registered at /api/techniques")
    else:
        print("❌ Techniques blueprint not registered")
    
    if wger_bp:
        app.register_blueprint(wger_bp, url_prefix='/api/wger')
        print("✅ wger blueprint registered at /api/wger")
    else:
        print("❌ wger blueprint not registered")

    if workout_bp:
        app.register_blueprint(workout_bp, url_prefix='/api/workout')
        print("✅ Workout blueprint registered at /api/workout")
    else:
        print("❌ Workout blueprint not registered")
    
    if user_bp:
        app.register_blueprint(user_bp, url_prefix='/api/user')
        print("✅ User blueprint registered at /api/user")
    else:
        print("❌ User blueprint not registered")
    
    if exercises_bp:
        app.register_blueprint(exercises_bp, url_prefix='/api/exercises')
        print("✅ Exercises blueprint registered at /api/exercises")
    else:
        print("❌ Exercises blueprint not registered")

    # Register AI blueprint if available
    ai_bp = None
    if ai_bp:
        app.register_blueprint(ai_bp, url_prefix='/api/ai')
        print("✅ AI insights blueprint registered at /api/ai")
    else:
        print("❌ AI insights blueprint not registered")
        
    print("✅ Blueprints registration complete")

    # Basic routes
    @app.route('/')
    def index():
        return jsonify({
            'message': 'DojoTracker API is running!',
            'version': '1.0.0',
            'status': 'healthy',
            'features': ['Training Sessions', 'Technique Library', 'User Authentication', 'Exercise Database', 'wger Integration', 'AI Insights (Beta)']
        })

    @app.route('/api/health')
    def health():
        return jsonify({'status': 'healthy', 'message': 'API is working'})
    
    @app.route('/api/video-analysis-test')
    def video_analysis_simple_test():
        """Simple AI test that works in browser"""
        try:
            # Test 1: Check API key
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                return jsonify({
                    'status': 'error',
                    'message': 'No GEMINI_API_KEY found',
                    'step': 'Add GEMINI_API_KEY=your_key_here to your .env file',
                    'api_key_present': False
                })
            
            # Test 2: Try importing AI service
            try:
                from services.ai_video_analysis import AIVideoAnalysisService
                service = AIVideoAnalysisService()
                service_ready = True
                service_error = None
            except Exception as service_error:
                service_ready = False
                service_error = str(service_error)
            
            return jsonify({
                'status': 'success' if service_ready else 'partial',
                'message': 'AI video analysis system status',
                'api_key_present': True,
                'api_key_length': len(api_key),
                'service_ready': service_ready,
                'service_error': service_error,
                'max_frames': service.max_frames if service_ready else None,
                'endpoints': [
                    '/api/video-analysis/status',
                    '/api/video-analysis/test'
                ]
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            })

    # AI Status endpoint - always available even if AI blueprint isn't loaded
    @app.route('/api/ai-status')
    def ai_status():
        """Simple AI service status check - no complex imports needed"""
        
        # Check if API key exists
        api_key = os.getenv('GEMINI_API_KEY')
        
        status_info = {
            'timestamp': datetime.utcnow().isoformat(),
            'ai_enabled': False,
            'status': 'checking',
            'message': 'Checking AI service availability...'
        }
        
        if not api_key:
            status_info.update({
                'ai_enabled': False,
                'status': 'no_api_key',
                'message': 'GEMINI_API_KEY not found in environment variables',
                'instructions': [
                    'Get API key from https://makersuite.google.com/app/apikey',
                    'Add GEMINI_API_KEY=your_key_here to backend/.env file',
                    'Restart the server'
                ]
            })
            return jsonify(status_info)
        
        # Check if library is installed
        try:
            import google.generativeai as genai
            status_info.update({
                'ai_enabled': True,
                'status': 'ready',
                'message': 'Google Gemini AI is ready to use!',
                'api_key_present': True,
                'library_installed': True,
                'blueprint_loaded': ai_bp is not None,
                'next_steps': [
                    'AI insights will appear on your dashboard',
                    'Full AI features coming soon'
                ]
            })
        except ImportError:
            status_info.update({
                'ai_enabled': False,
                'status': 'library_missing',
                'message': 'Google Generative AI library not installed',
                'api_key_present': True,
                'library_installed': False,
                'fix_command': 'pip install google-generativeai==0.3.2'
            })
        except Exception as e:
            status_info.update({
                'ai_enabled': False,
                'status': 'error',
                'message': f'AI service error: {str(e)}',
                'error': str(e)
            })
        
        return jsonify(status_info)

    # Add a simple test endpoint too
    @app.route('/api/ai-test')
    def ai_test():
        """Test if we can actually use the AI service"""
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return jsonify({
                'test_result': 'failed',
                'reason': 'No API key'
            }), 400
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            # Try to create a model instance
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            return jsonify({
                'test_result': 'success',
                'message': 'AI service is working correctly!',
                'model': 'gemini-1.5-flash',
                'ready_for_insights': True,
                'blueprint_available': ai_bp is not None
            })
            
        except Exception as e:
            return jsonify({
                'test_result': 'failed',
                'reason': str(e),
                'message': 'AI service test failed'
            }), 500

    # Add wger test route
    @app.route('/api/wger/test')
    def test_wger_integration():
        """Quick test endpoint for wger integration"""
        try:
            from services.wger_api import wger_service
            result = wger_service.test_connection()
            return jsonify({
                'wger_integration': True,
                'connection_test': result
            })
        except Exception as e:
            return jsonify({
                'wger_integration': False,
                'error': str(e)
            }), 500

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

    # Add debug route to see all registered routes
    @app.route('/api/debug/routes')
    def debug_routes():
        """Debug endpoint to see all registered routes"""
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'url': rule.rule
            })
        return jsonify({
            'total_routes': len(routes),
            'routes': sorted(routes, key=lambda x: x['url']),
            'ai_routes': [r for r in routes if '/api/video-analysis' in r['url']],
            'all_ai_routes': [r for r in routes if '/api/ai' in r['url'] or '/api/video-analysis' in r['url']]
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
            
            # Safe database statistics that won't fail if schema is wrong
            User = app.User
            TrainingSession = app.TrainingSession
            TechniqueProgress = app.TechniqueProgress
            TechniqueLibrary = app.TechniqueLibrary
            Exercise = app.Exercise
            
            # Try to get counts, but handle errors gracefully
            try:
                user_count = User.query.count()
                session_count = TrainingSession.query.count()
                technique_count = TechniqueLibrary.query.count()
                exercise_count = Exercise.query.count()
                
                print(f"📊 Current database state:")
                print(f"   Users: {user_count}")
                print(f"   Training Sessions: {session_count}")
                print(f"   Techniques: {technique_count}")
                print(f"   Exercises: {exercise_count}")
            except Exception as count_error:
                print(f"ℹ️ Could not get database counts (normal for new database): {count_error}")
                print("📊 Database appears to be freshly created")
            
        except Exception as e:
            print(f"❌ Database error: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("🚀 Starting server...")
    print("📍 Access at: http://localhost:8000")
    print("🔗 Frontend should use: http://localhost:8000/api")
    print("🧪 Test auth at: http://localhost:8000/api/auth/test")
    print("🥋 Test techniques at: http://localhost:8000/api/techniques/test")
    print("💪 Test exercises at: http://localhost:8000/api/exercises/test")
    print("🌐 Test wger at: http://localhost:8000/api/wger/test")
    print("🤖 Test AI status at: http://localhost:8000/api/ai-status")
    print("🔬 Test AI service at: http://localhost:8000/api/ai-test")
    print("🔍 JWT debug at: http://localhost:8000/api/debug/jwt")
    print("🗺️ All routes at: http://localhost:8000/api/debug/routes")
    print("=" * 50)
    
    try:
        app.run(debug=True, port=8000, host='127.0.0.1')
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        input("Press Enter to exit...")