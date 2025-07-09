import os
import uuid
import re
from werkzeug.utils import secure_filename
from flask import send_file
import magic
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date

training_bp = Blueprint('training', __name__)

def get_db():
    """Get database instance from current app"""
    return current_app.extensions['sqlalchemy']

def get_current_user_id():
    """Get current user ID from JWT token and convert from string to int"""
    from flask_jwt_extended import get_jwt_identity
    current_user_id_str = get_jwt_identity()  # This is now a string
    current_user_id = int(current_user_id_str)  # Convert to int for database queries
    return current_user_id

# Video Upload and Management Routes

# Configuration
UPLOAD_FOLDER = 'uploads/videos'
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
ALLOWED_VIDEO_EXTENSIONS = {
    'mp4', 'mov', 'avi', 'mkv', 'wmv', 'flv', 'webm', 'm4v'
}
ALLOWED_MIME_TYPES = {
    'video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska',
    'video/x-ms-wmv', 'video/x-flv', 'video/webm'
}

def ensure_upload_directory():
    """Ensure upload directory exists"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    return UPLOAD_FOLDER

def allowed_file(filename, file_content):
    """Check if file is allowed based on extension and MIME type"""
    if not filename:
        return False, "No filename provided"
    
    # Check file extension
    if '.' not in filename:
        return False, "File must have an extension"
    
    extension = filename.rsplit('.', 1)[1].lower()
    if extension not in ALLOWED_VIDEO_EXTENSIONS:
        return False, f"File type .{extension} not allowed. Allowed types: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}"
    
    # Check MIME type
    try:
        mime_type = magic.from_buffer(file_content, mime=True)
        if mime_type not in ALLOWED_MIME_TYPES:
            return False, f"Invalid file type. Expected video file, got {mime_type}"
    except Exception as e:
        print(f"Warning: Could not determine MIME type: {e}")
        # Continue without MIME type check if magic fails
    
    return True, None

def generate_unique_filename(original_filename, user_id):
    """Generate a unique filename for storage"""
    extension = original_filename.rsplit('.', 1)[1].lower()
    unique_id = str(uuid.uuid4())
    return f"user_{user_id}_{unique_id}.{extension}"

@training_bp.route('/videos', methods=['POST'])
@jwt_required()
def upload_video():
    """Upload a training video"""
    try:
        current_user_id = get_current_user_id()
        
        # Check if file is present
        if 'video' not in request.files:
            return jsonify({'message': 'No video file provided'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'message': 'No file selected'}), 400
        
        # Read file content for validation
        file_content = file.read()
        file.seek(0)  # Reset file pointer
        
        # Validate file size
        if len(file_content) > MAX_FILE_SIZE:
            return jsonify({
                'message': f'File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB'
            }), 400
        
        # Validate file type
        is_valid, error_message = allowed_file(file.filename, file_content)
        if not is_valid:
            return jsonify({'message': error_message}), 400
        
        # Ensure upload directory exists
        upload_dir = ensure_upload_directory()
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(original_filename, current_user_id)
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Get additional metadata from request
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        technique_name = request.form.get('technique_name', '').strip()
        style = request.form.get('style', '').strip()
        is_private = request.form.get('is_private', 'true').lower() == 'true'
        tags = request.form.get('tags', '').strip()
        
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()] if tags else []
        
        # Optional: Get video duration (simplified version without moviepy)
        duration = None
        try:
            # Try to get basic file info
            # Duration will be None for now - can be added later with AI analysis
            print(f"Video uploaded successfully - duration extraction will be added in AI phase")
        except Exception as e:
            print(f"Note: Video duration not extracted: {e}")
        
        # Create video record
        TrainingVideo = current_app.TrainingVideo
        db = get_db()
        
        video = TrainingVideo(
            user_id=current_user_id,
            filename=unique_filename,
            original_filename=original_filename,
            file_path=file_path,
            file_size=len(file_content),
            duration=duration,
            title=title if title else original_filename,
            description=description,
            technique_name=technique_name,
            style=style,
            is_private=is_private,
            tags=tag_list
        )
        
        video.save()
        
        print(f"✅ Video uploaded successfully: {original_filename} -> {unique_filename}")
        
        return jsonify({
            'message': 'Video uploaded successfully',
            'video': video.to_dict(),
            'next_steps': 'Video is ready for AI analysis'
        }), 201
        
    except Exception as e:
        print(f"❌ Video upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Clean up file if it was created
        try:
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
            
        return jsonify({'message': f'Video upload failed: {str(e)}'}), 500

@training_bp.route('/videos', methods=['GET'])
@jwt_required()
def get_videos():
    """Get all videos for the current user"""
    try:
        current_user_id = get_current_user_id()
        
        # Get query parameters
        limit = request.args.get('limit', type=int)
        technique_name = request.args.get('technique_name')
        style = request.args.get('style')
        analysis_status = request.args.get('analysis_status')
        
        TrainingVideo = current_app.TrainingVideo
        
        # Build query
        query = TrainingVideo.query.filter_by(user_id=current_user_id)
        
        if technique_name:
            query = query.filter_by(technique_name=technique_name)
        if style:
            query = query.filter_by(style=style)
        if analysis_status:
            query = query.filter_by(analysis_status=analysis_status)
            
        query = query.order_by(TrainingVideo.created_at.desc())
        
        if limit:
            query = query.limit(limit)
            
        videos = query.all()
        
        # Get video statistics
        stats = TrainingVideo.get_user_video_stats(current_user_id)
        
        return jsonify({
            'videos': [video.to_dict() for video in videos],
            'count': len(videos),
            'stats': stats,
            'message': f'Found {len(videos)} videos'
        }), 200
        
    except Exception as e:
        print(f"❌ Get videos error: {str(e)}")
        return jsonify({'message': f'Failed to get videos: {str(e)}'}), 500

@training_bp.route('/videos/<int:video_id>', methods=['GET'])
@jwt_required()
def get_video(video_id):
    """Get a specific video"""
    try:
        current_user_id = get_current_user_id()
        TrainingVideo = current_app.TrainingVideo
        
        video = TrainingVideo.query.filter_by(
            id=video_id,
            user_id=current_user_id
        ).first()
        
        if not video:
            return jsonify({'message': 'Video not found'}), 404
        
        return jsonify({
            'video': video.to_dict(include_analysis=True),
            'message': 'Video retrieved successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get video: {str(e)}'}), 500

@training_bp.route('/videos/<int:video_id>/file', methods=['GET'])
@jwt_required()
def get_video_file(video_id):
    """Stream or download a video file"""
    try:
        current_user_id = get_current_user_id()
        TrainingVideo = current_app.TrainingVideo
        
        video = TrainingVideo.query.filter_by(
            id=video_id,
            user_id=current_user_id
        ).first()
        
        if not video:
            return jsonify({'message': 'Video not found'}), 404
        
        if not os.path.exists(video.file_path):
            return jsonify({'message': 'Video file not found on disk'}), 404
        
        # Determine if this should be a download or stream
        download = request.args.get('download', 'false').lower() == 'true'
        
        return send_file(
            video.file_path,
            as_attachment=download,
            download_name=video.original_filename if download else None,
            mimetype='video/mp4'  # Default MIME type
        )
        
    except Exception as e:
        print(f"❌ Video file access error: {str(e)}")
        return jsonify({'message': f'Failed to access video file: {str(e)}'}), 500

@training_bp.route('/videos/<int:video_id>', methods=['PUT'])
@jwt_required()
def update_video(video_id):
    """Update video metadata"""
    try:
        current_user_id = get_current_user_id()
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        TrainingVideo = current_app.TrainingVideo
        db = get_db()
        
        video = TrainingVideo.query.filter_by(
            id=video_id,
            user_id=current_user_id
        ).first()
        
        if not video:
            return jsonify({'message': 'Video not found'}), 404
        
        # Update allowed fields
        if 'title' in data:
            video.title = data['title'].strip()
        if 'description' in data:
            video.description = data['description'].strip()
        if 'technique_name' in data:
            video.technique_name = data['technique_name'].strip()
        if 'style' in data:
            video.style = data['style'].strip()
        if 'is_private' in data:
            video.is_private = bool(data['is_private'])
        if 'tags' in data:
            if isinstance(data['tags'], list):
                video.tags = data['tags']
            elif isinstance(data['tags'], str):
                video.tags = [tag.strip() for tag in data['tags'].split(',') if tag.strip()]
        
        video.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Video updated successfully',
            'video': video.to_dict()
        }), 200
        
    except Exception as e:
        db = get_db()
        db.session.rollback()
        return jsonify({'message': f'Failed to update video: {str(e)}'}), 500

@training_bp.route('/videos/<int:video_id>', methods=['DELETE'])
@jwt_required()
def delete_video(video_id):
    """Delete a video and its file"""
    try:
        current_user_id = get_current_user_id()
        TrainingVideo = current_app.TrainingVideo
        db = get_db()
        
        video = TrainingVideo.query.filter_by(
            id=video_id,
            user_id=current_user_id
        ).first()
        
        if not video:
            return jsonify({'message': 'Video not found'}), 404
        
        original_filename = video.original_filename
        
        # Delete the video (this will also delete the file)
        video.delete()
        
        return jsonify({
            'message': f'Video "{original_filename}" deleted successfully'
        }), 200
        
    except Exception as e:
        db = get_db()
        db.session.rollback()
        return jsonify({'message': f'Failed to delete video: {str(e)}'}), 500

@training_bp.route('/videos/stats', methods=['GET'])
@jwt_required()
def get_video_stats():
    """Get video statistics for the current user"""
    try:
        current_user_id = get_current_user_id()
        TrainingVideo = current_app.TrainingVideo
        
        stats = TrainingVideo.get_user_video_stats(current_user_id)
        
        return jsonify({
            'stats': stats,
            'message': 'Video statistics retrieved successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get video statistics: {str(e)}'}), 500
    
# Training Sessions Routes
@training_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_training_sessions():
    """Get all training sessions for the current user"""
    try:
        current_user_id = get_current_user_id()  # Use helper function
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
        current_user_id = get_current_user_id()  # Use helper function
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
        current_user_id = get_current_user_id()
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
        current_user_id = get_current_user_id()
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
        current_user_id = get_current_user_id()
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
        current_user_id = get_current_user_id()
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
        current_user_id = get_current_user_id()
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
        current_user_id = get_current_user_id()
        TechniqueProgress = current_app.TechniqueProgress
        db = get_db()
        
        technique = TechniqueProgress.query.filter_by(
            id=technique_id,
            user_id=current_user_id
        ).first()
        
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
        current_user_id = get_current_user_id()
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
        current_user_id = get_current_user_id()  # Use helper function
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
        current_user_id = get_current_user_id()
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

# Video Upload and Management Routes

# Configuration for video uploads
UPLOAD_FOLDER = 'uploads/videos'
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
ALLOWED_VIDEO_EXTENSIONS = {
    'mp4', 'mov', 'avi', 'mkv', 'wmv', 'flv', 'webm', 'm4v'
}
ALLOWED_MIME_TYPES = {
    'video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska',
    'video/x-ms-wmv', 'video/x-flv', 'video/webm'
}

def ensure_upload_directory():
    """Ensure upload directory exists"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    return UPLOAD_FOLDER

def allowed_file(filename, file_content):
    """Check if file is allowed based on extension and MIME type"""
    if not filename:
        return False, "No filename provided"
    
    # Check file extension
    if '.' not in filename:
        return False, "File must have an extension"
    
    extension = filename.rsplit('.', 1)[1].lower()
    if extension not in ALLOWED_VIDEO_EXTENSIONS:
        return False, f"File type .{extension} not allowed. Allowed types: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}"
    
    # Check MIME type
    try:
        mime_type = magic.from_buffer(file_content, mime=True)
        if mime_type not in ALLOWED_MIME_TYPES:
            return False, f"Invalid file type. Expected video file, got {mime_type}"
    except Exception as e:
        print(f"Warning: Could not determine MIME type: {e}")
        # Continue without MIME type check if magic fails
    
    return True, None

def generate_unique_filename(original_filename, user_id):
    """Generate a unique filename for storage"""
    extension = original_filename.rsplit('.', 1)[1].lower()
    unique_id = str(uuid.uuid4())
    return f"user_{user_id}_{unique_id}.{extension}"

@training_bp.route('/videos/upload', methods=['POST'])  # CHANGED PATH TO AVOID CONFLICTS
@jwt_required()
def upload_training_video():  # CHANGED FUNCTION NAME TO AVOID CONFLICTS
    """Upload a training video"""
    try:
        current_user_id = get_current_user_id()
        
        # Check if file is present
        if 'video' not in request.files:
            return jsonify({'message': 'No video file provided'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'message': 'No file selected'}), 400
        
        # Read file content for validation
        file_content = file.read()
        file.seek(0)  # Reset file pointer
        
        # Validate file size
        if len(file_content) > MAX_FILE_SIZE:
            return jsonify({
                'message': f'File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB'
            }), 400
        
        # Validate file type
        is_valid, error_message = allowed_file(file.filename, file_content)
        if not is_valid:
            return jsonify({'message': error_message}), 400
        
        # Ensure upload directory exists
        upload_dir = ensure_upload_directory()
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(original_filename, current_user_id)
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Get additional metadata from request
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        technique_name = request.form.get('technique_name', '').strip()
        style = request.form.get('style', '').strip()
        is_private = request.form.get('is_private', 'true').lower() == 'true'
        tags = request.form.get('tags', '').strip()
        
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()] if tags else []
        
        # Optional: Get video duration (simplified version without moviepy)
        duration = None
        try:
            # Duration will be None for now - can be added later with AI analysis
            print(f"Video uploaded successfully - duration extraction will be added in AI phase")
        except Exception as e:
            print(f"Note: Video duration not extracted: {e}")
        
        # Create video record
        TrainingVideo = current_app.TrainingVideo
        db = get_db()
        
        video = TrainingVideo(
            user_id=current_user_id,
            filename=unique_filename,
            original_filename=original_filename,
            file_path=file_path,
            file_size=len(file_content),
            duration=duration,
            title=title if title else original_filename,
            description=description,
            technique_name=technique_name,
            style=style,
            is_private=is_private,
            tags=tag_list
        )
        
        video.save()
        
        print(f"✅ Video uploaded successfully: {original_filename} -> {unique_filename}")
        
        return jsonify({
            'message': 'Video uploaded successfully',
            'video': video.to_dict(),
            'next_steps': 'Video is ready for AI analysis'
        }), 201
        
    except Exception as e:
        print(f"❌ Video upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Clean up file if it was created
        try:
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
            
        return jsonify({'message': f'Video upload failed: {str(e)}'}), 500

@training_bp.route('/videos/list', methods=['GET'])  # CHANGED PATH TO AVOID CONFLICTS
@jwt_required()
def get_training_videos():  # CHANGED FUNCTION NAME TO AVOID CONFLICTS
    """Get all videos for the current user"""
    try:
        current_user_id = get_current_user_id()
        
        # Get query parameters
        limit = request.args.get('limit', type=int)
        technique_name = request.args.get('technique_name')
        style = request.args.get('style')
        analysis_status = request.args.get('analysis_status')
        
        TrainingVideo = current_app.TrainingVideo
        
        # Build query
        query = TrainingVideo.query.filter_by(user_id=current_user_id)
        
        if technique_name:
            query = query.filter_by(technique_name=technique_name)
        if style:
            query = query.filter_by(style=style)
        if analysis_status:
            query = query.filter_by(analysis_status=analysis_status)
            
        query = query.order_by(TrainingVideo.created_at.desc())
        
        if limit:
            query = query.limit(limit)
            
        videos = query.all()
        
        # Get video statistics
        stats = TrainingVideo.get_user_video_stats(current_user_id)
        
        return jsonify({
            'videos': [video.to_dict() for video in videos],
            'count': len(videos),
            'stats': stats,
            'message': f'Found {len(videos)} videos'
        }), 200
        
    except Exception as e:
        print(f"❌ Get videos error: {str(e)}")
        return jsonify({'message': f'Failed to get videos: {str(e)}'}), 500

@training_bp.route('/videos/<int:video_id>/details', methods=['GET'])  # CHANGED PATH TO AVOID CONFLICTS
@jwt_required()
def get_training_video_details(video_id):  # CHANGED FUNCTION NAME TO AVOID CONFLICTS
    """Get a specific video"""
    try:
        current_user_id = get_current_user_id()
        TrainingVideo = current_app.TrainingVideo
        
        video = TrainingVideo.query.filter_by(
            id=video_id,
            user_id=current_user_id
        ).first()
        
        if not video:
            return jsonify({'message': 'Video not found'}), 404
        
        return jsonify({
            'video': video.to_dict(include_analysis=True),
            'message': 'Video retrieved successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get video: {str(e)}'}), 500

@training_bp.route('/videos/<int:video_id>/stream', methods=['GET'])
def stream_training_video_with_auth(video_id):  # Remove @jwt_required() decorator
    """Stream video file with token parameter support for HTML5 video tags"""
    try:
        # Get token from URL parameter or Authorization header
        token = request.args.get('token') or request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'message': 'Authentication required'}), 401
        
        # Verify token manually
        try:
            from flask_jwt_extended import decode_token
            decoded_token = decode_token(token)
            current_user_id = int(decoded_token['sub'])
            print(f"🔑 Video stream auth: User ID {current_user_id}")
        except Exception as e:
            print(f"❌ Token verification failed: {str(e)}")
            return jsonify({'message': 'Invalid token'}), 401
        
        TrainingVideo = current_app.TrainingVideo
        
        video = TrainingVideo.query.filter_by(
            id=video_id,
            user_id=current_user_id
        ).first()
        
        if not video:
            print(f"❌ Video {video_id} not found for user {current_user_id}")
            return jsonify({'message': 'Video not found'}), 404
        
        if not os.path.exists(video.file_path):
            print(f"❌ Video file not found on disk: {video.file_path}")
            return jsonify({'message': 'Video file not found on disk'}), 404
        
        print(f"✅ Streaming video: {video.original_filename} ({video.file_size} bytes)")
        
        # Determine if this should be a download or stream
        download = request.args.get('download', 'false').lower() == 'true'
        
        if download:
            return send_file(
                video.file_path,
                as_attachment=True,
                download_name=video.original_filename,
                mimetype='video/mp4'
            )
        
        # Simple file streaming (without range requests for now)
        return send_file(
            video.file_path,
            mimetype='video/mp4',
            conditional=True
        )
        
    except Exception as e:
        print(f"❌ Video streaming error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Failed to stream video: {str(e)}'}), 500

@training_bp.route('/videos/<int:video_id>/update', methods=['PUT'])  # CHANGED PATH TO AVOID CONFLICTS
@jwt_required()
def update_training_video(video_id):  # CHANGED FUNCTION NAME TO AVOID CONFLICTS
    """Update video metadata"""
    try:
        current_user_id = get_current_user_id()
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        TrainingVideo = current_app.TrainingVideo
        db = get_db()
        
        video = TrainingVideo.query.filter_by(
            id=video_id,
            user_id=current_user_id
        ).first()
        
        if not video:
            return jsonify({'message': 'Video not found'}), 404
        
        # Update allowed fields
        if 'title' in data:
            video.title = data['title'].strip()
        if 'description' in data:
            video.description = data['description'].strip()
        if 'technique_name' in data:
            video.technique_name = data['technique_name'].strip()
        if 'style' in data:
            video.style = data['style'].strip()
        if 'is_private' in data:
            video.is_private = bool(data['is_private'])
        if 'tags' in data:
            if isinstance(data['tags'], list):
                video.tags = data['tags']
            elif isinstance(data['tags'], str):
                video.tags = [tag.strip() for tag in data['tags'].split(',') if tag.strip()]
        
        video.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Video updated successfully',
            'video': video.to_dict()
        }), 200
        
    except Exception as e:
        db = get_db()
        db.session.rollback()
        return jsonify({'message': f'Failed to update video: {str(e)}'}), 500

@training_bp.route('/videos/<int:video_id>/delete', methods=['DELETE'])  # CHANGED PATH TO AVOID CONFLICTS
@jwt_required()
def delete_training_video(video_id):  # CHANGED FUNCTION NAME TO AVOID CONFLICTS
    """Delete a video and its file"""
    try:
        current_user_id = get_current_user_id()
        TrainingVideo = current_app.TrainingVideo
        db = get_db()
        
        video = TrainingVideo.query.filter_by(
            id=video_id,
            user_id=current_user_id
        ).first()
        
        if not video:
            return jsonify({'message': 'Video not found'}), 404
        
        original_filename = video.original_filename
        
        # Delete the video (this will also delete the file)
        video.delete()
        
        return jsonify({
            'message': f'Video "{original_filename}" deleted successfully'
        }), 200
        
    except Exception as e:
        db = get_db()
        db.session.rollback()
        return jsonify({'message': f'Failed to delete video: {str(e)}'}), 500

@training_bp.route('/videos/stats', methods=['GET'])
@jwt_required()
def get_training_video_stats():  # CHANGED FUNCTION NAME TO AVOID CONFLICTS
    """Get video statistics for the current user"""
    try:
        current_user_id = get_current_user_id()
        TrainingVideo = current_app.TrainingVideo
        
        stats = TrainingVideo.get_user_video_stats(current_user_id)
        
        return jsonify({
            'stats': stats,
            'message': 'Video statistics retrieved successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get video statistics: {str(e)}'}), 500

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
        current_user_id = get_current_user_id()
        print(f"🔐 Auth test - User ID: {current_user_id}")
        return jsonify({
            'message': 'Training authentication is working',
            'user_id': current_user_id,
            'timestamp': str(datetime.utcnow())
        }), 200
    except Exception as e:
        print(f"❌ Auth test error: {str(e)}")
        return jsonify({'message': f'Auth test failed: {str(e)}'}), 500
    
@training_bp.route('/sessions/<int:session_id>/exercises', methods=['POST'])
@jwt_required()
def add_exercise_to_session(session_id):
    """Add an exercise to a training session"""
    try:
        current_user_id = get_current_user_id()
        data = request.get_json()
        
        if not data or not data.get('exercise_id'):
            return jsonify({'message': 'Exercise ID is required'}), 400
        
        db = get_db()
        TrainingSession = current_app.TrainingSession
        Exercise = current_app.Exercise
        WorkoutExercise = current_app.WorkoutExercise
        
        # Verify session ownership
        session = TrainingSession.query.filter_by(id=session_id, user_id=current_user_id).first()
        if not session:
            return jsonify({'message': 'Training session not found'}), 404
        
        # Verify exercise exists
        exercise = Exercise.query.get(data['exercise_id'])
        if not exercise:
            return jsonify({'message': 'Exercise not found'}), 404
        
        # Check if exercise already in session
        existing = WorkoutExercise.query.filter_by(
            training_session_id=session_id,
            exercise_id=data['exercise_id']
        ).first()
        
        if existing:
            return jsonify({'message': 'Exercise already added to this session'}), 409
        
        # Create workout exercise
        workout_exercise = WorkoutExercise(
            training_session_id=session_id,
            exercise_id=data['exercise_id'],
            sets=data.get('sets', 0),
            reps=data.get('reps', 0),
            weight=data.get('weight', 0.0),
            duration=data.get('duration', 0),
            distance=data.get('distance', 0.0),
            rest_time=data.get('rest_time', 0),
            order_in_workout=data.get('order', 0),
            notes=data.get('notes', ''),
            started_at=datetime.utcnow() if data.get('start_now') else None
        )
        
        db.session.add(workout_exercise)
        db.session.commit()
        
        print(f"✅ Added exercise {exercise.name} to session {session_id}")
        
        return jsonify({
            'workout_exercise': workout_exercise.to_dict(),
            'message': f'Exercise "{exercise.name}" added to training session'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Failed to add exercise to session: {str(e)}")
        return jsonify({'message': f'Failed to add exercise: {str(e)}'}), 500

@training_bp.route('/sessions/<int:session_id>/exercises/<int:workout_exercise_id>', methods=['PUT'])
@jwt_required()
def update_workout_exercise(session_id, workout_exercise_id):
    """Update exercise performance data in a training session"""
    try:
        current_user_id = get_current_user_id()
        data = request.get_json()
        
        db = get_db()
        TrainingSession = current_app.TrainingSession
        WorkoutExercise = current_app.WorkoutExercise
        
        # Verify session ownership
        session = TrainingSession.query.filter_by(id=session_id, user_id=current_user_id).first()
        if not session:
            return jsonify({'message': 'Training session not found'}), 404
        
        # Get workout exercise
        workout_exercise = WorkoutExercise.query.filter_by(
            id=workout_exercise_id,
            training_session_id=session_id
        ).first()
        
        if not workout_exercise:
            return jsonify({'message': 'Exercise not found in this session'}), 404
        
        # Update performance data
        if 'sets' in data:
            workout_exercise.sets = data['sets']
        if 'reps' in data:
            workout_exercise.reps = data['reps']
        if 'weight' in data:
            workout_exercise.weight = data['weight']
        if 'duration' in data:
            workout_exercise.duration = data['duration']
        if 'distance' in data:
            workout_exercise.distance = data['distance']
        if 'rest_time' in data:
            workout_exercise.rest_time = data['rest_time']
        if 'difficulty_rating' in data:
            workout_exercise.difficulty_rating = data['difficulty_rating']
        if 'form_rating' in data:
            workout_exercise.form_rating = data['form_rating']
        if 'notes' in data:
            workout_exercise.notes = data['notes']
        if 'order_in_workout' in data:
            workout_exercise.order_in_workout = data['order_in_workout']
        
        # Handle completion
        if data.get('completed'):
            workout_exercise.completed_at = datetime.utcnow()
        elif data.get('started'):
            workout_exercise.started_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'workout_exercise': workout_exercise.to_dict(),
            'message': 'Exercise performance updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to update exercise: {str(e)}'}), 500

@training_bp.route('/sessions/<int:session_id>/exercises/<int:workout_exercise_id>', methods=['DELETE'])
@jwt_required()
def remove_exercise_from_session(session_id, workout_exercise_id):
    """Remove an exercise from a training session"""
    try:
        current_user_id = get_current_user_id()
        
        db = get_db()
        TrainingSession = current_app.TrainingSession
        WorkoutExercise = current_app.WorkoutExercise
        
        # Verify session ownership
        session = TrainingSession.query.filter_by(id=session_id, user_id=current_user_id).first()
        if not session:
            return jsonify({'message': 'Training session not found'}), 404
        
        # Get workout exercise
        workout_exercise = WorkoutExercise.query.filter_by(
            id=workout_exercise_id,
            training_session_id=session_id
        ).first()
        
        if not workout_exercise:
            return jsonify({'message': 'Exercise not found in this session'}), 404
        
        exercise_name = workout_exercise.exercise_ref.name
        db.session.delete(workout_exercise)
        db.session.commit()
        
        return jsonify({
            'message': f'Exercise "{exercise_name}" removed from training session'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to remove exercise: {str(e)}'}), 500

@training_bp.route('/sessions/<int:session_id>/exercises', methods=['GET'])
@jwt_required()
def get_session_exercises(session_id):
    """Get all exercises in a training session"""
    try:
        current_user_id = get_current_user_id()
        
        TrainingSession = current_app.TrainingSession
        WorkoutExercise = current_app.WorkoutExercise
        
        # Verify session ownership
        session = TrainingSession.query.filter_by(id=session_id, user_id=current_user_id).first()
        if not session:
            return jsonify({'message': 'Training session not found'}), 404
        
        # Get exercises ordered by workout order
        workout_exercises = WorkoutExercise.query.filter_by(
            training_session_id=session_id
        ).order_by(WorkoutExercise.order_in_workout, WorkoutExercise.created_at).all()
        
        return jsonify({
            'session': {
                'id': session.id,
                'name': session.name,
                'date': session.date.isoformat() if session.date else None,
                'duration': session.duration,
                'status': session.status
            },
            'exercises': [we.to_dict() for we in workout_exercises],
            'count': len(workout_exercises),
            'message': f'Found {len(workout_exercises)} exercises in training session'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get session exercises: {str(e)}'}), 500