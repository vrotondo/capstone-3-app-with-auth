from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import json

workout_bp = Blueprint('workout', __name__)

def get_db():
    """Get db from current app to avoid circular imports"""
    return current_app.extensions['sqlalchemy']

def get_models():
    """Get models from current app"""
    return (
        current_app.FavoriteExercise,
        current_app.WorkoutPlan, 
        current_app.WorkoutPlanExercise
    )

# ==================== TEST ENDPOINT ====================

@workout_bp.route('/test', methods=['GET'])
def test_workout_routes():
    """Test endpoint for workout routes"""
    return jsonify({
        'message': 'Workout routes are working!',
        'endpoints': {
            'favorites': 'GET /api/workout/favorites',
            'add_favorite': 'POST /api/workout/favorites',
            'remove_favorite': 'DELETE /api/workout/favorites/<exercise_id>',
            'check_favorite': 'GET /api/workout/favorites/check/<exercise_id>',
            'workout_plans': 'GET /api/workout/plans',
            'create_plan': 'POST /api/workout/plans',
            'add_to_workout': 'POST /api/workout/plans/<plan_id>/exercises'
        }
    }), 200

# ==================== FAVORITES ENDPOINTS ====================

@workout_bp.route('/favorites', methods=['GET'])
@jwt_required()
def get_user_favorites():
    """Get all favorite exercises for the current user"""
    try:
        user_id = get_jwt_identity()
        FavoriteExercise, WorkoutPlan, WorkoutPlanExercise = get_models()
        
        print(f"🔍 Getting favorites for user {user_id}")
        
        favorites = FavoriteExercise.query.filter_by(user_id=user_id).order_by(FavoriteExercise.created_at.desc()).all()
        
        print(f"✅ Found {len(favorites)} favorites for user {user_id}")
        
        return jsonify({
            'success': True,
            'count': len(favorites),
            'favorites': [fav.to_dict() for fav in favorites]
        })
    except Exception as e:
        print(f"❌ Error getting favorites: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@workout_bp.route('/favorites', methods=['POST'])
@jwt_required()
def add_to_favorites():
    """Add an exercise to user's favorites"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        FavoriteExercise, WorkoutPlan, WorkoutPlanExercise = get_models()
        db = get_db()
        
        print(f"🔍 Adding to favorites for user {user_id}: {data}")
        
        exercise_id = data.get('exercise_id')
        exercise_name = data.get('exercise_name')
        exercise_category = data.get('exercise_category')
        exercise_muscles = data.get('exercise_muscles', [])
        exercise_equipment = data.get('exercise_equipment', [])
        
        if not exercise_id:
            return jsonify({
                'success': False,
                'error': 'exercise_id is required'
            }), 400
        
        # Check if already favorited
        existing = FavoriteExercise.query.filter_by(
            user_id=user_id, 
            exercise_id=exercise_id
        ).first()
        
        if existing:
            return jsonify({
                'success': False,
                'error': 'Exercise already in favorites'
            }), 400
        
        # Create new favorite
        favorite = FavoriteExercise(
            user_id=user_id,
            exercise_id=exercise_id,
            exercise_name=exercise_name,
            exercise_category=exercise_category,
            exercise_muscles=json.dumps(exercise_muscles),
            exercise_equipment=json.dumps(exercise_equipment)
        )
        
        db.session.add(favorite)
        db.session.commit()
        
        print(f"✅ Added exercise {exercise_id} to favorites for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Exercise added to favorites',
            'favorite': favorite.to_dict()
        })
        
    except Exception as e:
        if 'db' in locals():
            db.session.rollback()
        print(f"❌ Error adding to favorites: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@workout_bp.route('/favorites/<int:exercise_id>', methods=['DELETE'])
@jwt_required()
def remove_from_favorites(exercise_id):
    """Remove an exercise from user's favorites"""
    try:
        user_id = get_jwt_identity()
        FavoriteExercise, WorkoutPlan, WorkoutPlanExercise = get_models()
        db = get_db()
        
        print(f"🔍 Removing exercise {exercise_id} from favorites for user {user_id}")
        
        favorite = FavoriteExercise.query.filter_by(
            user_id=user_id,
            exercise_id=exercise_id
        ).first()
        
        if not favorite:
            return jsonify({
                'success': False,
                'error': 'Exercise not found in favorites'
            }), 404
        
        db.session.delete(favorite)
        db.session.commit()
        
        print(f"✅ Removed exercise {exercise_id} from favorites for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Exercise removed from favorites'
        })
        
    except Exception as e:
        if 'db' in locals():
            db.session.rollback()
        print(f"❌ Error removing from favorites: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@workout_bp.route('/favorites/check/<int:exercise_id>', methods=['GET'])
@jwt_required()
def check_favorite_status(exercise_id):
    """Check if an exercise is favorited by the user"""
    try:
        user_id = get_jwt_identity()
        FavoriteExercise, WorkoutPlan, WorkoutPlanExercise = get_models()
        
        favorite = FavoriteExercise.query.filter_by(
            user_id=user_id,
            exercise_id=exercise_id
        ).first()
        
        return jsonify({
            'success': True,
            'is_favorited': favorite is not None
        })
        
    except Exception as e:
        print(f"❌ Error checking favorite status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== WORKOUT PLANS ENDPOINTS ====================

@workout_bp.route('/plans', methods=['GET'])
@jwt_required()
def get_workout_plans():
    """Get all workout plans for the current user"""
    try:
        user_id = get_jwt_identity()
        FavoriteExercise, WorkoutPlan, WorkoutPlanExercise = get_models()
        
        print(f"🔍 Getting workout plans for user {user_id}")
        
        plans = WorkoutPlan.query.filter_by(user_id=user_id, is_active=True).order_by(WorkoutPlan.updated_at.desc()).all()
        
        print(f"✅ Found {len(plans)} workout plans for user {user_id}")
        
        return jsonify({
            'success': True,
            'count': len(plans),
            'workout_plans': [plan.to_dict() for plan in plans]
        })
    except Exception as e:
        print(f"❌ Error getting workout plans: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@workout_bp.route('/plans', methods=['POST'])
@jwt_required()
def create_workout_plan():
    """Create a new workout plan"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        FavoriteExercise, WorkoutPlan, WorkoutPlanExercise = get_models()
        db = get_db()
        
        name = data.get('name')
        description = data.get('description', '')
        
        print(f"🔍 Creating workout plan for user {user_id}: {name}")
        
        if not name:
            return jsonify({
                'success': False,
                'error': 'Workout plan name is required'
            }), 400
        
        # Create new workout plan
        plan = WorkoutPlan(
            user_id=user_id,
            name=name,
            description=description
        )
        
        db.session.add(plan)
        db.session.commit()
        
        print(f"✅ Created workout plan '{name}' for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Workout plan created',
            'workout_plan': plan.to_dict()
        })
        
    except Exception as e:
        if 'db' in locals():
            db.session.rollback()
        print(f"❌ Error creating workout plan: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@workout_bp.route('/plans/<int:plan_id>/exercises', methods=['POST'])
@jwt_required()
def add_exercise_to_workout(plan_id):
    """Add an exercise to a workout plan"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        FavoriteExercise, WorkoutPlan, WorkoutPlanExercise = get_models()
        db = get_db()
        
        print(f"🔍 Adding exercise to workout plan {plan_id} for user {user_id}")
        
        # Verify plan ownership
        plan = WorkoutPlan.query.filter_by(
            id=plan_id,
            user_id=user_id,
            is_active=True
        ).first()
        
        if not plan:
            return jsonify({
                'success': False,
                'error': 'Workout plan not found'
            }), 404
        
        exercise_id = data.get('exercise_id')
        if not exercise_id:
            return jsonify({
                'success': False,
                'error': 'exercise_id is required'
            }), 400
        
        # Get next order number - FIXED: Import func from sqlalchemy
        from sqlalchemy import func
        max_order = db.session.query(func.max(WorkoutPlanExercise.order_in_workout)).filter_by(workout_plan_id=plan_id).scalar() or 0
        
        # Create workout exercise
        workout_exercise = WorkoutPlanExercise(
            workout_plan_id=plan_id,
            exercise_id=exercise_id,
            exercise_name=data.get('exercise_name'),
            exercise_category=data.get('exercise_category'),
            exercise_muscles=json.dumps(data.get('exercise_muscles', [])),
            exercise_equipment=json.dumps(data.get('exercise_equipment', [])),
            sets=data.get('sets', 3),
            reps=data.get('reps', '10-12'),
            rest_seconds=data.get('rest_seconds', 60),
            notes=data.get('notes', ''),
            order_in_workout=max_order + 1
        )
        
        db.session.add(workout_exercise)
        db.session.commit()
        
        print(f"✅ Added exercise {exercise_id} to workout plan {plan_id}")
        
        return jsonify({
            'success': True,
            'message': 'Exercise added to workout',
            'workout_exercise': workout_exercise.to_dict()
        })
        
    except Exception as e:
        if 'db' in locals():
            db.session.rollback()
        print(f"❌ Error adding exercise to workout: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@workout_bp.route('/plans/<int:plan_id>', methods=['PUT'])
@jwt_required()
def update_workout_plan(plan_id):
    """Update a workout plan"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        FavoriteExercise, WorkoutPlan, WorkoutPlanExercise = get_models()
        db = get_db()
        
        # Verify plan ownership
        plan = WorkoutPlan.query.filter_by(
            id=plan_id,
            user_id=user_id,
            is_active=True
        ).first()
        
        if not plan:
            return jsonify({
                'success': False,
                'error': 'Workout plan not found'
            }), 404
        
        # Update plan fields
        if 'name' in data:
            plan.name = data['name']
        if 'description' in data:
            plan.description = data['description']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Workout plan updated',
            'workout_plan': plan.to_dict()
        })
        
    except Exception as e:
        if 'db' in locals():
            db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@workout_bp.route('/plans/<int:plan_id>', methods=['DELETE'])
@jwt_required()
def delete_workout_plan(plan_id):
    """Delete a workout plan"""
    try:
        user_id = get_jwt_identity()
        FavoriteExercise, WorkoutPlan, WorkoutPlanExercise = get_models()
        db = get_db()
        
        # Verify plan ownership
        plan = WorkoutPlan.query.filter_by(
            id=plan_id,
            user_id=user_id,
            is_active=True
        ).first()
        
        if not plan:
            return jsonify({
                'success': False,
                'error': 'Workout plan not found'
            }), 404
        
        # Soft delete by setting is_active to False
        plan.is_active = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Workout plan deleted'
        })
        
    except Exception as e:
        if 'db' in locals():
            db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@workout_bp.route('/plans/<int:plan_id>/exercises/<int:exercise_id>', methods=['DELETE'])
@jwt_required()
def remove_exercise_from_workout(plan_id, exercise_id):
    """Remove an exercise from a workout plan"""
    try:
        user_id = get_jwt_identity()
        FavoriteExercise, WorkoutPlan, WorkoutPlanExercise = get_models()
        db = get_db()
        
        # Verify plan ownership
        plan = WorkoutPlan.query.filter_by(
            id=plan_id,
            user_id=user_id,
            is_active=True
        ).first()
        
        if not plan:
            return jsonify({
                'success': False,
                'error': 'Workout plan not found'
            }), 404
        
        # Find and remove the exercise
        workout_exercise = WorkoutPlanExercise.query.filter_by(
            workout_plan_id=plan_id,
            exercise_id=exercise_id
        ).first()
        
        if not workout_exercise:
            return jsonify({
                'success': False,
                'error': 'Exercise not found in workout plan'
            }), 404
        
        db.session.delete(workout_exercise)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Exercise removed from workout plan'
        })
        
    except Exception as e:
        if 'db' in locals():
            db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500