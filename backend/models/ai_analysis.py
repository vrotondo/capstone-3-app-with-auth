from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship

def create_ai_analysis_models(db):
    """
    Create AI analysis models for storing video analysis results
    """
    
    class VideoAnalysis(db.Model):
        """
        Main analysis results for a video
        """
        __tablename__ = 'video_analyses'
        
        id = Column(Integer, primary_key=True)
        
        # Foreign key to training video
        video_id = Column(Integer, ForeignKey('training_videos.id'), nullable=False)
        user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
        
        # Analysis metadata
        analysis_status = Column(String(20), default='pending')  # pending, processing, completed, failed
        started_at = Column(DateTime, default=datetime.utcnow)
        completed_at = Column(DateTime, nullable=True)
        
        # AI model information
        ai_model = Column(String(50), default='gemini-1.5-flash')
        frames_analyzed = Column(Integer, default=0)
        
        # Analysis context
        technique_name = Column(String(100), nullable=True)
        martial_art_style = Column(String(50), nullable=True)
        
        # Overall results
        overall_score = Column(Float, nullable=True)  # 0-10 scale
        technique_identified = Column(String(100), nullable=True)
        identified_style = Column(String(50), nullable=True)
        
        # Detailed scores (stored as JSON for flexibility)
        detailed_scores = Column(JSON, nullable=True)
        # Example: {"form_analysis": 8.5, "timing_and_flow": 7.2, ...}
        
        # Analysis content (stored as JSON)
        strengths = Column(JSON, nullable=True)  # List of strengths
        areas_for_improvement = Column(JSON, nullable=True)  # List of improvements
        coaching_tips = Column(JSON, nullable=True)  # List of coaching advice
        safety_considerations = Column(JSON, nullable=True)  # Safety notes
        next_steps = Column(JSON, nullable=True)  # Recommended next steps
        
        # Raw AI response for debugging/reference
        raw_ai_response = Column(Text, nullable=True)
        
        # Error handling
        error_message = Column(Text, nullable=True)
        
        # RELATIONSHIPS COMMENTED OUT FOR NOW - we'll add them back later
        # video = relationship("TrainingVideo", back_populates="analyses")
        # user = relationship("User", back_populates="video_analyses")
        feedback_items = relationship("AnalysisFeedback", back_populates="analysis", cascade="all, delete-orphan")
        
        def __repr__(self):
            return f'<VideoAnalysis {self.id}: {self.technique_name} - {self.overall_score}/10>'
        
        def to_dict(self):
            """Convert analysis to dictionary for API responses"""
            return {
                'id': self.id,
                'video_id': self.video_id,
                'analysis_status': self.analysis_status,
                'started_at': self.started_at.isoformat() if self.started_at else None,
                'completed_at': self.completed_at.isoformat() if self.completed_at else None,
                'ai_model': self.ai_model,
                'frames_analyzed': self.frames_analyzed,
                'technique_name': self.technique_name,
                'martial_art_style': self.martial_art_style,
                'overall_score': self.overall_score,
                'technique_identified': self.technique_identified,
                'identified_style': self.identified_style,
                'detailed_scores': self.detailed_scores,
                'strengths': self.strengths,
                'areas_for_improvement': self.areas_for_improvement,
                'coaching_tips': self.coaching_tips,
                'safety_considerations': self.safety_considerations,
                'next_steps': self.next_steps,
                'error_message': self.error_message
            }
        
        def get_summary_text(self):
            """Generate human-readable summary"""
            if self.analysis_status != 'completed' or not self.overall_score:
                return f"Analysis {self.analysis_status}"
            
            summary = f"🥋 {self.technique_identified or 'Technique'}"
            if self.identified_style:
                summary += f" ({self.identified_style})"
            summary += f"\n🎯 Overall Score: {self.overall_score}/10"
            
            if self.strengths and len(self.strengths) > 0:
                summary += f"\n💪 Key Strength: {self.strengths[0]}"
            
            if self.areas_for_improvement and len(self.areas_for_improvement) > 0:
                summary += f"\n🎓 Focus Area: {self.areas_for_improvement[0]}"
            
            return summary

    class AnalysisFeedback(db.Model):
        """
        Structured feedback items from analysis
        """
        __tablename__ = 'analysis_feedback'
        
        id = Column(Integer, primary_key=True)
        analysis_id = Column(Integer, ForeignKey('video_analyses.id'), nullable=False)
        
        # Feedback categorization
        feedback_type = Column(String(50), nullable=False)  # strength, improvement, coaching_tip, safety, next_step
        category = Column(String(50), nullable=True)  # form, timing, power, defense, etc.
        
        # Feedback content
        title = Column(String(200), nullable=False)
        description = Column(Text, nullable=True)
        priority = Column(Integer, default=1)  # 1=low, 2=medium, 3=high
        
        # Scoring if applicable
        score = Column(Float, nullable=True)
        max_score = Column(Float, default=10.0)
        
        # Relationships
        analysis = relationship("VideoAnalysis", back_populates="feedback_items")
        
        def __repr__(self):
            return f'<AnalysisFeedback {self.id}: {self.feedback_type} - {self.title}>'
        
        def to_dict(self):
            return {
                'id': self.id,
                'analysis_id': self.analysis_id,
                'feedback_type': self.feedback_type,
                'category': self.category,
                'title': self.title,
                'description': self.description,
                'priority': self.priority,
                'score': self.score,
                'max_score': self.max_score
            }

    class AnalysisProgress(db.Model):
        """
        Track user's progress over time based on analyses
        """
        __tablename__ = 'analysis_progress'
        
        id = Column(Integer, primary_key=True)
        user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
        
        # Progress tracking
        technique_name = Column(String(100), nullable=False)
        martial_art_style = Column(String(50), nullable=True)
        
        # Score progression
        first_analysis_id = Column(Integer, ForeignKey('video_analyses.id'), nullable=True)
        latest_analysis_id = Column(Integer, ForeignKey('video_analyses.id'), nullable=True)
        
        first_score = Column(Float, nullable=True)
        latest_score = Column(Float, nullable=True)
        best_score = Column(Float, nullable=True)
        average_score = Column(Float, nullable=True)
        
        # Statistics
        total_analyses = Column(Integer, default=0)
        improvement_rate = Column(Float, nullable=True)  # Score improvement per analysis
        
        # Timestamps
        first_analysis_date = Column(DateTime, nullable=True)
        latest_analysis_date = Column(DateTime, nullable=True)
        
        # RELATIONSHIPS COMMENTED OUT FOR NOW - we'll add them back later
        # user = relationship("User", back_populates="analysis_progress")
        first_analysis = relationship("VideoAnalysis", foreign_keys=[first_analysis_id])
        latest_analysis = relationship("VideoAnalysis", foreign_keys=[latest_analysis_id])
        
        def __repr__(self):
            return f'<AnalysisProgress {self.user_id}: {self.technique_name} - {self.latest_score}/10>'
        
        def to_dict(self):
            return {
                'id': self.id,
                'user_id': self.user_id,
                'technique_name': self.technique_name,
                'martial_art_style': self.martial_art_style,
                'first_score': self.first_score,
                'latest_score': self.latest_score,
                'best_score': self.best_score,
                'average_score': self.average_score,
                'total_analyses': self.total_analyses,
                'improvement_rate': self.improvement_rate,
                'first_analysis_date': self.first_analysis_date.isoformat() if self.first_analysis_date else None,
                'latest_analysis_date': self.latest_analysis_date.isoformat() if self.latest_analysis_date else None
            }
        
        def calculate_improvement(self):
            """Calculate improvement percentage"""
            if self.first_score and self.latest_score and self.first_score > 0:
                return ((self.latest_score - self.first_score) / self.first_score) * 100
            return 0

    # Return all models
    return VideoAnalysis, AnalysisFeedback, AnalysisProgress