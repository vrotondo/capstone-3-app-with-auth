from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import sys
import os

try:
    from services.wger_api import WgerAPIService
    wger_service = WgerAPIService(api_key=os.getenv('WGER_API_KEY'))
    print("✅ Successfully imported wger_service with API key")
except ImportError as e:
    print(f"❌ Failed to import wger_service: {e}")
    wger_service = None

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

try:
    from services.wger_api import wger_service
    print("✅ Successfully imported wger_service")
except ImportError as e:
    print(f"❌ Failed to import wger_service: {e}")
    wger_service = None

wger_bp = Blueprint('wger', __name__)

@wger_bp.route('/test', methods=['GET'])
def test_wger_connection():
    """Test wger API connection"""
    if not wger_service:
        return jsonify({
            'success': False,
            'message': 'wger service not available'
        }), 500
    
    result = wger_service.test_connection()
    status_code = 200 if result['success'] else 500
    return jsonify(result), status_code

@wger_bp.route('/categories', methods=['GET'])
def get_exercise_categories():
    """Get all exercise categories"""
    try:
        if not wger_service:
            return jsonify({'error': 'wger service not available'}), 500
        
        categories = wger_service.get_exercise_categories()
        
        return jsonify({
            'success': True,
            'count': len(categories),
            'categories': categories
        })
        
    except Exception as e:
        print(f"❌ Error fetching categories: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'categories': []
        }), 500

@wger_bp.route('/muscles', methods=['GET'])
def get_muscles():
    """Get all muscle groups"""
    try:
        if not wger_service:
            return jsonify({'error': 'wger service not available'}), 500
        
        muscles = wger_service.get_muscles()
        
        return jsonify({
            'success': True,
            'count': len(muscles),
            'muscles': muscles
        })
        
    except Exception as e:
        print(f"❌ Error fetching muscles: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'muscles': []
        }), 500

@wger_bp.route('/equipment', methods=['GET'])
def get_equipment():
    """Get all equipment types"""
    try:
        if not wger_service:
            return jsonify({'error': 'wger service not available'}), 500
        
        equipment = wger_service.get_equipment()
        
        return jsonify({
            'success': True,
            'count': len(equipment),
            'equipment': equipment
        })
        
    except Exception as e:
        print(f"❌ Error fetching equipment: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'equipment': []
        }), 500

@wger_bp.route('/exercises', methods=['GET'])
def get_exercises():
    """Get exercises with optional filtering"""
    try:
        if not wger_service:
            return jsonify({'error': 'wger service not available'}), 500
        
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        category = request.args.get('category', type=int)
        muscle = request.args.get('muscle', type=int)
        equipment = request.args.get('equipment', type=int)
        search = request.args.get('search', type=str)
        
        # Limit the limit to prevent abuse
        limit = min(limit, 100)
        
        exercises_data = wger_service.get_exercises(
            limit=limit,
            offset=offset,
            category=category,
            muscle=muscle,
            equipment=equipment,
            search=search
        )
        
        # Add debugging
        print(f"🔍 Raw exercises_data keys: {exercises_data.keys()}")
        print(f"🔍 Number of exercises: {len(exercises_data.get('results', []))}")
        
        # Check if any exercises were enhanced properly
        if exercises_data.get('results'):
            first_exercise = exercises_data['results'][0]
            print(f"🔍 First exercise sample: {first_exercise}")
        
        return jsonify({
            'success': True,
            'count': exercises_data.get('count', 0),
            'next': exercises_data.get('next'),
            'previous': exercises_data.get('previous'),
            'exercises': exercises_data.get('results', [])
        })
        
    except Exception as e:
        print(f"❌ Error in get_exercises route: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'exercises': []
        }), 500

@wger_bp.route('/exercises/<int:exercise_id>', methods=['GET'])
def get_exercise_detail(exercise_id):
    """Get detailed information about a specific exercise"""
    try:
        if not wger_service:
            return jsonify({'error': 'wger service not available'}), 500
        
        exercise = wger_service.get_exercise_details(exercise_id)
        
        if not exercise:
            return jsonify({
                'success': False,
                'error': 'Exercise not found'
            }), 404
        
        # Convert dataclass to dict
        exercise_dict = {
            'id': exercise.id,
            'name': exercise.name,
            'description': exercise.description,
            'category': exercise.category,
            'muscles': exercise.muscles,
            'muscles_secondary': exercise.muscles_secondary,
            'equipment': exercise.equipment,
            'instructions': exercise.instructions,
            'variations': exercise.variations,
            'license_author': exercise.license_author,
            'creation_date': exercise.creation_date,
            'uuid': exercise.uuid,
            'images': exercise.images
        }
        
        return jsonify({
            'success': True,
            'exercise': exercise_dict
        })
        
    except Exception as e:
        print(f"❌ Error fetching exercise detail: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@wger_bp.route('/exercises/search', methods=['GET'])
def search_exercises():
    """Search exercises by name or keyword"""
    try:
        if not wger_service:
            return jsonify({'error': 'wger service not available'}), 500
        
        query = request.args.get('q', '').strip()
        limit = request.args.get('limit', 20, type=int)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query is required'
            }), 400
        
        # Limit the limit to prevent abuse
        limit = min(limit, 50)
        
        results = wger_service.search_exercises(query, limit)
        
        return jsonify({
            'success': True,
            'count': len(results),
            'query': query,
            'exercises': results
        })
        
    except Exception as e:
        print(f"❌ Error searching exercises: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'exercises': []
        }), 500

@wger_bp.route('/exercises/martial-arts', methods=['GET'])
def get_martial_arts_exercises():
    """Get exercises particularly relevant for martial arts training"""
    try:
        if not wger_service:
            return jsonify({'error': 'wger service not available'}), 500
        
        limit = request.args.get('limit', 100, type=int)
        limit = min(limit, 200)  # Cap at 200
        
        exercises = wger_service.get_martial_arts_relevant_exercises(limit)
        
        return jsonify({
            'success': True,
            'count': len(exercises),
            'message': 'Exercises curated for martial arts training',
            'exercises': exercises
        })
        
    except Exception as e:
        print(f"❌ Error fetching martial arts exercises: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'exercises': []
        }), 500

@wger_bp.route('/exercises/by-category/<category_name>', methods=['GET'])
def get_exercises_by_category(category_name):
    """Get exercises for a specific category"""
    try:
        if not wger_service:
            return jsonify({'error': 'wger service not available'}), 500
        
        limit = request.args.get('limit', 50, type=int)
        limit = min(limit, 100)
        
        exercises = wger_service.get_exercises_by_category(category_name, limit)
        
        return jsonify({
            'success': True,
            'count': len(exercises),
            'category': category_name,
            'exercises': exercises
        })
        
    except Exception as e:
        print(f"❌ Error fetching exercises by category: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'exercises': []
        }), 500

@wger_bp.route('/exercises/by-muscle/<muscle_name>', methods=['GET'])
def get_exercises_by_muscle(muscle_name):
    """Get exercises that target a specific muscle"""
    try:
        if not wger_service:
            return jsonify({'error': 'wger service not available'}), 500
        
        limit = request.args.get('limit', 30, type=int)
        limit = min(limit, 100)
        
        exercises = wger_service.get_muscle_exercises(muscle_name, limit)
        
        return jsonify({
            'success': True,
            'count': len(exercises),
            'muscle': muscle_name,
            'exercises': exercises
        })
        
    except Exception as e:
        print(f"❌ Error fetching exercises by muscle: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'exercises': []
        }), 500

@wger_bp.route('/exercises/by-equipment/<equipment_name>', methods=['GET'])
def get_exercises_by_equipment(equipment_name):
    """Get exercises that use specific equipment"""
    try:
        if not wger_service:
            return jsonify({'error': 'wger service not available'}), 500
        
        limit = request.args.get('limit', 30, type=int)
        limit = min(limit, 100)
        
        exercises = wger_service.get_equipment_exercises(equipment_name, limit)
        
        return jsonify({
            'success': True,
            'count': len(exercises),
            'equipment': equipment_name,
            'exercises': exercises
        })
        
    except Exception as e:
        print(f"❌ Error fetching exercises by equipment: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'exercises': []
        }), 500

@wger_bp.route('/stats', methods=['GET'])
def get_api_stats():
    """Get statistics about the wger API data"""
    try:
        if not wger_service:
            return jsonify({'error': 'wger service not available'}), 500
        
        stats = wger_service.get_api_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        print(f"❌ Error fetching API stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'stats': {}
        }), 500

@wger_bp.route('/cache/clear', methods=['POST'])
@jwt_required()
def clear_cache():
    """Clear the wger API cache (requires authentication)"""
    try:
        if not wger_service:
            return jsonify({'error': 'wger service not available'}), 500
        
        wger_service.clear_cache()
        
        return jsonify({
            'success': True,
            'message': 'Cache cleared successfully'
        })
        
    except Exception as e:
        print(f"❌ Error clearing cache: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Protected routes for user-specific exercise data
@wger_bp.route('/user/favorites', methods=['GET', 'POST', 'DELETE'])
@jwt_required()
def user_favorite_exercises():
    """Manage user's favorite exercises from wger"""
    try:
        user_id = get_jwt_identity()
        
        if request.method == 'GET':
            # Get user's favorite exercises
            # This would integrate with your user preferences model
            # For now, return a placeholder
            return jsonify({
                'success': True,
                'favorites': []
            })
        
        elif request.method == 'POST':
            # Add exercise to favorites
            data = request.get_json()
            exercise_id = data.get('exercise_id')
            
            if not exercise_id:
                return jsonify({
                    'success': False,
                    'error': 'exercise_id is required'
                }), 400
            
            # Here you would save to your database
            # For now, return success
            return jsonify({
                'success': True,
                'message': f'Exercise {exercise_id} added to favorites'
            })
        
        elif request.method == 'DELETE':
            # Remove exercise from favorites
            exercise_id = request.args.get('exercise_id', type=int)
            
            if not exercise_id:
                return jsonify({
                    'success': False,
                    'error': 'exercise_id is required'
                }), 400
            
            # Here you would remove from your database
            # For now, return success
            return jsonify({
                'success': True,
                'message': f'Exercise {exercise_id} removed from favorites'
            })
            
    except Exception as e:
        print(f"❌ Error managing favorite exercises: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@wger_bp.route('/user/workout-plans', methods=['GET', 'POST'])
@jwt_required()
def user_workout_plans():
    """Manage user's workout plans using wger exercises"""
    try:
        user_id = get_jwt_identity()
        
        if request.method == 'GET':
            # Get user's workout plans
            return jsonify({
                'success': True,
                'workout_plans': []
            })
        
        elif request.method == 'POST':
            # Create new workout plan
            data = request.get_json()
            plan_name = data.get('name')
            exercise_ids = data.get('exercise_ids', [])
            
            if not plan_name or not exercise_ids:
                return jsonify({
                    'success': False,
                    'error': 'name and exercise_ids are required'
                }), 400
            
            # Here you would save to your database
            return jsonify({
                'success': True,
                'message': f'Workout plan "{plan_name}" created with {len(exercise_ids)} exercises'
            })
            
    except Exception as e:
        print(f"❌ Error managing workout plans: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500