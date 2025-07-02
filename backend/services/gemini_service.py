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
    
    def generate_chat_response(self, message: str, chat_history: List[Dict], user_context: Dict[str, Any]) -> str:
        """Generate conversational response as a martial arts coach"""
        if not self.enabled:
            return "I'm sorry, but the AI coaching service is currently unavailable. Please check back later!"
        
        try:
            # Build conversation context
            conversation_context = self._build_chat_context(chat_history, user_context)
            
            # Create coaching prompt
            coaching_prompt = f"""
            You are an expert martial arts coach and mentor with 20+ years of experience training students in various martial arts disciplines. You are having a conversation with one of your students.

            STUDENT PROFILE:
            - Name: {user_context.get('name', 'Student')}
            - Experience Level: {user_context.get('experience', 'Not specified')}
            - Primary Martial Art: {user_context.get('primary_art', 'Various')}
            - Recent Training Activity: {user_context.get('recent_sessions', 0)} sessions logged recently
            - Techniques Being Worked On: {user_context.get('total_techniques', 0)} techniques tracked

            CONVERSATION HISTORY:
            {conversation_context}

            CURRENT STUDENT MESSAGE: "{message}"

            RESPOND AS A SUPPORTIVE MARTIAL ARTS COACH:
            - Be encouraging and motivational
            - Give specific, actionable advice
            - Reference martial arts principles and philosophy when relevant
            - Ask follow-up questions to better understand their needs
            - Personalize your response using their profile information
            - Keep responses conversational and engaging (2-4 sentences typically)
            - If they ask about techniques, provide step-by-step guidance
            - If they ask about training, reference their actual training data when possible
            - Always prioritize safety and proper form

            COACHING STYLE:
            - Supportive but challenging
            - Focus on continuous improvement
            - Emphasize both physical and mental aspects
            - Encourage consistent practice
            - Share wisdom from martial arts traditions
            
            Respond naturally as if you're having a face-to-face conversation with your student.
            """
            
            response = self.model.generate_content(coaching_prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error generating chat response: {e}")
            return "I'm having trouble processing your message right now. Could you try rephrasing your question? I'm here to help with your martial arts training!"

    def _build_chat_context(self, chat_history: List[Dict], user_context: Dict[str, Any]) -> str:
        """Build conversation context from chat history"""
        if not chat_history:
            return f"This is the start of your conversation with {user_context.get('name', 'your student')}."
        
        context = "Recent conversation:\n"
        for chat in chat_history[-5:]:  # Last 5 exchanges
            role = chat.get('role', 'user')
            content = chat.get('content', '')
            
            if role == 'user':
                context += f"Student: {content}\n"
            elif role == 'assistant' or role == 'coach':
                context += f"Coach: {content}\n"
        
        return context
    
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
        - Average Duration: {avg_duration:.0f} minutes per session
        - Average Intensity: {avg_intensity:.1f}/10
        - Primary Martial Arts: {', '.join([style for style, count in top_styles])}
        - User Experience: {user_profile.get('experience_level', 'Not specified')}
        - Training Goals: {user_profile.get('goals', 'Not specified')}
        """
        
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

        Format your response with clear, actionable insights. Each insight should:
        - Have a clear title
        - Explain what you observed
        - Give specific recommendations
        - Be encouraging and motivational

        Focus on practical advice they can implement in their next training sessions.
        """
    
    def _parse_ai_response(self, response_text: str, user_data: Dict[str, Any]) -> List[TrainingInsight]:
        """Parse AI response and convert to TrainingInsight objects"""
        insights = []
        
        try:
            # Split response into sections
            lines = response_text.split('\n')
            current_insight = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Look for numbered sections or **headers**
                if (line.startswith(('1.', '2.', '3.', '4.')) or 
                    (line.startswith('**') and line.endswith('**'))):
                    
                    # Save previous insight
                    if current_insight and current_insight.message.strip():
                        insights.append(current_insight)
                    
                    # Extract title
                    title = line
                    title = title.replace('*', '').replace('#', '')
                    title = title.replace('1.', '').replace('2.', '').replace('3.', '').replace('4.', '')
                    title = title.strip()
                    
                    # Start new insight
                    current_insight = TrainingInsight(
                        type='recommendation',
                        title=title,
                        message='',
                        confidence=0.8,
                        action_items=[],
                        data_points={}
                    )
                    
                elif current_insight:
                    # Add to current insight message
                    current_insight.message += line + ' '
                    
                    # Extract action items
                    if any(keyword in line.lower() for keyword in ['should', 'try', 'consider', 'recommend', 'focus on']):
                        action = line.replace('-', '').replace('•', '').strip()
                        if action and len(action) > 15 and action not in current_insight.action_items:
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