# Create this file: backend/routes/exercises.py

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from services.wger_api import wger_service
import json

exercises_bp = Blueprint('exercises', __name__)

def get_db():
    """Get database instance from current app"""
    return current_app.extensions['sqlalchemy']

def get_current_user_id():
    """Get current user ID from JWT token"""
    current_user_id_str = get_jwt_identity()
    return int(current_user_id_str) if current_user_id_str else None

@exercises_bp.route('/test', methods=['GET'])
def test_exercises_routes():
    """Test endpoint for exercise routes"""
    return jsonify({
        'message': 'Exercise routes are working!',
        'timestamp': str(datetime.utcnow()),
        'endpoints': {
            'wger_test': 'GET /api/exercises/wger/test',
            'search': 'GET /api/exercises/search?q=query',
            'categories': 'GET /api/exercises/categories',
            'muscles': 'GET /api/exercises/muscles',
            'equipment': 'GET /api/exercises/equipment',
            'sync_from_wger': 'POST /api/exercises/sync',
            'list': 'GET /api/exercises/',
            'create_custom': 'POST /api/exercises/custom'
        }
    }), 200

@exercises_bp.route('/wger/test', methods=['GET'])
def test_wger_connection():
    """Test connection to wger API"""
    result = wger_service.test_connection()
    return jsonify(result), 200 if result['success'] else 500

@exercises_bp.route('/wger/categories', methods=['GET'])
def get_wger_categories():
    """Get exercise categories from wger API"""
    try:
        categories = wger_service.get_exercise_categories()
        return jsonify({
            'categories': categories,
            'count': len(categories),
            'message': 'Categories retrieved successfully'
        }), 200
    except Exception as e:
        return jsonify({'message': f'Failed to get categories: {str(e)}'}), 500

@exercises_bp.route('/wger/muscles', methods=['GET'])
def get_wger_muscles():
    """Get muscle groups from wger API"""
    try:
        muscles = wger_service.get_muscles()
        return jsonify({
            'muscles': muscles,
            'count': len(muscles),
            'message': 'Muscle groups retrieved successfully'
        }), 200
    except Exception as e:
        return jsonify({'message': f'Failed to get muscle groups: {str(e)}'}), 500

@exercises_bp.route('/wger/equipment', methods=['GET'])
def get_wger_equipment():
    """Get equipment types from wger API"""
    try:
        equipment = wger_service.get_equipment()
        return jsonify({
            'equipment': equipment,
            'count': len(equipment),
            'message': 'Equipment retrieved successfully'
        }), 200
    except Exception as e:
        return jsonify({'message': f'Failed to get equipment: {str(e)}'}), 500

@exercises_bp.route('/wger/exercises', methods=['GET'])
def get_wger_exercises():
    """Get exercises from wger API with optional filtering"""
    try:
        # Get query parameters
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        category = request.args.get('category', type=int)
        muscle = request.args.get('muscle', type=int)
        equipment = request.args.get('equipment', type=int)
        
        data = wger_service.get_exercises(
            limit=limit,
            offset=offset,
            category=category,
            muscle=muscle,
            equipment=equipment
        )
        
        return jsonify({
            'exercises': data.get('results', []),
            'count': data.get('count', 0),
            'next': data.get('next'),
            'previous': data.get('previous'),
            'message': 'Exercises retrieved successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get exercises: {str(e)}'}), 500

@exercises_bp.route('/wger/search', methods=['GET'])
def search_wger_exercises():
    """Search exercises in wger API"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'message': 'Search query is required'}), 400
        
        limit = request.args.get('limit', 20, type=int)
        exercises = wger_service.search_exercises(query, limit)
        
        return jsonify({
            'exercises': exercises,
            'count': len(exercises),
            'query': query,
            'message': f'Found {len(exercises)} exercises for "{query}"'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Search failed: {str(e)}'}), 500

@exercises_bp.route('/wger/martial-arts', methods=['GET'])
def get_martial_arts_exercises():
    """Get exercises relevant for martial arts training"""
    try:
        exercises = wger_service.get_martial_arts_relevant_exercises()
        
        return jsonify({
            'exercises': exercises,
            'count': len(exercises),
            'message': 'Martial arts relevant exercises retrieved successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get martial arts exercises: {str(e)}'}), 500

@exercises_bp.route('/sync', methods=['POST'])
@jwt_required()
def sync_exercises_from_wger():
    """Sync exercises from wger to local database"""
    try:
        data = request.get_json()
        sync_type = data.get('type', 'martial_arts')  # 'all', 'martial_arts', 'categories'
        limit = data.get('limit', 100)
        
        db = get_db()
        Exercise = current_app.Exercise
        ExerciseCategory = current_app.ExerciseCategory
        
        print(f"🔄 Starting exercise sync: type={sync_type}, limit={limit}")
        
        # Sync categories first
        categories = wger_service.get_exercise_categories()
        synced_categories = 0
        
        for cat_data in categories:
            existing_cat = ExerciseCategory.query.filter_by(wger_id=cat_data['id']).first()
            if not existing_cat:
                new_category = ExerciseCategory(
                    wger_id=cat_data['id'],
                    name=cat_data['name'],
                    description=cat_data.get('description', '')
                )
                db.session.add(new_category)
                synced_categories += 1
        
        # Sync exercises based on type
        if sync_type == 'martial_arts':
            exercises = wger_service.get_martial_arts_relevant_exercises()
        else:
            exercises_data = wger_service.get_exercises(limit=limit)
            exercises = exercises_data.get('results', [])
        
        synced_exercises = 0
        
        for ex_data in exercises[:limit]:
            existing_exercise = Exercise.query.filter_by(wger_id=ex_data['id']).first()
            if existing_exercise:
                continue  # Skip if already exists
            
            # Get detailed exercise info
            detailed_exercise = wger_service.get_exercise_details(ex_data['id'])
            if not detailed_exercise:
                continue
            
            # Find category
            category = None
            if ex_data.get('category'):
                category = ExerciseCategory.query.filter_by(wger_id=ex_data['category']).first()
            
            # Create new exercise
            new_exercise = Exercise(
                wger_id=ex_data['id'],
                name=detailed_exercise.name,
                description=detailed_exercise.description,
                category_id=category.id if category else None,
                martial_arts_relevant=True if sync_type == 'martial_arts' else False,
                is_custom=False,
                license_author=detailed_exercise.license_author
            )
            
            # Set JSON fields
            new_exercise.set_instructions(detailed_exercise.instructions)
            new_exercise.set_primary_muscles(detailed_exercise.muscles)
            new_exercise.set_secondary_muscles(detailed_exercise.muscles_secondary)
            new_exercise.set_equipment_needed(detailed_exercise.equipment)
            
            db.session.add(new_exercise)
            synced_exercises += 1
        
        # Commit changes
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully synced {synced_exercises} exercises and {synced_categories} categories',
            'synced_exercises': synced_exercises,
            'synced_categories': synced_categories,
            'sync_type': sync_type
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Exercise sync failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Sync failed: {str(e)}'}), 500

@exercises_bp.route('/', methods=['GET'])
def list_exercises():
    """Get all exercises from local database with filtering"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category_id = request.args.get('category', type=int)
        martial_arts_only = request.args.get('martial_arts', 'false').lower() == 'true'
        search = request.args.get('search', '').strip()
        
        Exercise = current_app.Exercise
        query = Exercise.query
        
        # Apply filters
        if category_id:
            query = query.filter(Exercise.category_id == category_id)
        
        if martial_arts_only:
            query = query.filter(Exercise.martial_arts_relevant == True)
        
        if search:
            query = query.filter(Exercise.name.contains(search))
        
        # Paginate results
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        exercises = [exercise.to_dict() for exercise in pagination.items]
        
        return jsonify({
            'exercises': exercises,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'filters': {
                'category_id': category_id,
                'martial_arts_only': martial_arts_only,
                'search': search
            },
            'message': f'Found {len(exercises)} exercises'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to list exercises: {str(e)}'}), 500

@exercises_bp.route('/<int:exercise_id>', methods=['GET'])
def get_exercise_details(exercise_id):
    """Get detailed information for a specific exercise"""
    try:
        Exercise = current_app.Exercise
        exercise = Exercise.query.get(exercise_id)
        
        if not exercise:
            return jsonify({'message': 'Exercise not found'}), 404
        
        return jsonify({
            'exercise': exercise.to_dict(),
            'message': 'Exercise retrieved successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get exercise: {str(e)}'}), 500

@exercises_bp.route('/custom', methods=['POST'])
@jwt_required()
def create_custom_exercise():
    """Create a custom exercise"""
    try:
        current_user_id = get_current_user_id()
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'message': 'Exercise name is required'}), 400
        
        db = get_db()
        Exercise = current_app.Exercise
        ExerciseCategory = current_app.ExerciseCategory
        
        # Get or create category
        category = None
        if data.get('category_id'):
            category = ExerciseCategory.query.get(data['category_id'])
        elif data.get('category_name'):
            category = ExerciseCategory.query.filter_by(name=data['category_name']).first()
            if not category:
                # Create new category
                category = ExerciseCategory(
                    wger_id=0,  # Custom category
                    name=data['category_name'],
                    description=f"Custom category created by user"
                )
                db.session.add(category)
                db.session.flush()  # Get the ID
        
        # Create custom exercise
        custom_exercise = Exercise(
            name=data['name'],
            description=data.get('description', ''),
            category_id=category.id if category else None,
            martial_arts_relevant=data.get('martial_arts_relevant', True),
            difficulty_level=data.get('difficulty_level', 'beginner'),
            is_custom=True,
            created_by_user_id=current_user_id
        )
        
        # Set JSON fields
        if data.get('instructions'):
            custom_exercise.set_instructions(data['instructions'])
        if data.get('primary_muscles'):
            custom_exercise.set_primary_muscles(data['primary_muscles'])
        if data.get('secondary_muscles'):
            custom_exercise.set_secondary_muscles(data['secondary_muscles'])
        if data.get('equipment_needed'):
            custom_exercise.set_equipment_needed(data['equipment_needed'])
        
        db.session.add(custom_exercise)
        db.session.commit()
        
        print(f"✅ Created custom exercise: {custom_exercise.name}")
        
        return jsonify({
            'exercise': custom_exercise.to_dict(),
            'message': 'Custom exercise created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Failed to create custom exercise: {str(e)}")
        return jsonify({'message': f'Failed to create exercise: {str(e)}'}), 500

@exercises_bp.route('/custom/<int:exercise_id>', methods=['PUT'])
@jwt_required()
def update_custom_exercise(exercise_id):
    """Update a custom exercise (only by creator)"""
    try:
        current_user_id = get_current_user_id()
        data = request.get_json()
        
        db = get_db()
        Exercise = current_app.Exercise
        
        exercise = Exercise.query.get(exercise_id)
        if not exercise:
            return jsonify({'message': 'Exercise not found'}), 404
        
        if not exercise.is_custom:
            return jsonify({'message': 'Cannot modify non-custom exercises'}), 403
        
        if exercise.created_by_user_id != current_user_id:
            return jsonify({'message': 'Can only modify your own custom exercises'}), 403
        
        # Update fields
        if 'name' in data:
            exercise.name = data['name']
        if 'description' in data:
            exercise.description = data['description']
        if 'martial_arts_relevant' in data:
            exercise.martial_arts_relevant = data['martial_arts_relevant']
        if 'difficulty_level' in data:
            exercise.difficulty_level = data['difficulty_level']
        
        # Update JSON fields
        if 'instructions' in data:
            exercise.set_instructions(data['instructions'])
        if 'primary_muscles' in data:
            exercise.set_primary_muscles(data['primary_muscles'])
        if 'secondary_muscles' in data:
            exercise.set_secondary_muscles(data['secondary_muscles'])
        if 'equipment_needed' in data:
            exercise.set_equipment_needed(data['equipment_needed'])
        
        exercise.last_updated = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'exercise': exercise.to_dict(),
            'message': 'Exercise updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to update exercise: {str(e)}'}), 500

@exercises_bp.route('/custom/<int:exercise_id>', methods=['DELETE'])
@jwt_required()
def delete_custom_exercise(exercise_id):
    """Delete a custom exercise (only by creator)"""
    try:
        current_user_id = get_current_user_id()
        
        db = get_db()
        Exercise = current_app.Exercise
        
        exercise = Exercise.query.get(exercise_id)
        if not exercise:
            return jsonify({'message': 'Exercise not found'}), 404
        
        if not exercise.is_custom:
            return jsonify({'message': 'Cannot delete non-custom exercises'}), 403
        
        if exercise.created_by_user_id != current_user_id:
            return jsonify({'message': 'Can only delete your own custom exercises'}), 403
        
        exercise_name = exercise.name
        db.session.delete(exercise)
        db.session.commit()
        
        return jsonify({
            'message': f'Custom exercise "{exercise_name}" deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to delete exercise: {str(e)}'}), 500

@exercises_bp.route('/categories', methods=['GET'])
def list_exercise_categories():
    """Get all exercise categories from local database"""
    try:
        ExerciseCategory = current_app.ExerciseCategory
        categories = ExerciseCategory.query.all()
        
        return jsonify({
            'categories': [cat.to_dict() for cat in categories],
            'count': len(categories),
            'message': 'Categories retrieved successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get categories: {str(e)}'}), 500

@exercises_bp.route('/search', methods=['GET'])
def search_exercises():
    """Search exercises in local database"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'message': 'Search query is required'}), 400
        
        limit = request.args.get('limit', 20, type=int)
        martial_arts_only = request.args.get('martial_arts', 'false').lower() == 'true'
        
        Exercise = current_app.Exercise
        search_query = Exercise.query.filter(Exercise.name.contains(query))
        
        if martial_arts_only:
            search_query = search_query.filter(Exercise.martial_arts_relevant == True)
        
        exercises = search_query.limit(limit).all()
        
        return jsonify({
            'exercises': [ex.to_dict() for ex in exercises],
            'count': len(exercises),
            'query': query,
            'martial_arts_only': martial_arts_only,
            'message': f'Found {len(exercises)} exercises for "{query}"'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Search failed: {str(e)}'}), 500

@exercises_bp.route('/stats', methods=['GET'])
def get_exercise_stats():
    """Get exercise database statistics"""
    try:
        Exercise = current_app.Exercise
        ExerciseCategory = current_app.ExerciseCategory
        
        total_exercises = Exercise.query.count()
        martial_arts_exercises = Exercise.query.filter(Exercise.martial_arts_relevant == True).count()
        custom_exercises = Exercise.query.filter(Exercise.is_custom == True).count()
        wger_exercises = Exercise.query.filter(Exercise.is_custom == False).count()
        total_categories = ExerciseCategory.query.count()
        
        return jsonify({
            'stats': {
                'total_exercises': total_exercises,
                'martial_arts_exercises': martial_arts_exercises,
                'custom_exercises': custom_exercises,
                'wger_exercises': wger_exercises,
                'total_categories': total_categories
            },
            'message': 'Exercise statistics retrieved successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get stats: {str(e)}'}), 500