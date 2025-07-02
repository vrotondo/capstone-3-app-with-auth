import os
import json
import google.generativeai as genai
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class TrainingInsight:
    """Data class for AI-generated training insights"""
    type: str  # 'pattern', 'recommendation', 'achievement', 'warning'
    title: str
    message: str
    confidence: float  # 0.0 to 1.0
    action_items: List[str]
    data_points: Dict[str, Any]

class GeminiService:
    """Service for integrating Google Gemini AI for training analysis"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
            self.enabled = False
            return
            
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.enabled = True
            logger.info("Gemini service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini service: {e}")
            self.enabled = False
    
    def is_enabled(self) -> bool:
        """Check if Gemini service is available"""
        return self.enabled
    
    def analyze_training_patterns(self, user_data: Dict[str, Any]) -> List[TrainingInsight]:
        """
        Analyze user's training data and generate insights
        
        Args:
            user_data: Dictionary containing:
                - sessions: List of training sessions
                - techniques: List of technique progress
                - user_profile: User preferences and goals
                - timeframe: Analysis period (e.g., 'last_30_days')
        
        Returns:
            List of TrainingInsight objects
        """
        if not self.enabled:
            return [TrainingInsight(
                type='warning',
                title='AI Analysis Unavailable',
                message='Gemini AI service is not configured. Contact your administrator to enable AI features.',
                confidence=1.0,
                action_items=['Configure Gemini API key'],
                data_points={}
            )]
        
        try:
            # Prepare training data summary for AI analysis
            training_summary = self._prepare_training_summary(user_data)
            
            # Generate AI prompt
            prompt = self._create_analysis_prompt(training_summary, user_data.get('timeframe', 'last_30_days'))
            
            # Get AI response
            response = self.model.generate_content(prompt)
            
            # Parse and structure the response
            insights = self._parse_ai_response(response.text, user_data)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error analyzing training patterns: {e}")
            return [TrainingInsight(
                type='warning',
                title='Analysis Error',
                message='Unable to generate AI insights at this time. Please try again later.',
                confidence=0.0,
                action_items=['Check your internet connection', 'Try again in a few minutes'],
                data_points={'error': str(e)}
            )]
    
    def generate_workout_suggestions(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered workout suggestions based on training history"""
        if not self.enabled:
            return {'error': 'Gemini AI service not available'}
        
        try:
            summary = self._prepare_training_summary(user_data)
            
            prompt = f"""
            Based on this martial artist's training data, suggest 3 specific workout plans for the next week.
            Consider their training history, intensity patterns, and martial arts style focus.
            
            Training History: {summary}
            
            Provide practical, actionable workout suggestions in JSON format:
            {{
                "suggestions": [
                    {{
                        "name": "Descriptive workout name",
                        "focus": "Primary focus area (technique, conditioning, sparring, etc.)",
                        "duration": "Estimated duration in minutes",
                        "exercises": ["specific exercise 1", "specific exercise 2", "specific exercise 3"],
                        "reasoning": "Why this workout is recommended based on their data",
                        "intensity": "Low/Medium/High based on recent training"
                    }}
                ],
                "general_advice": "Overall training advice for the week",
                "recovery_notes": "Important recovery considerations"
            }}
            
            Focus on practical exercises they can actually do, considering their martial arts style and recent training patterns.
            """
            
            response = self.model.generate_content(prompt)
            
            # Try to parse as JSON, fall back to text response
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                return {
                    'suggestions': [{
                        'name': 'AI-Generated Workout Plan',
                        'focus': 'General Training',
                        'duration': '45-60 minutes',
                        'exercises': ['Review AI response for details'],
                        'reasoning': response.text[:200] + '...' if len(response.text) > 200 else response.text,
                        'intensity': 'Medium'
                    }],
                    'general_advice': 'See full AI response for detailed recommendations',
                    'raw_response': response.text
                }
            
        except Exception as e:
            logger.error(f"Error generating workout suggestions: {e}")
            return {'error': f'Unable to generate suggestions: {str(e)}'}
    
    def analyze_technique_progress(self, technique_data: List[Dict]) -> List[TrainingInsight]:
        """Analyze progress on specific techniques"""
        if not self.enabled:
            return []
        
        try:
            techniques_summary = self._prepare_technique_summary(technique_data)
            
            prompt = f"""
            Analyze this martial artist's technique progress and provide specific insights:
            
            Technique Data: {techniques_summary}
            
            Focus on:
            1. Techniques showing good progress (level improvements)
            2. Techniques that need more work (low levels or no progress)
            3. Recommended focus areas for next training sessions
            4. Potential skill gaps based on technique levels
            5. Suggestions for advancement
            
            Provide practical, actionable insights that help improve their martial arts training.
            """
            
            response = self.model.generate_content(prompt)
            return self._parse_technique_response(response.text, technique_data)
            
        except Exception as e:
            logger.error(f"Error analyzing technique progress: {e}")
            return []
    
    def _prepare_training_summary(self, user_data: Dict[str, Any]) -> str:
        """Prepare a concise summary of training data for AI analysis"""
        sessions = user_data.get('sessions', [])
        techniques = user_data.get('techniques', [])
        user_profile = user_data.get('user_profile', {})
        timeframe = user_data.get('timeframe', 'last_30_days')
        
        # Calculate training statistics
        total_sessions = len(sessions)
        if not sessions:
            return f"No training sessions found in {timeframe}. User is just starting their martial arts journey."
        
        # Calculate frequency and patterns
        recent_sessions = [s for s in sessions if self._is_recent(s.get('date', s.get('created_at')))]
        
        # Handle different field names that might be used
        total_duration = 0
        total_intensity = 0
        valid_sessions = 0
        
        for session in sessions:
            # Try different possible field names for duration
            duration = session.get('duration_minutes') or session.get('duration') or 0
            total_duration += duration
            
            # Try different possible field names for intensity
            intensity = session.get('intensity') or session.get('intensity_level') or 0
            if intensity > 0:
                total_intensity += intensity
                valid_sessions += 1
        
        avg_intensity = total_intensity / valid_sessions if valid_sessions > 0 else 0
        avg_duration = total_duration / total_sessions if total_sessions > 0 else 0
        
        # Identify common styles and techniques
        styles = []
        for session in sessions:
            style = session.get('martial_art_style') or session.get('style') or session.get('art_style')
            if style:
                styles.append(style)
        
        style_counts = {}
        for style in styles:
            style_counts[style] = style_counts.get(style, 0) + 1
        
        # Get most common styles
        top_styles = sorted(style_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        summary = f"""
        Training Profile ({timeframe}):
        - Total Sessions: {total_sessions}
        - Recent Sessions (last 30 days): {len(recent_sessions)}
        - Average Duration: {avg_duration:.0f} minutes per session
        - Average Intensity: {avg_intensity:.1f}/10
        - Primary Martial Arts: {', '.join([style for style, count in top_styles])}
        - User Experience: {user_profile.get('experience_level', 'Not specified')}
        - Training Goals: {user_profile.get('goals', 'Not specified')}
        
        Recent Training Pattern:
        """
        
        # Add recent session details (last 5)
        for session in recent_sessions[-5:]:
            style = session.get('martial_art_style', session.get('style', 'Unknown'))
            duration = session.get('duration_minutes', session.get('duration', 0))
            intensity = session.get('intensity', session.get('intensity_level', 0))
            summary += f"- {style}: {duration}min, intensity {intensity}/10\n"
        
        # Add technique progress if available
        if techniques:
            summary += f"\nTechnique Progress: {len(techniques)} techniques being tracked\n"
            high_level = [t for t in techniques if t.get('current_level', 0) >= 7]
            low_level = [t for t in techniques if t.get('current_level', 0) <= 3]
            summary += f"- Advanced techniques (7+): {len(high_level)}\n"
            summary += f"- Beginner techniques (≤3): {len(low_level)}\n"
        
        return summary
    
    def _prepare_technique_summary(self, technique_data: List[Dict]) -> str:
        """Prepare technique progress summary"""
        if not technique_data:
            return "No technique progress data available."
        
        summary = f"Technique Progress Summary ({len(technique_data)} techniques):\n"
        
        # Group by skill level
        beginner = []  # 1-3
        intermediate = []  # 4-6
        advanced = []  # 7-10
        
        for tech in technique_data:
            level = tech.get('current_level', 0)
            name = tech.get('technique_name', 'Unknown')
            target = tech.get('target_level', 'N/A')
            
            if level <= 3:
                beginner.append(f"{name} (Level {level}, Target: {target})")
            elif level <= 6:
                intermediate.append(f"{name} (Level {level}, Target: {target})")
            else:
                advanced.append(f"{name} (Level {level}, Target: {target})")
        
        if beginner:
            summary += f"\nBeginner Level (1-3): {len(beginner)} techniques\n"
            for tech in beginner[:3]:  # Show first 3
                summary += f"  - {tech}\n"
        
        if intermediate:
            summary += f"\nIntermediate Level (4-6): {len(intermediate)} techniques\n"
            for tech in intermediate[:3]:
                summary += f"  - {tech}\n"
        
        if advanced:
            summary += f"\nAdvanced Level (7-10): {len(advanced)} techniques\n"
            for tech in advanced[:3]:
                summary += f"  - {tech}\n"
        
        return summary
    
    def _create_analysis_prompt(self, training_summary: str, timeframe: str) -> str:
        """Create AI prompt for training analysis"""
        return f"""
        You are an expert martial arts coach and training analyst. Analyze this training data and provide practical insights:

        {training_summary}
        
        Analysis Period: {timeframe}

        Provide analysis in these specific areas:
        1. **Training Consistency**: Are they training regularly? What patterns do you see?
        2. **Intensity Management**: Is their training intensity appropriate for their level?
        3. **Skill Development**: What areas need focus based on their training?
        4. **Balance Assessment**: Are they covering all important aspects of martial arts?
        5. **Progress Opportunities**: What specific improvements can they make?

        Format your response with clear, actionable insights. Each insight should:
        - Have a clear title
        - Explain what you observed
        - Give specific recommendations
        - Be encouraging and motivational

        Focus on practical advice they can implement in their next training sessions.
        Keep insights concise but valuable - this is for a martial artist who wants to improve.
        """
    
    def _parse_ai_response(self, response_text: str, user_data: Dict[str, Any]) -> List[TrainingInsight]:
        """Parse AI response and convert to TrainingInsight objects"""
        insights = []
        
        try:
            # Split response into sections
            lines = response_text.split('\n')
            current_insight = None
            collecting_content = False
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Look for numbered sections or **headers**
                if (line.startswith(('1.', '2.', '3.', '4.', '5.')) or 
                    (line.startswith('**') and line.endswith('**')) or
                    line.startswith('###')):
                    
                    # Save previous insight
                    if current_insight and current_insight.message.strip():
                        insights.append(current_insight)
                    
                    # Extract title
                    title = line
                    title = title.replace('*', '').replace('#', '')
                    title = title.replace('1.', '').replace('2.', '').replace('3.', '').replace('4.', '').replace('5.', '')
                    title = title.strip()
                    
                    # Determine insight type
                    insight_type = 'recommendation'
                    if 'consistency' in title.lower():
                        insight_type = 'pattern'
                    elif 'progress' in title.lower() or 'improvement' in title.lower():
                        insight_type = 'achievement'
                    elif 'warning' in title.lower() or 'concern' in title.lower():
                        insight_type = 'warning'
                    
                    # Start new insight
                    current_insight = TrainingInsight(
                        type=insight_type,
                        title=title,
                        message='',
                        confidence=0.8,
                        action_items=[],
                        data_points={}
                    )
                    collecting_content = True
                    
                elif current_insight and collecting_content:
                    # Add to current insight message
                    current_insight.message += line + ' '
                    
                    # Extract action items
                    if any(keyword in line.lower() for keyword in ['should', 'try', 'consider', 'recommend', 'focus on', 'work on']):
                        action = line.replace('-', '').replace('•', '').strip()
                        if action and len(action) > 10 and action not in current_insight.action_items:
                            current_insight.action_items.append(action)
            
            # Add the last insight
            if current_insight and current_insight.message.strip():
                insights.append(current_insight)
            
            # If no insights parsed, create a general one
            if not insights:
                insights.append(TrainingInsight(
                    type='general',
                    title='Training Analysis',
                    message=response_text[:300] + '...' if len(response_text) > 300 else response_text,
                    confidence=0.7,
                    action_items=['Continue training consistently'],
                    data_points={}
                ))
            
            # Add some data points based on user data
            sessions = user_data.get('sessions', [])
            if sessions:
                total_sessions = len(sessions)
                avg_duration = sum(s.get('duration_minutes', s.get('duration', 0)) for s in sessions) / total_sessions
                
                for insight in insights:
                    insight.data_points.update({
                        'total_sessions': total_sessions,
                        'avg_duration': round(avg_duration, 1),
                        'timeframe': user_data.get('timeframe', 'last_30_days')
                    })
        
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            insights = [TrainingInsight(
                type='warning',
                title='Analysis Complete',
                message='Training analysis completed successfully. Continue your martial arts journey with consistency and focus.',
                confidence=0.5,
                action_items=['Review your training patterns manually', 'Set specific goals for improvement'],
                data_points={}
            )]
        
        return insights[:4]  # Limit to 4 insights for UI
    
    def _parse_technique_response(self, response_text: str, technique_data: List[Dict]) -> List[TrainingInsight]:
        """Parse technique-specific AI response"""
        try:
            # Create technique-focused insights
            insights = []
            
            if technique_data:
                total_techniques = len(technique_data)
                avg_level = sum(t.get('current_level', 0) for t in technique_data) / total_techniques
                
                insight = TrainingInsight(
                    type='technique',
                    title='Technique Progress Analysis',
                    message=response_text[:400] + '...' if len(response_text) > 400 else response_text,
                    confidence=0.8,
                    action_items=[
                        'Focus on techniques below your target level',
                        'Practice fundamental movements daily',
                        'Track progress consistently'
                    ],
                    data_points={
                        'total_techniques': total_techniques,
                        'average_level': round(avg_level, 1)
                    }
                )
                insights.append(insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error parsing technique response: {e}")
            return []
    
    def _is_recent(self, date_str: str, days: int = 30) -> bool:
        """Check if a date string is within the last N days"""
        try:
            if isinstance(date_str, str):
                # Try different date formats
                for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f']:
                    try:
                        date_obj = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    return False
            else:
                date_obj = date_str
            
            return (datetime.now() - date_obj).days <= days
        except:
            return False

# Global service instance
gemini_service = GeminiService()

def get_gemini_service() -> GeminiService:
    """Get the global Gemini service instance"""
    return gemini_service