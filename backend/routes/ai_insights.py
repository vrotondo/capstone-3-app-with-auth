from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import logging

# Import the Gemini service
from services.gemini_service import get_gemini_service, TrainingInsight

logger = logging.getLogger(__name__)

# Create the AI insights blueprint
ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/health', methods=['GET'])
def ai_health():
    """Check if AI service is available"""
    gemini_service = get_gemini_service()
    return jsonify({
        'ai_service_enabled': gemini_service.is_enabled(),
        'service': 'gemini',
        'status': 'healthy' if gemini_service.is_enabled() else 'disabled',
        'timestamp': datetime.utcnow().isoformat()
    })

@ai_bp.route('/insights', methods=['GET'])
@jwt_required()
def get_training_insights():
    """
    Generate AI-powered insights based on user's training data
    Query params:
    - timeframe: 'last_7_days', 'last_30_days', 'last_90_days' (default: last_30_days)
    - include_techniques: true/false (default: true)
    """
    try:
        user_id = get_jwt_identity()
        timeframe = request.args.get('timeframe', 'last_30_days')
        include_techniques = request.args.get('include_techniques', 'true').lower() == 'true'
        
        logger.info(f"Generating AI insights for user {user_id}, timeframe: {timeframe}")
        
        # Get models from app context
        User = current_app.User
        TrainingSession = current_app.TrainingSession
        TechniqueProgress = current_app.TechniqueProgress
        
        # Fetch user profile
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Calculate date range based on timeframe
        end_date = datetime.utcnow()
        days_map = {
            'last_7_days': 7,
            'last_30_days': 30,
            'last_90_days': 90
        }
        days = days_map.get(timeframe, 30)
        start_date = end_date - timedelta(days=days)
        
        # Fetch training sessions within timeframe
        sessions = TrainingSession.query.filter(
            TrainingSession.user_id == user_id,
            TrainingSession.created_at >= start_date
        ).order_by(TrainingSession.created_at.desc()).all()
        
        # Convert sessions to dict format for AI analysis
        sessions_data = []
        for session in sessions:
            # Handle different possible field names and attributes
            session_dict = {
                'id': session.id,
                'date': session.created_at.isoformat() if session.created_at else None,
                'created_at': session.created_at.isoformat() if session.created_at else None,
            }
            
            # Add duration (try different field names)
            if hasattr(session, 'duration_minutes') and session.duration_minutes:
                session_dict['duration_minutes'] = session.duration_minutes
                session_dict['duration'] = session.duration_minutes
            elif hasattr(session, 'duration') and session.duration:
                session_dict['duration'] = session.duration
                session_dict['duration_minutes'] = session.duration
            else:
                session_dict['duration_minutes'] = 0
                session_dict['duration'] = 0
            
            # Add intensity (try different field names)
            if hasattr(session, 'intensity') and session.intensity:
                session_dict['intensity'] = session.intensity
                session_dict['intensity_level'] = session.intensity
            elif hasattr(session, 'intensity_level') and session.intensity_level:
                session_dict['intensity_level'] = session.intensity_level
                session_dict['intensity'] = session.intensity_level
            else:
                session_dict['intensity'] = 0
                session_dict['intensity_level'] = 0
            
            # Add martial art style
            if hasattr(session, 'martial_art_style') and session.martial_art_style:
                session_dict['martial_art_style'] = session.martial_art_style
                session_dict['style'] = session.martial_art_style
            elif hasattr(session, 'style') and session.style:
                session_dict['style'] = session.style
                session_dict['martial_art_style'] = session.style
            else:
                session_dict['martial_art_style'] = 'Unknown'
                session_dict['style'] = 'Unknown'
            
            # Add techniques practiced
            if hasattr(session, 'techniques_practiced') and session.techniques_practiced:
                session_dict['techniques_practiced'] = session.techniques_practiced
            else:
                session_dict['techniques_practiced'] = ''
            
            # Add notes
            if hasattr(session, 'notes') and session.notes:
                session_dict['notes'] = session.notes
            else:
                session_dict['notes'] = ''
            
            sessions_data.append(session_dict)
        
        # Fetch technique progress if requested
        techniques_data = []
        if include_techniques:
            techniques = TechniqueProgress.query.filter(
                TechniqueProgress.user_id == user_id
            ).all()
            
            for tech in techniques:
                tech_dict = {
                    'technique_name': tech.technique_name if hasattr(tech, 'technique_name') else 'Unknown',
                    'current_level': tech.current_level if hasattr(tech, 'current_level') else 0,
                    'target_level': tech.target_level if hasattr(tech, 'target_level') else 10,
                    'notes': tech.notes if hasattr(tech, 'notes') else '',
                }
                
                # Add last practiced date
                if hasattr(tech, 'last_practiced') and tech.last_practiced:
                    tech_dict['last_practiced'] = tech.last_practiced.isoformat()
                elif hasattr(tech, 'created_at') and tech.created_at:
                    tech_dict['last_practiced'] = tech.created_at.isoformat()
                else:
                    tech_dict['last_practiced'] = None
                
                techniques_data.append(tech_dict)
        
        # Prepare user profile data
        user_profile = {
            'username': user.username if hasattr(user, 'username') else 'Unknown',
        }
        
        # Add optional user profile fields if they exist
        if hasattr(user, 'first_name') and user.first_name:
            user_profile['first_name'] = user.first_name
        if hasattr(user, 'primary_martial_art') and user.primary_martial_art:
            user_profile['primary_martial_art'] = user.primary_martial_art
        if hasattr(user, 'experience_level') and user.experience_level:
            user_profile['experience_level'] = user.experience_level
        if hasattr(user, 'training_goals') and user.training_goals:
            user_profile['goals'] = user.training_goals
        
        # Prepare data for AI analysis
        analysis_data = {
            'sessions': sessions_data,
            'techniques': techniques_data,
            'user_profile': user_profile,
            'timeframe': timeframe,
            'analysis_date': datetime.utcnow().isoformat()
        }
        
        # Generate AI insights
        gemini_service = get_gemini_service()
        insights = gemini_service.analyze_training_patterns(analysis_data)
        
        # Convert insights to JSON-serializable format
        insights_json = []
        for insight in insights:
            insights_json.append({
                'type': insight.type,
                'title': insight.title,
                'message': insight.message.strip(),
                'confidence': insight.confidence,
                'action_items': insight.action_items,
                'data_points': insight.data_points
            })
        
        # Calculate basic statistics for context
        total_sessions = len(sessions_data)
        total_duration = sum(s.get('duration_minutes', s.get('duration', 0)) for s in sessions_data)
        
        # Calculate average intensity safely
        intensities = [s.get('intensity', s.get('intensity_level', 0)) for s in sessions_data if s.get('intensity', s.get('intensity_level', 0)) > 0]
        avg_intensity = sum(intensities) / len(intensities) if intensities else 0
        
        # Count unique martial arts styles
        styles = [s.get('martial_art_style', s.get('style', '')) for s in sessions_data if s.get('martial_art_style', s.get('style', ''))]
        unique_styles = len(set(style for style in styles if style and style != 'Unknown'))
        
        return jsonify({
            'success': True,
            'insights': insights_json,
            'statistics': {
                'total_sessions': total_sessions,
                'total_duration_minutes': total_duration,
                'average_intensity': round(avg_intensity, 1),
                'unique_styles': unique_styles,
                'timeframe': timeframe,
                'analysis_period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                'techniques_tracked': len(techniques_data)
            },
            'ai_service': {
                'enabled': gemini_service.is_enabled(),
                'generated_at': datetime.utcnow().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error generating AI insights: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to generate insights',
            'message': str(e),
            'success': False
        }), 500

@ai_bp.route('/workout-suggestions', methods=['POST'])
@jwt_required()
def get_workout_suggestions():
    """Generate AI-powered workout suggestions"""
    try:
        user_id = get_jwt_identity()
        request_data = request.get_json() or {}
        
        # Get user's training data (similar to insights endpoint)
        User = current_app.User
        TrainingSession = current_app.TrainingSession
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get recent sessions for context (last 2 weeks)
        recent_sessions = TrainingSession.query.filter(
            TrainingSession.user_id == user_id,
            TrainingSession.created_at >= datetime.utcnow() - timedelta(days=14)
        ).order_by(TrainingSession.created_at.desc()).limit(10).all()
        
        sessions_data = []
        for session in recent_sessions:
            session_data = {
                'date': session.created_at.isoformat() if session.created_at else None,
                'duration': getattr(session, 'duration_minutes', getattr(session, 'duration', 0)),
                'intensity': getattr(session, 'intensity', getattr(session, 'intensity_level', 0)),
                'martial_art_style': getattr(session, 'martial_art_style', getattr(session, 'style', 'Unknown')),
                'techniques_practiced': getattr(session, 'techniques_practiced', '')
            }
            sessions_data.append(session_data)
        
        # Prepare user profile
        user_profile = {
            'username': getattr(user, 'username', 'Unknown'),
            'primary_martial_art': getattr(user, 'primary_martial_art', None),
            'experience_level': getattr(user, 'experience_level', None),
            'preferences': request_data.get('preferences', {})
        }
        
        analysis_data = {
            'sessions': sessions_data,
            'user_profile': user_profile
        }
        
        # Generate workout suggestions
        gemini_service = get_gemini_service()
        suggestions = gemini_service.generate_workout_suggestions(analysis_data)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating workout suggestions: {e}")
        return jsonify({
            'error': 'Failed to generate workout suggestions',
            'message': str(e),
            'success': False
        }), 500

@ai_bp.route('/technique-analysis', methods=['GET'])
@jwt_required()
def get_technique_analysis():
    """Get AI analysis of technique progress"""
    try:
        user_id = get_jwt_identity()
        
        # Get models
        TechniqueProgress = current_app.TechniqueProgress
        
        # Fetch all technique progress for user
        techniques = TechniqueProgress.query.filter(
            TechniqueProgress.user_id == user_id
        ).all()
        
        if not techniques:
            return jsonify({
                'success': True,
                'insights': [],
                'message': 'No technique progress data found',
                'technique_count': 0
            })
        
        techniques_data = []
        for tech in techniques:
            tech_data = {
                'technique_name': getattr(tech, 'technique_name', 'Unknown'),
                'current_level': getattr(tech, 'current_level', 0),
                'target_level': getattr(tech, 'target_level', 10),
                'notes': getattr(tech, 'notes', ''),
                'created_at': tech.created_at.isoformat() if hasattr(tech, 'created_at') and tech.created_at else None
            }
            
            # Add last practiced date
            if hasattr(tech, 'last_practiced') and tech.last_practiced:
                tech_data['last_practiced'] = tech.last_practiced.isoformat()
            else:
                tech_data['last_practiced'] = None
            
            techniques_data.append(tech_data)
        
        # Generate technique analysis
        gemini_service = get_gemini_service()
        insights = gemini_service.analyze_technique_progress(techniques_data)
        
        # Convert to JSON format
        insights_json = []
        for insight in insights:
            insights_json.append({
                'type': insight.type,
                'title': insight.title,
                'message': insight.message.strip(),
                'confidence': insight.confidence,
                'action_items': insight.action_items,
                'data_points': insight.data_points
            })
        
        return jsonify({
            'success': True,
            'insights': insights_json,
            'technique_count': len(techniques_data),
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error analyzing technique progress: {e}")
        return jsonify({
            'error': 'Failed to analyze technique progress',
            'message': str(e),
            'success': False
        }), 500

@ai_bp.route('/test', methods=['GET'])
def test_ai_service():
    """Test endpoint to verify AI service is working"""
    gemini_service = get_gemini_service()
    
    if not gemini_service.is_enabled():
        return jsonify({
            'status': 'disabled',
            'message': 'Gemini AI service is not configured. Please set GEMINI_API_KEY environment variable.',
            'test_result': 'failed'
        }), 503
    
    try:
        # Simple test analysis with mock data
        test_data = {
            'sessions': [
                {
                    'date': '2024-01-01',
                    'duration_minutes': 60,
                    'duration': 60,
                    'intensity': 7,
                    'intensity_level': 7,
                    'martial_art_style': 'Karate',
                    'style': 'Karate',
                    'techniques_practiced': 'kata, kumite',
                    'notes': 'Good session, worked on timing'
                },
                {
                    'date': '2024-01-03',
                    'duration_minutes': 45,
                    'duration': 45,
                    'intensity': 6,
                    'intensity_level': 6,
                    'martial_art_style': 'Karate',
                    'style': 'Karate',
                    'techniques_practiced': 'basics, sparring',
                    'notes': 'Focused on footwork'
                }
            ],
            'techniques': [
                {
                    'technique_name': 'Front Kick',
                    'current_level': 5,
                    'target_level': 8,
                    'notes': 'Working on height and balance'
                }
            ],
            'user_profile': {
                'username': 'test_user',
                'experience_level': 'Intermediate'
            },
            'timeframe': 'test'
        }
        
        insights = gemini_service.analyze_training_patterns(test_data)
        
        return jsonify({
            'status': 'enabled',
            'message': 'Gemini AI service is working correctly',
            'test_result': 'success',
            'test_insights_count': len(insights),
            'sample_insight': {
                'type': insights[0].type,
                'title': insights[0].title,
                'message': insights[0].message[:100] + '...' if len(insights[0].message) > 100 else insights[0].message,
                'confidence': insights[0].confidence
            } if insights else None,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"AI service test failed: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Gemini AI service test failed: {str(e)}',
            'test_result': 'failed',
            'error_details': str(e)
        }), 500

@ai_bp.route('/status', methods=['GET'])
def ai_status():
    """Get detailed AI service status"""
    gemini_service = get_gemini_service()
    
    return jsonify({
        'ai_enabled': gemini_service.is_enabled(),
        'service': 'Google Gemini',
        'endpoints': {
            'health': '/api/ai/health',
            'insights': '/api/ai/insights',
            'workout_suggestions': '/api/ai/workout-suggestions',
            'technique_analysis': '/api/ai/technique-analysis',
            'test': '/api/ai/test',
            'status': '/api/ai/status'
        },
        'features': [
            'Training pattern analysis',
            'Personalized recommendations',
            'Technique progress insights',
            'Workout plan suggestions'
        ],
        'timestamp': datetime.utcnow().isoformat()
    })

@ai_bp.route('/chat', methods=['POST'])
@jwt_required()
def ai_chat():
    """
    AI Chat feature - Talk to your personal martial arts coach
    """
    try:
        user_id = get_jwt_identity()
        request_data = request.get_json()
        
        message = request_data.get('message', '').strip()
        chat_history = request_data.get('chat_history', [])
        
        if not message:
            return jsonify({
                'error': 'Message is required',
                'success': False
            }), 400
        
        # Get user profile and training data for context
        User = current_app.User
        TrainingSession = current_app.TrainingSession
        TechniqueProgress = current_app.TechniqueProgress
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get recent training data for context
        recent_sessions = TrainingSession.query.filter(
            TrainingSession.user_id == user_id
        ).order_by(TrainingSession.created_at.desc()).limit(5).all()
        
        recent_techniques = TechniqueProgress.query.filter(
            TechniqueProgress.user_id == user_id
        ).limit(10).all()
        
        # Prepare context for AI
        user_context = {
            'name': getattr(user, 'first_name', getattr(user, 'username', 'Student')),
            'experience': getattr(user, 'experience_level', 'Not specified'),
            'primary_art': getattr(user, 'primary_martial_art', 'Various'),
            'recent_sessions': len(recent_sessions),
            'total_techniques': len(recent_techniques)
        }
        
        # Generate AI response
        gemini_service = get_gemini_service()
        ai_response = gemini_service.generate_chat_response(message, chat_history, user_context)
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in AI chat: {e}")
        return jsonify({
            'error': 'Failed to generate chat response',
            'message': str(e),
            'success': False
        }), 500

@ai_bp.route('/chat/suggestions', methods=['GET'])
@jwt_required()
def get_chat_suggestions():
    """Get suggested questions for the AI chat"""
    user_id = get_jwt_identity()
    
    # Get user's training data to provide relevant suggestions
    User = current_app.User
    TrainingSession = current_app.TrainingSession
    
    user = User.query.get(user_id)
    recent_sessions = TrainingSession.query.filter(
        TrainingSession.user_id == user_id
    ).order_by(TrainingSession.created_at.desc()).limit(3).all()
    
    # Base suggestions
    suggestions = [
        "How can I improve my technique?",
        "What should I focus on in my next training session?",
        "How often should I train per week?",
        "What are some good warm-up exercises?",
        "How do I stay motivated in my martial arts journey?"
    ]
    
    # Add personalized suggestions based on user data
    if user and hasattr(user, 'primary_martial_art') and user.primary_martial_art:
        art = user.primary_martial_art
        suggestions.insert(0, f"What are the fundamentals I should master in {art}?")
        suggestions.insert(1, f"What's a good training plan for {art}?")
    
    if recent_sessions:
        latest_session = recent_sessions[0]
        if hasattr(latest_session, 'martial_art_style') and latest_session.martial_art_style:
            suggestions.insert(0, f"How did my last {latest_session.martial_art_style} session look?")
    
    return jsonify({
        'success': True,
        'suggestions': suggestions[:8]  # Limit to 8 suggestions
    })

@ai_bp.route('/workout-plan', methods=['POST'])
@jwt_required()
def generate_workout_plan():
    """Generate AI-powered weekly workout plan"""
    try:
        user_id = get_jwt_identity()
        request_data = request.get_json() or {}
        preferences = request_data.get('preferences', {})
        
        # Get user data
        User = current_app.User
        TrainingSession = current_app.TrainingSession
        TechniqueProgress = current_app.TechniqueProgress
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get training history
        sessions = TrainingSession.query.filter(
            TrainingSession.user_id == user_id
        ).order_by(TrainingSession.created_at.desc()).limit(20).all()
        
        techniques = TechniqueProgress.query.filter(
            TechniqueProgress.user_id == user_id
        ).all()
        
        # Prepare data
        user_data = {
            'sessions': [{
                'date': s.created_at.isoformat() if s.created_at else None,
                'duration_minutes': getattr(s, 'duration_minutes', getattr(s, 'duration', 0)),
                'intensity': getattr(s, 'intensity', getattr(s, 'intensity_level', 0)),
                'martial_art_style': getattr(s, 'martial_art_style', getattr(s, 'style', 'Unknown')),
                'techniques_practiced': getattr(s, 'techniques_practiced', '')
            } for s in sessions],
            'user_profile': {
                'first_name': getattr(user, 'first_name', getattr(user, 'username', 'Student')),
                'primary_martial_art': getattr(user, 'primary_martial_art', 'Mixed Martial Arts'),
                'experience_level': getattr(user, 'experience_level', 'Intermediate'),
                'goals': getattr(user, 'training_goals', 'General improvement')
            }
        }
        
        # Generate workout plan
        gemini_service = get_gemini_service()
        workout_plan = gemini_service.generate_workout_plan(user_data, preferences)
        
        return jsonify(workout_plan)
        
    except Exception as e:
        logger.error(f"Error generating workout plan: {e}")
        return jsonify({
            'error': 'Failed to generate workout plan',
            'message': str(e),
            'success': False
        }), 500

@ai_bp.route('/injury-risk', methods=['GET'])
@jwt_required()
def analyze_injury_risk():
    """Analyze user's training patterns for injury risk factors"""
    try:
        user_id = get_jwt_identity()
        
        # Get training data
        TrainingSession = current_app.TrainingSession
        sessions = TrainingSession.query.filter(
            TrainingSession.user_id == user_id
        ).order_by(TrainingSession.created_at.desc()).limit(30).all()
        
        if len(sessions) < 3:
            return jsonify({
                'error': 'Need at least 3 training sessions for injury risk analysis',
                'success': False
            }), 400
        
        # Prepare data
        user_data = {
            'sessions': [{
                'date': s.created_at.isoformat() if s.created_at else None,
                'duration_minutes': getattr(s, 'duration_minutes', getattr(s, 'duration', 0)),
                'intensity': getattr(s, 'intensity', getattr(s, 'intensity_level', 0)),
                'martial_art_style': getattr(s, 'martial_art_style', getattr(s, 'style', 'Unknown')),
                'notes': getattr(s, 'notes', '')
            } for s in sessions]
        }
        
        # Analyze injury risk
        gemini_service = get_gemini_service()
        risk_analysis = gemini_service.analyze_injury_risk(user_data)
        
        return jsonify(risk_analysis)
        
    except Exception as e:
        logger.error(f"Error analyzing injury risk: {e}")
        return jsonify({
            'error': 'Failed to analyze injury risk',
            'message': str(e),
            'success': False
        }), 500

@ai_bp.route('/competition-prep', methods=['POST'])
@jwt_required()
def generate_competition_prep():
    """Generate AI-powered competition preparation plan"""
    try:
        user_id = get_jwt_identity()
        request_data = request.get_json() or {}
        
        competition_date = request_data.get('competition_date')
        competition_type = request_data.get('competition_type', 'tournament')
        current_skills = request_data.get('current_skills', [])
        
        if not competition_date:
            return jsonify({
                'error': 'Competition date is required',
                'success': False
            }), 400
        
        # Get user data
        User = current_app.User
        TrainingSession = current_app.TrainingSession
        TechniqueProgress = current_app.TechniqueProgress
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get training history
        sessions = TrainingSession.query.filter(
            TrainingSession.user_id == user_id
        ).order_by(TrainingSession.created_at.desc()).limit(15).all()
        
        techniques = TechniqueProgress.query.filter(
            TechniqueProgress.user_id == user_id
        ).all()
        
        # Calculate time until competition
        from datetime import datetime
        comp_date = datetime.fromisoformat(competition_date.replace('Z', '+00:00'))
        days_until = (comp_date - datetime.utcnow()).days
        
        # Generate competition prep plan
        gemini_service = get_gemini_service()
        
        prep_prompt = f"""
        Create a detailed competition preparation plan for this martial artist:

        COMPETITION DETAILS:
        - Date: {competition_date}
        - Days until competition: {days_until}
        - Competition type: {competition_type}
        - Current skills focus: {', '.join(current_skills) if current_skills else 'General'}

        ATHLETE PROFILE:
        - Name: {getattr(user, 'first_name', 'Athlete')}
        - Experience: {getattr(user, 'experience_level', 'Intermediate')}
        - Primary Art: {getattr(user, 'primary_martial_art', 'Mixed Martial Arts')}

        RECENT TRAINING:
        - Total sessions (last 30 days): {len(sessions)}
        - Techniques being worked on: {len(techniques)}

        CREATE A PHASE-BASED PREPARATION PLAN:

        1. **IMMEDIATE FOCUS (Next 2 weeks)**
        2. **MID-TERM PREPARATION (Following weeks)**
        3. **COMPETITION WEEK STRATEGY**
        4. **MENTAL PREPARATION PLAN**
        5. **RECOVERY & INJURY PREVENTION**

        For each phase, include:
        - Specific training goals
        - Recommended techniques to focus on
        - Training intensity and frequency
        - Mental preparation exercises
        - Nutrition and recovery recommendations

        Consider the time available and create a realistic, progressive plan.
        """
        
        try:
            response = gemini_service.model.generate_content(prep_prompt)
            
            return jsonify({
                'success': True,
                'preparation_plan': response.text,
                'competition_date': competition_date,
                'days_until_competition': days_until,
                'competition_type': competition_type,
                'generated_at': datetime.utcnow().isoformat()
            })
            
        except Exception as ai_error:
            return jsonify({
                'error': 'Failed to generate competition prep plan',
                'message': str(ai_error),
                'success': False
            }), 500
        
    except Exception as e:
        logger.error(f"Error generating competition prep: {e}")
        return jsonify({
            'error': 'Failed to generate competition preparation plan',
            'message': str(e),
            'success': False
        }), 500

@ai_bp.route('/training-tips', methods=['GET'])
@jwt_required()
def get_daily_training_tips():
    """Get daily training tips based on user's martial art and recent activity"""
    try:
        user_id = get_jwt_identity()
        
        # Get user data
        User = current_app.User
        TrainingSession = current_app.TrainingSession
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get recent session
        latest_session = TrainingSession.query.filter(
            TrainingSession.user_id == user_id
        ).order_by(TrainingSession.created_at.desc()).first()
        
        gemini_service = get_gemini_service()
        
        tips_prompt = f"""
        Provide 3 daily training tips for this martial artist:

        MARTIAL ARTIST:
        - Name: {getattr(user, 'first_name', 'Student')}
        - Primary Art: {getattr(user, 'primary_martial_art', 'Mixed Martial Arts')}
        - Experience: {getattr(user, 'experience_level', 'Intermediate')}

        RECENT ACTIVITY:
        - Last session: {latest_session.martial_art_style if latest_session and hasattr(latest_session, 'martial_art_style') else 'No recent sessions'}
        - Last training date: {latest_session.created_at.strftime('%Y-%m-%d') if latest_session and latest_session.created_at else 'No recent training'}

        Provide 3 practical, actionable tips:
        1. A technique tip
        2. A conditioning/fitness tip  
        3. A mental/mindset tip

        Make them specific to their martial art and encouraging. Keep each tip to 1-2 sentences.
        """
        
        try:
            response = gemini_service.model.generate_content(tips_prompt)
            
            return jsonify({
                'success': True,
                'tips': response.text,
                'martial_art': getattr(user, 'primary_martial_art', 'Mixed Martial Arts'),
                'generated_at': datetime.utcnow().isoformat()
            })
            
        except Exception as ai_error:
            return jsonify({
                'error': 'Failed to generate training tips',
                'message': str(ai_error),
                'success': False
            }), 500
        
    except Exception as e:
        logger.error(f"Error getting training tips: {e}")
        return jsonify({
            'error': 'Failed to get training tips',
            'message': str(e),
            'success': False
        }), 500

@ai_bp.route('/debug-service', methods=['GET'])
def debug_gemini_service():
    """Debug endpoint to check GeminiService methods"""
    try:
        from services.gemini_service import get_gemini_service
        gemini_service = get_gemini_service()
        
        # Get all methods and attributes
        all_attributes = dir(gemini_service)
        methods = [attr for attr in all_attributes if callable(getattr(gemini_service, attr)) and not attr.startswith('_')]
        
        return jsonify({
            'service_enabled': gemini_service.is_enabled() if hasattr(gemini_service, 'is_enabled') else 'No is_enabled method',
            'service_type': str(type(gemini_service)),
            'has_generate_chat_response': hasattr(gemini_service, 'generate_chat_response'),
            'available_methods': methods,
            'all_attributes': [attr for attr in all_attributes if not attr.startswith('__')],
            'service_file_location': gemini_service.__class__.__module__ if hasattr(gemini_service, '__class__') else 'Unknown'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': str(e)
        }), 500