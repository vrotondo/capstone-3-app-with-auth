import os
import threading
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import and_, desc
# REMOVED: from models.ai_analysis import VideoAnalysis, AnalysisFeedback, AnalysisProgress
from services.ai_video_analysis import AIVideoAnalysisService

# Create blueprint with unique name to avoid conflicts
video_analysis_bp = Blueprint('video_analysis', __name__)

def get_db():
    """Get database instance from current app"""
    return current_app.extensions['sqlalchemy'].db

def get_models():
    """Get model classes from current app - FIXED VERSION"""
    return {
        'VideoAnalysis': getattr(current_app, 'VideoAnalysis', None),
        'AnalysisFeedback': getattr(current_app, 'AnalysisFeedback', None),
        'AnalysisProgress': getattr(current_app, 'AnalysisProgress', None),
        'TrainingVideo': getattr(current_app, 'TrainingVideo', None),
        'User': getattr(current_app, 'User', None)
    }

@video_analysis_bp.route('/status', methods=['GET'])
def ai_status():
    """Check AI analysis service status"""
    try:
        # Check if API key is available
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return jsonify({
                'status': 'error',
                'message': 'GEMINI_API_KEY not configured',
                'ai_enabled': False
            }), 500
        
        # Try to initialize service
        try:
            service = AIVideoAnalysisService()
            return jsonify({
                'status': 'ready',
                'message': 'AI analysis service is ready',
                'ai_enabled': True,
                'model': 'gemini-1.5-flash',
                'max_frames': service.max_frames
            })
        except Exception as service_error:
            return jsonify({
                'status': 'error',
                'message': f'Service initialization failed: {str(service_error)}',
                'ai_enabled': False
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Status check failed: {str(e)}',
            'ai_enabled': False
        }), 500

@video_analysis_bp.route('/analyze-video/<int:video_id>', methods=['POST'])
@jwt_required()
def trigger_video_analysis(video_id):
    """
    Trigger AI analysis for a specific video
    """
    try:
        user_id = get_jwt_identity()
        db = get_db()
        models = get_models()
        
        print(f"🔍 AI Analysis request for video {video_id} by user {user_id}")
        
        # Get model classes
        VideoAnalysis = models['VideoAnalysis']
        TrainingVideo = models['TrainingVideo']
        
        if not VideoAnalysis or not TrainingVideo:
            return jsonify({'error': 'Required models not available'}), 500
        
        # Get video details
        video = TrainingVideo.query.filter_by(id=video_id, user_id=user_id).first()
        if not video:
            return jsonify({'error': 'Video not found or access denied'}), 404
        
        # Check if analysis already exists and is in progress
        existing_analysis = VideoAnalysis.query.filter_by(
            video_id=video_id,
            user_id=user_id
        ).filter(
            VideoAnalysis.analysis_status.in_(['pending', 'processing'])
        ).first()
        
        if existing_analysis:
            return jsonify({
                'message': 'Analysis already in progress',
                'analysis_id': existing_analysis.id,
                'status': existing_analysis.analysis_status
            }), 200
        
        # Get analysis parameters from request
        data = request.get_json() or {}
        technique_name = data.get('technique_name', getattr(video, 'technique_name', None))
        martial_art_style = data.get('martial_art_style', getattr(video, 'style', None))
        
        print(f"🥋 Analysis params - Technique: {technique_name}, Style: {martial_art_style}")
        
        # Create analysis record
        analysis = VideoAnalysis(
            video_id=video_id,
            user_id=user_id,
            analysis_status='pending',
            technique_name=technique_name,
            martial_art_style=martial_art_style,
            ai_model='gemini-1.5-flash',
            started_at=datetime.utcnow()
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        print(f"✅ Created analysis record {analysis.id}")
        
        # Start analysis in background thread
        def run_analysis():
            """Background analysis function"""
            try:
                print(f"🚀 Starting background analysis for video {video_id}")
                
                # Update status to processing
                with current_app.app_context():
                    db = get_db()
                    models = get_models()
                    VideoAnalysis = models['VideoAnalysis']
                    analysis = VideoAnalysis.query.get(analysis.id)
                    analysis.analysis_status = 'processing'
                    db.session.commit()
                
                # Initialize AI service
                ai_service = AIVideoAnalysisService()
                
                # Get video file path
                video_file_path = getattr(video, 'file_path', None)
                if not video_file_path or not os.path.exists(video_file_path):
                    raise ValueError(f"Video file not found: {video_file_path}")
                
                print(f"📹 Analyzing video file: {video_file_path}")
                
                # Run AI analysis
                results = ai_service.analyze_video_file(
                    video_file_path,
                    technique_name,
                    martial_art_style
                )
                
                # Update analysis with results
                with current_app.app_context():
                    db = get_db()
                    models = get_models()
                    VideoAnalysis = models['VideoAnalysis']
                    analysis = VideoAnalysis.query.get(analysis.id)
                    
                    if 'error' in results:
                        # Analysis failed
                        analysis.analysis_status = 'failed'
                        analysis.error_message = results['error']
                        analysis.completed_at = datetime.utcnow()
                        print(f"❌ Analysis failed: {results['error']}")
                    else:
                        # Analysis succeeded
                        analysis.analysis_status = 'completed'
                        analysis.completed_at = datetime.utcnow()
                        analysis.overall_score = results.get('overall_score')
                        analysis.technique_identified = results.get('technique_identified')
                        analysis.identified_style = results.get('martial_art_style')
                        analysis.detailed_scores = results.get('detailed_scores')
                        analysis.strengths = results.get('strengths')
                        analysis.areas_for_improvement = results.get('areas_for_improvement')
                        analysis.coaching_tips = results.get('coaching_tips')
                        analysis.safety_considerations = results.get('safety_considerations')
                        analysis.next_steps = results.get('next_steps')
                        analysis.frames_analyzed = results.get('frames_analyzed', 0)
                        analysis.raw_ai_response = results.get('raw_response')
                        
                        print(f"✅ Analysis completed successfully! Score: {analysis.overall_score}/10")
                        
                        # Update progress tracking
                        update_analysis_progress(analysis.user_id, analysis)
                    
                    db.session.commit()
                    
            except Exception as e:
                print(f"❌ Background analysis error: {str(e)}")
                # Update analysis with error
                try:
                    with current_app.app_context():
                        db = get_db()
                        models = get_models()
                        VideoAnalysis = models['VideoAnalysis']
                        analysis = VideoAnalysis.query.get(analysis.id)
                        analysis.analysis_status = 'failed'
                        analysis.error_message = str(e)
                        analysis.completed_at = datetime.utcnow()
                        db.session.commit()
                except:
                    pass  # Avoid nested errors
        
        # Start background thread
        thread = threading.Thread(target=run_analysis)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'message': 'Analysis started successfully',
            'analysis_id': analysis.id,
            'status': 'pending',
            'estimated_time': '1-2 minutes'
        }), 202
        
    except Exception as e:
        print(f"❌ Analysis trigger error: {str(e)}")
        return jsonify({'error': f'Failed to start analysis: {str(e)}'}), 500

@video_analysis_bp.route('/analysis/<int:analysis_id>', methods=['GET'])
@jwt_required()
def get_analysis_results(analysis_id):
    """Get analysis results for a specific analysis"""
    try:
        user_id = get_jwt_identity()
        models = get_models()
        VideoAnalysis = models['VideoAnalysis']
        
        if not VideoAnalysis:
            return jsonify({'error': 'VideoAnalysis model not available'}), 500
        
        # Get analysis
        analysis = VideoAnalysis.query.filter_by(
            id=analysis_id,
            user_id=user_id
        ).first()
        
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        return jsonify({
            'analysis': analysis.to_dict(),
            'summary': analysis.get_summary_text()
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get analysis: {str(e)}'}), 500

@video_analysis_bp.route('/video/<int:video_id>/analyses', methods=['GET'])
@jwt_required()
def get_video_analyses(video_id):
    """Get all analyses for a specific video"""
    try:
        user_id = get_jwt_identity()
        models = get_models()
        VideoAnalysis = models['VideoAnalysis']
        
        if not VideoAnalysis:
            return jsonify({'error': 'VideoAnalysis model not available'}), 500
        
        # Get all analyses for this video
        analyses = VideoAnalysis.query.filter_by(
            video_id=video_id,
            user_id=user_id
        ).order_by(desc(VideoAnalysis.started_at)).all()
        
        return jsonify({
            'video_id': video_id,
            'analyses': [analysis.to_dict() for analysis in analyses],
            'total_analyses': len(analyses)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get video analyses: {str(e)}'}), 500

@video_analysis_bp.route('/progress', methods=['GET'])
@jwt_required()
def get_user_progress():
    """Get user's overall analysis progress"""
    try:
        user_id = get_jwt_identity()
        models = get_models()
        VideoAnalysis = models['VideoAnalysis']
        AnalysisProgress = models['AnalysisProgress']
        
        if not VideoAnalysis or not AnalysisProgress:
            return jsonify({'error': 'Required models not available'}), 500
        
        # Get progress records
        progress_records = AnalysisProgress.query.filter_by(
            user_id=user_id
        ).order_by(desc(AnalysisProgress.latest_analysis_date)).all()
        
        # Get recent analyses
        recent_analyses = VideoAnalysis.query.filter_by(
            user_id=user_id,
            analysis_status='completed'
        ).order_by(desc(VideoAnalysis.completed_at)).limit(10).all()
        
        return jsonify({
            'progress_by_technique': [progress.to_dict() for progress in progress_records],
            'recent_analyses': [analysis.to_dict() for analysis in recent_analyses],
            'total_techniques_analyzed': len(progress_records),
            'total_analyses_completed': len(recent_analyses)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get progress: {str(e)}'}), 500

def update_analysis_progress(user_id, analysis):
    """Update progress tracking for a completed analysis"""
    try:
        if not analysis.technique_name or analysis.overall_score is None:
            return
        
        db = get_db()
        models = get_models()
        VideoAnalysis = models['VideoAnalysis']
        AnalysisProgress = models['AnalysisProgress']
        
        if not AnalysisProgress:
            return
        
        # Find or create progress record
        progress = AnalysisProgress.query.filter_by(
            user_id=user_id,
            technique_name=analysis.technique_name,
            martial_art_style=analysis.martial_art_style
        ).first()
        
        if not progress:
            # Create new progress record
            progress = AnalysisProgress(
                user_id=user_id,
                technique_name=analysis.technique_name,
                martial_art_style=analysis.martial_art_style,
                first_analysis_id=analysis.id,
                latest_analysis_id=analysis.id,
                first_score=analysis.overall_score,
                latest_score=analysis.overall_score,
                best_score=analysis.overall_score,
                average_score=analysis.overall_score,
                total_analyses=1,
                first_analysis_date=analysis.completed_at,
                latest_analysis_date=analysis.completed_at
            )
            db.session.add(progress)
        else:
            # Update existing progress
            progress.latest_analysis_id = analysis.id
            progress.latest_score = analysis.overall_score
            progress.latest_analysis_date = analysis.completed_at
            progress.total_analyses += 1
            
            # Update best score
            if analysis.overall_score > (progress.best_score or 0):
                progress.best_score = analysis.overall_score
            
            # Recalculate average
            all_scores = VideoAnalysis.query.filter(
                and_(
                    VideoAnalysis.user_id == user_id,
                    VideoAnalysis.technique_name == analysis.technique_name,
                    VideoAnalysis.martial_art_style == analysis.martial_art_style,
                    VideoAnalysis.analysis_status == 'completed',
                    VideoAnalysis.overall_score.isnot(None)
                )
            ).with_entities(VideoAnalysis.overall_score).all()
            
            scores = [score[0] for score in all_scores]
            if scores:
                progress.average_score = sum(scores) / len(scores)
                
                # Calculate improvement rate
                if len(scores) > 1:
                    progress.improvement_rate = (scores[-1] - scores[0]) / (len(scores) - 1)
        
        db.session.commit()
        print(f"📈 Updated progress for {analysis.technique_name}: {progress.latest_score}/10")
        
    except Exception as e:
        print(f"❌ Progress update error: {str(e)}")
        db.session.rollback()

# Test endpoint for development
@video_analysis_bp.route('/test', methods=['GET'])
def test_ai_service():
    """Test endpoint to verify AI service setup"""
    try:
        service = AIVideoAnalysisService()
        return jsonify({
            'status': 'success',
            'message': 'AI service is working correctly',
            'model': 'gemini-1.5-flash',
            'max_frames': service.max_frames
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'AI service test failed: {str(e)}'
        })