from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import re

user_bp = Blueprint('user', __name__)

def get_db():
    """Get database instance from current app"""
    return current_app.extensions['sqlalchemy']

def get_current_user_id():
    """Get current user ID from JWT token and convert from string to int"""
    current_user_id_str = get_jwt_identity()
    return int(current_user_id_str) if current_user_id_str else None

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    """Get current user profile"""
    try:
        current_user_id = get_current_user_id()
        User = current_app.User
        
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        print(f"📋 Retrieved profile for user: {user.email}")
        
        return jsonify({
            'user': user.to_dict(),
            'message': 'Profile retrieved successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get user profile error: {str(e)}")
        print(f"❌ Get profile error: {str(e)}")
        return jsonify({'message': 'Failed to get profile'}), 500

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_user_profile():
    """Update current user profile"""
    try:
        current_user_id = get_current_user_id()
        User = current_app.User
        db = get_db()
        
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        print(f"🔄 Updating profile for user {user.email} with data: {data}")
        
        # Track what fields are being updated
        updated_fields = []
        
        # Update allowed fields with better error handling
        if 'first_name' in data and data['first_name']:
            user.first_name = data['first_name'].strip()
            updated_fields.append('first_name')
            
        if 'last_name' in data and data['last_name']:
            user.last_name = data['last_name'].strip()
            updated_fields.append('last_name')
            
        # Handle both snake_case and camelCase field names
        martial_art = data.get('martial_art') or data.get('martialArt') or data.get('primaryStyle')
        if martial_art:
            user.primary_style = martial_art
            updated_fields.append('primary_style')
            
        current_belt = data.get('current_belt') or data.get('currentBelt') or data.get('belt_rank')
        if current_belt:
            user.belt_rank = current_belt
            updated_fields.append('belt_rank')
            
        if 'dojo' in data:
            user.dojo = data['dojo']
            updated_fields.append('dojo')
            
        # Additional profile fields
        if 'bio' in data:
            user.bio = data['bio']
            updated_fields.append('bio')
            
        if 'location' in data:
            user.location = data['location']
            updated_fields.append('location')
            
        # Handle years training
        years_training = data.get('years_training') or data.get('yearsTraining')
        if years_training is not None:
            try:
                user.years_training = int(years_training)
                updated_fields.append('years_training')
            except (ValueError, TypeError):
                print(f"⚠️ Invalid years_training value: {years_training}")
        
        if 'instructor' in data:
            user.instructor = data['instructor']
            updated_fields.append('instructor')
            
        if 'goals' in data:
            user.goals = data['goals']
            updated_fields.append('goals')
        
        # Handle email update with validation
        if 'email' in data and data['email']:
            new_email = data['email'].strip().lower()
            if new_email != user.email:
                # Basic email validation
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, new_email):
                    return jsonify({'message': 'Invalid email format'}), 400
                
                # Check if email is already taken
                existing_user = User.query.filter_by(email=new_email).first()
                if existing_user and existing_user.id != user.id:
                    return jsonify({'message': 'Email already in use'}), 409
                
                user.email = new_email
                updated_fields.append('email')
        
        # Handle password update
        if 'password' in data and data['password']:
            if len(data['password']) < 6:
                return jsonify({'message': 'Password must be at least 6 characters long'}), 400
            user.set_password(data['password'])
            updated_fields.append('password')
        
        # Update timestamp
        user.updated_at = datetime.utcnow()
        
        # Save changes
        try:
            db.session.commit()
            print(f"✅ Successfully updated fields: {', '.join(updated_fields)}")
        except Exception as save_error:
            db.session.rollback()
            print(f"❌ Database save error: {str(save_error)}")
            return jsonify({'message': f'Failed to save profile: {str(save_error)}'}), 500
        
        return jsonify({
            'message': f'Profile updated successfully. Updated: {", ".join(updated_fields)}',
            'user': user.to_dict(),
            'updated_fields': updated_fields
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Update profile error: {str(e)}")
        print(f"❌ Update profile error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Failed to update profile: {str(e)}'}), 500

@user_bp.route('/test', methods=['GET'])
def test_user_routes():
    """Test endpoint for user routes"""
    return jsonify({
        'message': 'User routes are working!',
        'timestamp': str(datetime.utcnow()),
        'endpoints': {
            'profile_get': 'GET /api/user/profile',
            'profile_update': 'PUT /api/user/profile'
        }
    }), 200