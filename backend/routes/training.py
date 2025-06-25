from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date
from models.training import TrainingSession, TechniqueProgress, db
from models.user import User

training_bp = Blueprint('training', __name__)

# Training Sessions Routes
@training_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_training_sessions():
    """Get all training sessions for the current user"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get query parameters
        limit = request.args.get('limit', type=int)
        style = request.args.get('style')
        
        # Build query
        query = TrainingSession.query.filter_by(user_id=current_user_id)
        
        if style:
            query = query.filter_by(style=style)
            
        query = query.order_by(TrainingSession.date.desc())
        
        if limit:
            query = query.limit(limit)
            
        sessions = query.all()
        
        return jsonify({
            'sessions': [session.to_dict() for session in sessions],
            'count': len(sessions)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get training sessions error: {str(e)}")
        return jsonify({'message': 'Failed to get training sessions'}), 500

@training_bp.route('/sessions', methods=['POST'])
@jwt_required()
def create_training_session():
    """Create a new training session"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['duration', 'style']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} is required'}), 400
        
        # Validate duration
        try:
            duration = int(data['duration'])
            if duration <= 0:
                return jsonify({'message': 'Duration must be a positive number'}), 400
        except ValueError:
            return jsonify({'message': 'Duration must be a valid number'}), 400
        
        # Parse date if provided
        session_date = None
        if data.get('date'):
            try:
                session_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'message': 'Date must be in YYYY-MM-DD format'}), 400
        
        # Validate intensity level
        intensity_level = data.get('intensity_level', 5)
        if not isinstance(intensity_level, int) or intensity_level < 1 or intensity_level > 10:
            return jsonify({'message': 'Intensity level must be between 1 and 10'}), 400
        
        # Create training session
        session = TrainingSession(
            user_id=current_user_id,
            duration=duration,
            style=data['style'],
            date=session_date,
            techniques_practiced=data.get('techniques_practiced', []),
            notes=data.get('notes'),
            intensity_level=intensity_level,
            energy_before=data.get('energy_before'),
            energy_after=data.get('energy_after'),
            mood=data.get('mood'),
            calories_burned=data.get('calories_burned'),
            avg_heart_rate=data.get('avg_heart_rate'),
            max_heart_rate=data.get('max_heart_rate')
        )
        
        session.save()
        
        return jsonify({
            'message': 'Training session created successfully',
            'session': session.to_dict()
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Create training session error: {str(e)}")
        return jsonify({'message': 'Failed to create training session'}), 500

@training_bp.route('/sessions/<int:session_id>', methods=['GET'])
@jwt_required()
def get_training_session(session_id):
    """Get a specific training session"""
    try:
        current_user_id = get_jwt_identity()
        
        session = TrainingSession.query.filter_by(
            id=session_id, 
            user_id=current_user_id
        ).first()
        
        if not session:
            return jsonify({'message': 'Training session not found'}), 404
        
        return jsonify({'session': session.to_dict()}), 200
        
    except Exception as e:
        current_app.logger.error(f"Get training session error: {str(e)}")
        return jsonify({'message': 'Failed to get training session'}), 500

@training_bp.route('/sessions/<int:session_id>', methods=['PUT'])
@jwt_required()
def update_training_session(session_id):
    """Update a training session"""
    try:
        current_user_id = get_jwt_identity()
        
        session = TrainingSession.query.filter_by(
            id=session_id, 
            user_id=current_user_id
        ).first()
        
        if not session:
            return jsonify({'message': 'Training session not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'duration' in data:
            try:
                duration = int(data['duration'])
                if duration <= 0:
                    return jsonify({'message': 'Duration must be a positive number'}), 400
                session.duration = duration
            except ValueError:
                return jsonify({'message': 'Duration must be a valid number'}), 400
        
        if 'style' in data:
            session.style = data['style']
        
        if 'date' in data:
            try:
                session.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'message': 'Date must be in YYYY-MM-DD format'}), 400
        
        if 'techniques_practiced' in data:
            session.techniques_practiced = data['techniques_practiced']
        
        if 'notes' in data:
            session.notes = data['notes']
        
        if 'intensity_level' in data:
            intensity = data['intensity_level']
            if not isinstance(intensity, int) or intensity < 1 or intensity > 10:
                return jsonify({'message': 'Intensity level must be between 1 and 10'}), 400
            session.intensity_level = intensity
        
        # Update optional fields
        for field in ['energy_before', 'energy_after', 'mood', 'calories_burned', 
                     'avg_heart_rate', 'max_heart_rate']:
            if field in data:
                setattr(session, field, data[field])
        
        session.save()
        
        return jsonify({
            'message': 'Training session updated successfully',
            'session': session.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Update training session error: {str(e)}")
        return jsonify({'message': 'Failed to update training session'}), 500

@training_bp.route('/sessions/<int:session_id>', methods=['DELETE'])
@jwt_required()
def delete_training_session(session_id):
    """Delete a training session"""
    try:
        current_user_id = get_jwt_identity()
        
        session = TrainingSession.query.filter_by(
            id=session_id, 
            user_id=current_user_id
        ).first()
        
        if not session:
            return jsonify({'message': 'Training session not found'}), 404
        
        session.delete()
        
        return jsonify({'message': 'Training session deleted successfully'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Delete training session error: {str(e)}")
        return jsonify({'message': 'Failed to delete training session'}), 500

# Technique Progress Routes
@training_bp.route('/techniques', methods=['GET'])
@jwt_required()
def get_technique_progress():
    """Get technique progress for the current user"""
    try:
        current_user_id = get_jwt_identity()
        style = request.args.get('style')
        
        techniques = TechniqueProgress.get_user_techniques(current_user_id, style)
        
        return jsonify({
            'techniques': [technique.to_dict() for technique in techniques],
            'count': len(techniques)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get technique progress error: {str(e)}")
        return jsonify({'message': 'Failed to get technique progress'}), 500

@training_bp.route('/techniques', methods=['POST'])
@jwt_required()
def create_technique_progress():
    """Create or update technique progress"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['technique_name', 'style']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} is required'}), 400
        
        # Check if technique already exists for this user and style
        existing_technique = TechniqueProgress.query.filter_by(
            user_id=current_user_id,
            technique_name=data['technique_name'],
            style=data['style']
        ).first()
        
        if existing_technique:
            return jsonify({'message': 'Technique already exists for this style'}), 409
        
        # Validate proficiency level
        proficiency_level = data.get('proficiency_level', 1)
        if not isinstance(proficiency_level, int) or proficiency_level < 1 or proficiency_level > 10:
            return jsonify({'message': 'Proficiency level must be between 1 and 10'}), 400
        
        # Create technique progress
        technique = TechniqueProgress(
            user_id=current_user_id,
            technique_name=data['technique_name'],
            style=data['style'],
            proficiency_level=proficiency_level,
            notes=data.get('notes'),
            video_url=data.get('video_url')
        )
        
        technique.save()
        
        return jsonify({
            'message': 'Technique progress created successfully',
            'technique': technique.to_dict()
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Create technique progress error: {str(e)}")
        return jsonify({'message': 'Failed to create technique progress'}), 500

@training_bp.route('/techniques/<int:technique_id>', methods=['PUT'])
@jwt_required()
def update_technique_progress(technique_id):
    """Update technique progress"""
    try:
        current_user_id = get_jwt_identity()
        
        technique = TechniqueProgress.query.filter_by(
            id=technique_id,
            user_id=current_user_id
        ).first()
        
        if not technique:
            return jsonify({'message': 'Technique not found'}), 404
        
        data = request.get_json()
        
        # Update proficiency level and notes if provided
        proficiency_level = data.get('proficiency_level')
        notes = data.get('notes')
        
        if proficiency_level is not None:
            if not isinstance(proficiency_level, int) or proficiency_level < 1 or proficiency_level > 10:
                return jsonify({'message': 'Proficiency level must be between 1 and 10'}), 400
        
        # Use the update_practice method which handles automatic updates
        technique.update_practice(proficiency_level=proficiency_level, notes=notes)
        
        # Update other fields if provided
        if 'video_url' in data:
            technique.video_url = data['video_url']
        
        technique.save()
        
        return jsonify({
            'message': 'Technique progress updated successfully',
            'technique': technique.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Update technique progress error: {str(e)}")
        return jsonify({'message': 'Failed to update technique progress'}), 500

@training_bp.route('/techniques/<int:technique_id>', methods=['DELETE'])
@jwt_required()
def delete_technique_progress(technique_id):
    """Delete technique progress"""
    try:
        current_user_id = get_jwt_identity()
        
        technique = TechniqueProgress.query.filter_by(
            id=technique_id,
            user_id=current_user_id
        ).first()
        
        if not technique:
            return jsonify({'message': 'Technique not found'}), 404
        
        technique.delete()
        
        return jsonify({'message': 'Technique progress deleted successfully'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Delete technique progress error: {str(e)}")
        return jsonify({'message': 'Failed to delete technique progress'}), 500

# Statistics and Analytics Routes
@training_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_training_stats():
    """Get training statistics for the current user"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get all sessions for the user
        sessions = TrainingSession.query.filter_by(user_id=current_user_id).all()
        
        if not sessions:
            return jsonify({
                'total_sessions': 0,
                'total_hours': 0,
                'avg_intensity': 0,
                'styles_practiced': [],
                'recent_sessions': []
            }), 200
        
        # Calculate statistics
        total_sessions = len(sessions)
        total_minutes = sum(session.duration for session in sessions)
        total_hours = round(total_minutes / 60, 2)
        
        # Calculate average intensity
        intensities = [session.intensity_level for session in sessions if session.intensity_level]
        avg_intensity = round(sum(intensities) / len(intensities), 1) if intensities else 0
        
        # Get unique styles
        styles_practiced = list(set(session.style for session in sessions))
        
        # Get recent sessions (last 10)
        recent_sessions = sorted(sessions, key=lambda x: x.date, reverse=True)[:10]
        
        # Calculate weekly/monthly stats
        from datetime import timedelta
        today = date.today()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        this_week_sessions = [s for s in sessions if s.date >= week_ago]
        this_month_sessions = [s for s in sessions if s.date >= month_ago]
        
        return jsonify({
            'total_sessions': total_sessions,
            'total_hours': total_hours,
            'avg_intensity': avg_intensity,
            'styles_practiced': styles_practiced,
            'this_week': {
                'sessions': len(this_week_sessions),
                'hours': round(sum(s.duration for s in this_week_sessions) / 60, 2)
            },
            'this_month': {
                'sessions': len(this_month_sessions),
                'hours': round(sum(s.duration for s in this_month_sessions) / 60, 2)
            },
            'recent_sessions': [session.to_dict() for session in recent_sessions]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get training stats error: {str(e)}")
        return jsonify({'message': 'Failed to get training statistics'}), 500

@training_bp.route('/test', methods=['GET'])
def test_training():
    """Test endpoint for training system"""
    return jsonify({
        'message': 'Training system is working',
        'timestamp': str(datetime.utcnow())
    }), 200