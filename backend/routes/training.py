from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date

training_bp = Blueprint('training', __name__)

def get_db():
    """Get database instance from current app"""
    return current_app.extensions['sqlalchemy']

# Training Sessions Routes
@training_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_training_sessions():
    """Get all training sessions for the current user"""
    try:
        current_user_id = get_jwt_identity()
        print(f"🔍 Getting sessions for user ID: {current_user_id}")
        
        TrainingSession = current_app.TrainingSession
        
        # Get query parameters
        limit = request.args.get('limit', type=int)
        style = request.args.get('style')
        date_from = request.args.get('from')  # YYYY-MM-DD format
        date_to = request.args.get('to')      # YYYY-MM-DD format
        
        print(f"📋 Query params - limit: {limit}, style: {style}, from: {date_from}, to: {date_to}")
        
        # Build query
        query = TrainingSession.query.filter_by(user_id=current_user_id)
        
        if style:
            query = query.filter_by(style=style)
            
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
                query = query.filter(TrainingSession.date >= from_date)
            except ValueError:
                return jsonify({'message': 'Invalid from date format. Use YYYY-MM-DD'}), 400
                
        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
                query = query.filter(TrainingSession.date <= to_date)
            except ValueError:
                return jsonify({'message': 'Invalid to date format. Use YYYY-MM-DD'}), 400
            
        query = query.order_by(TrainingSession.date.desc())
        
        if limit:
            query = query.limit(limit)
            
        sessions = query.all()
        print(f"✅ Found {len(sessions)} sessions")
        
        return jsonify({
            'sessions': [session.to_dict() for session in sessions],
            'count': len(sessions),
            'message': 'Training sessions retrieved successfully'
        }), 200
        
    except Exception as e:
        print(f"❌ Get training sessions error: {str(e)}")
        import traceback
        traceback.print_exc()
        current_app.logger.error(f"Get training sessions error: {str(e)}")
        return jsonify({'message': f'Failed to get training sessions: {str(e)}'}), 500

@training_bp.route('/sessions', methods=['POST'])
@jwt_required()
def create_training_session():
    """Create a new training session"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        TrainingSession = current_app.TrainingSession
        db = get_db()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
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
        except (ValueError, TypeError):
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
        
        # Validate energy levels if provided
        for field in ['energy_before', 'energy_after']:
            if data.get(field) is not None:
                energy = data[field]
                if not isinstance(energy, int) or energy < 1 or energy > 10:
                    return jsonify({'message': f'{field} must be between 1 and 10'}), 400
        
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
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'message': 'Training session created successfully',
            'session': session.to_dict()
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Create training session error: {str(e)}")
        db = get_db()
        db.session.rollback()
        return jsonify({'message': 'Failed to create training session'}), 500

@training_bp.route('/sessions/<int:session_id>', methods=['GET'])
@jwt_required()
def get_training_session(session_id):
    """Get a specific training session"""
    try:
        current_user_id = get_jwt_identity()
        TrainingSession = current_app.TrainingSession
        
        session = TrainingSession.query.filter_by(
            id=session_id, 
            user_id=current_user_id
        ).first()
        
        if not session:
            return jsonify({'message': 'Training session not found'}), 404
        
        return jsonify({
            'session': session.to_dict(),
            'message': 'Training session retrieved successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get training session error: {str(e)}")
        return jsonify({'message': 'Failed to get training session'}), 500

@training_bp.route('/sessions/<int:session_id>', methods=['PUT'])
@jwt_required()
def update_training_session(session_id):
    """Update a training session"""
    try:
        current_user_id = get_jwt_identity()
        TrainingSession = current_app.TrainingSession
        db = get_db()
        
        session = TrainingSession.query.filter_by(
            id=session_id, 
            user_id=current_user_id
        ).first()
        
        if not session:
            return jsonify({'message': 'Training session not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        # Update fields
        if 'duration' in data:
            try:
                duration = int(data['duration'])
                if duration <= 0:
                    return jsonify({'message': 'Duration must be a positive number'}), 400
                session.duration = duration
            except (ValueError, TypeError):
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
        
        session.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Training session updated successfully',
            'session': session.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Update training session error: {str(e)}")
        db = get_db()
        db.session.rollback()
        return jsonify({'message': 'Failed to update training session'}), 500

@training_bp.route('/sessions/<int:session_id>', methods=['DELETE'])
@jwt_required()
def delete_training_session(session_id):
    """Delete a training session"""
    try:
        current_user_id = get_jwt_identity()
        TrainingSession = current_app.TrainingSession
        db = get_db()
        
        session = TrainingSession.query.filter_by(
            id=session_id, 
            user_id=current_user_id
        ).first()
        
        if not session:
            return jsonify({'message': 'Training session not found'}), 404
        
        db.session.delete(session)
        db.session.commit()
        
        return jsonify({'message': 'Training session deleted successfully'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Delete training session error: {str(e)}")
        db = get_db()
        db.session.rollback()
        return jsonify({'message': 'Failed to delete training session'}), 500

# Technique Progress Routes
@training_bp.route('/techniques', methods=['GET'])
@jwt_required()
def get_technique_progress():
    """Get technique progress for the current user"""
    try:
        current_user_id = get_jwt_identity()
        TechniqueProgress = current_app.TechniqueProgress
        
        style = request.args.get('style')
        mastery_status = request.args.get('status')  # learning, practicing, competent, mastery
        
        query = TechniqueProgress.query.filter_by(user_id=current_user_id)
        
        if style:
            query = query.filter_by(style=style)
            
        if mastery_status:
            query = query.filter_by(mastery_status=mastery_status)
        
        techniques = query.order_by(TechniqueProgress.technique_name).all()
        
        return jsonify({
            'techniques': [technique.to_dict() for technique in techniques],
            'count': len(techniques),
            'message': 'Techniques retrieved successfully'
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
        
        TechniqueProgress = current_app.TechniqueProgress
        db = get_db()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
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
        
        db.session.add(technique)
        db.session.commit()
        
        return jsonify({
            'message': 'Technique progress created successfully',
            'technique': technique.to_dict()
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Create technique progress error: {str(e)}")
        db = get_db()
        db.session.rollback()
        return jsonify({'message': 'Failed to create technique progress'}), 500

@training_bp.route('/techniques/<int:technique_id>', methods=['PUT'])
@jwt_required()
def update_technique_progress(technique_id):
    """Update technique progress"""
    try:
        current_user_id = get_jwt_identity()
        TechniqueProgress = current_app.TechniqueProgress
        db = get_db()
        
        technique = TechniqueProgress.query.filter_by(
            id=technique_id,
            user_id=current_user_id
        ).first()
        
        if not technique:
            return jsonify({'message': 'Technique not found'}), 404
        
        db.session.delete(technique)
        db.session.commit()
        
        return jsonify({'message': 'Technique progress deleted successfully'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Delete technique progress error: {str(e)}")
        db = get_db()
        db.session.rollback()
        return jsonify({'message': 'Failed to delete technique progress'}), 500

# Statistics and Analytics Routes
@training_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_training_stats():
    """Get training statistics for the current user"""
    try:
        current_user_id = get_jwt_identity()
        print(f"🔍 Getting stats for user ID: {current_user_id}")
        
        TrainingSession = current_app.TrainingSession
        TechniqueProgress = current_app.TechniqueProgress
        
        # Get all sessions for the user
        sessions = TrainingSession.query.filter_by(user_id=current_user_id).all()
        print(f"📊 Found {len(sessions)} training sessions")
        
        if not sessions:
            return jsonify({
                'total_sessions': 0,
                'total_hours': 0,
                'avg_intensity': 0,
                'styles_practiced': [],
                'this_week': {'sessions': 0, 'hours': 0},
                'this_month': {'sessions': 0, 'hours': 0},
                'recent_sessions': [],
                'technique_stats': {'total_techniques': 0, 'mastery_breakdown': {}},
                'message': 'No training sessions found'
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
        
        # Get technique statistics
        techniques = TechniqueProgress.query.filter_by(user_id=current_user_id).all()
        print(f"🎯 Found {len(techniques)} techniques")
        
        technique_stats = {
            'total_techniques': len(techniques),
            'mastery_breakdown': {}
        }
        
        # Count techniques by mastery status
        for technique in techniques:
            status = technique.mastery_status
            technique_stats['mastery_breakdown'][status] = technique_stats['mastery_breakdown'].get(status, 0) + 1
        
        result = {
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
            'recent_sessions': [session.to_dict() for session in recent_sessions],
            'technique_stats': technique_stats,
            'message': 'Training statistics retrieved successfully'
        }
        
        print(f"✅ Stats calculated successfully")
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ Get training stats error: {str(e)}")
        import traceback
        traceback.print_exc()
        current_app.logger.error(f"Get training stats error: {str(e)}")
        return jsonify({'message': f'Failed to get training statistics: {str(e)}'}), 500

@training_bp.route('/styles', methods=['GET'])
@jwt_required()
def get_user_styles():
    """Get all martial arts styles the user has trained in"""
    try:
        current_user_id = get_jwt_identity()
        TrainingSession = current_app.TrainingSession
        TechniqueProgress = current_app.TechniqueProgress
        db = get_db()
        
        # Get unique styles from training sessions
        session_styles = db.session.query(TrainingSession.style).filter_by(
            user_id=current_user_id
        ).distinct().all()
        
        # Get unique styles from techniques
        technique_styles = db.session.query(TechniqueProgress.style).filter_by(
            user_id=current_user_id
        ).distinct().all()
        
        # Combine and deduplicate
        all_styles = set()
        for style_tuple in session_styles:
            all_styles.add(style_tuple[0])
        for style_tuple in technique_styles:
            all_styles.add(style_tuple[0])
        
        styles_list = sorted(list(all_styles))
        
        return jsonify({
            'styles': styles_list,
            'count': len(styles_list),
            'message': 'User styles retrieved successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get user styles error: {str(e)}")
        return jsonify({'message': 'Failed to get user styles'}), 500

@training_bp.route('/test', methods=['GET'])
def test_training():
    """Test endpoint for training system"""
    return jsonify({
        'message': 'Training system is working',
        'timestamp': str(datetime.utcnow()),
        'endpoints': {
            'sessions': ['GET', 'POST'],
            'sessions/<id>': ['GET', 'PUT', 'DELETE'],
            'techniques': ['GET', 'POST'],
            'techniques/<id>': ['PUT', 'DELETE'],
            'stats': ['GET'],
            'styles': ['GET']
        }
    }), 200

@training_bp.route('/test-auth', methods=['GET'])
@jwt_required()
def test_training_auth():
    """Test endpoint for JWT authentication"""
    try:
        current_user_id = get_jwt_identity()
        print(f"🔐 Auth test - User ID: {current_user_id}")
        return jsonify({
            'message': 'Training authentication is working',
            'user_id': current_user_id,
            'timestamp': str(datetime.utcnow())
        }), 200
    except Exception as e:
        print(f"❌ Auth test error: {str(e)}")
        return jsonify({'message': f'Auth test failed: {str(e)}'}), 500()
        
        if not technique:
            return jsonify({'message': 'Technique not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
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
        
        db.session.commit()
        
        return jsonify({
            'message': 'Technique progress updated successfully',
            'technique': technique.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Update technique progress error: {str(e)}")
        db = get_db()
        db.session.rollback()
        return jsonify({'message': 'Failed to update technique progress'}), 500

@training_bp.route('/techniques/<int:technique_id>', methods=['DELETE'])
@jwt_required()
def delete_technique_progress(technique_id):
    """Delete technique progress"""
    try:
        current_user_id = get_jwt_identity()
        TechniqueProgress = current_app.TechniqueProgress
        db = get_db()
        
        technique = TechniqueProgress.query.filter_by(
            id=technique_id,
            user_id=current_user_id
        ).first