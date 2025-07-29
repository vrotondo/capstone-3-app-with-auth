import os
import cv2
import tempfile
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import google.generativeai as genai
from PIL import Image
import numpy as np

class AIVideoAnalysisService:
    """
    Advanced AI service for analyzing martial arts technique videos using Google Gemini Vision
    """
    
    def __init__(self):
        """Initialize the AI service with Gemini configuration"""
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Analysis configuration
        self.max_frames = 10  # Number of frames to analyze per video
        self.analysis_timeout = 60  # Seconds
        
        print("🤖 AI Video Analysis Service initialized with Gemini 1.5 Flash")

    def extract_key_frames(self, video_path: str, num_frames: int = 10) -> List[Image.Image]:
        """
        Extract key frames from video for AI analysis
        
        Args:
            video_path: Path to the video file
            num_frames: Number of frames to extract
            
        Returns:
            List of PIL Images representing key frames
        """
        try:
            print(f"📹 Extracting {num_frames} key frames from video...")
            
            # Open video with OpenCV
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Could not open video file: {video_path}")
            
            # Get video properties
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps if fps > 0 else 0
            
            print(f"📊 Video stats: {total_frames} frames, {fps:.2f} FPS, {duration:.2f}s")
            
            # Calculate frame indices to extract (evenly distributed)
            if total_frames <= num_frames:
                frame_indices = list(range(total_frames))
            else:
                frame_indices = [int(i * total_frames / num_frames) for i in range(num_frames)]
            
            extracted_frames = []
            
            for frame_idx in frame_indices:
                # Set video position to specific frame
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if ret:
                    # Convert BGR (OpenCV) to RGB (PIL)
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Convert to PIL Image
                    pil_image = Image.fromarray(frame_rgb)
                    
                    # Resize if too large (Gemini has size limits)
                    max_size = 1024
                    if max(pil_image.size) > max_size:
                        pil_image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                    
                    extracted_frames.append(pil_image)
                    print(f"✅ Extracted frame {frame_idx}/{total_frames} ({len(extracted_frames)}/{num_frames})")
                else:
                    print(f"⚠️ Could not extract frame {frame_idx}")
            
            cap.release()
            print(f"🎬 Successfully extracted {len(extracted_frames)} frames")
            return extracted_frames
            
        except Exception as e:
            print(f"❌ Error extracting frames: {str(e)}")
            return []

    def generate_analysis_prompt(self, technique_name: str = None, martial_art_style: str = None) -> str:
        """
        Generate a comprehensive prompt for martial arts technique analysis
        
        Args:
            technique_name: Specific technique being performed (e.g., "roundhouse kick")
            martial_art_style: Martial art style (e.g., "Taekwondo", "Karate")
            
        Returns:
            Detailed analysis prompt for the AI
        """
        
        base_prompt = """
You are an expert martial arts instructor and technique analyst. Analyze the martial arts technique shown in these video frames with the precision of a master coach.

ANALYSIS FRAMEWORK:

1. **TECHNIQUE IDENTIFICATION**
   - Identify the primary technique being performed
   - Recognize the martial art style if evident
   - Note any combination techniques or transitions

2. **FORM ANALYSIS** (Score 1-10)
   - Stance and balance throughout the movement
   - Body alignment and posture
   - Hand/foot positioning and technique execution
   - Hip rotation and power generation
   - Follow-through and recovery

3. **TIMING AND FLOW** (Score 1-10)
   - Smooth transition between phases
   - Proper sequence of body movements
   - Rhythm and cadence
   - Speed appropriateness for the technique

4. **POWER AND MECHANICS** (Score 1-10)
   - Efficient use of body mechanics
   - Transfer of power from ground through body
   - Proper muscle engagement
   - Impact potential (if applicable)

5. **DEFENSIVE AWARENESS** (Score 1-10)
   - Maintaining guard position
   - Balance recovery
   - Vulnerability assessment
   - Counter-attack readiness

6. **OVERALL TECHNICAL EXECUTION** (Score 1-10)
   - Adherence to proper technique standards
   - Consistency across repetitions
   - Level of mastery demonstrated

PROVIDE YOUR ANALYSIS IN THIS JSON FORMAT:
{
    "technique_identified": "Name of the technique",
    "martial_art_style": "Identified style or 'Mixed/Unknown'",
    "overall_score": 0-10,
    "detailed_scores": {
        "form_analysis": 0-10,
        "timing_and_flow": 0-10,
        "power_and_mechanics": 0-10,
        "defensive_awareness": 0-10,
        "technical_execution": 0-10
    },
    "strengths": [
        "List specific things done well",
        "Be encouraging and specific"
    ],
    "areas_for_improvement": [
        "List specific areas to work on",
        "Provide actionable feedback"
    ],
    "coaching_tips": [
        "Specific drills or exercises to improve",
        "Technical adjustments to make",
        "Practice recommendations"
    ],
    "safety_considerations": [
        "Any safety concerns observed",
        "Injury prevention advice"
    ],
    "next_steps": [
        "Recommended progression",
        "Skills to work on next"
    ]
}

"""
        
        # Add specific technique context if provided
        if technique_name:
            base_prompt += f"\nSPECIFIC TECHNIQUE FOCUS: Analyze this as a '{technique_name}' technique."
        
        if martial_art_style:
            base_prompt += f"\nMARTIAL ART CONTEXT: Evaluate according to '{martial_art_style}' standards and principles."
        
        base_prompt += """

Be thorough, constructive, and encouraging in your analysis. Focus on helping the practitioner improve while acknowledging their current skill level.
"""
        
        return base_prompt

    def analyze_technique_frames(self, frames: List[Image.Image], technique_name: str = None, 
                               martial_art_style: str = None) -> Dict:
        """
        Analyze martial arts technique using extracted video frames
        
        Args:
            frames: List of PIL Images from the video
            technique_name: Specific technique being analyzed
            martial_art_style: Martial art style context
            
        Returns:
            Comprehensive analysis results dictionary
        """
        try:
            if not frames:
                return {"error": "No frames provided for analysis"}
            
            print(f"🔍 Analyzing {len(frames)} frames with Gemini AI...")
            
            # Generate analysis prompt
            prompt = self.generate_analysis_prompt(technique_name, martial_art_style)
            
            # Prepare content for Gemini (prompt + images)
            content = [prompt] + frames
            
            print("🤖 Sending frames to Gemini for analysis...")
            
            # Generate analysis with Gemini
            response = self.model.generate_content(
                content,
                generation_config=genai.types.GenerationConfig(
                    candidate_count=1,
                    max_output_tokens=2048,
                    temperature=0.7,  # Slightly creative but mostly factual
                )
            )
            
            print("✅ Received analysis from Gemini")
            
            # Extract and parse the response
            analysis_text = response.text
            print(f"📝 Raw analysis length: {len(analysis_text)} characters")
            
            # Try to extract JSON from the response
            try:
                # Look for JSON structure in the response
                json_start = analysis_text.find('{')
                json_end = analysis_text.rfind('}') + 1
                
                if json_start != -1 and json_end != -1:
                    json_str = analysis_text[json_start:json_end]
                    analysis_data = json.loads(json_str)
                    
                    # Add metadata
                    analysis_data['analysis_timestamp'] = datetime.utcnow().isoformat()
                    analysis_data['frames_analyzed'] = len(frames)
                    analysis_data['ai_model'] = 'gemini-1.5-flash'
                    analysis_data['raw_response'] = analysis_text
                    
                    print("🎯 Analysis successfully parsed and structured")
                    return analysis_data
                    
                else:
                    # Fallback: return raw text if JSON parsing fails
                    print("⚠️ Could not parse JSON, returning raw analysis")
                    return {
                        "error": "Could not parse structured analysis",
                        "raw_analysis": analysis_text,
                        "analysis_timestamp": datetime.utcnow().isoformat(),
                        "frames_analyzed": len(frames),
                        "ai_model": 'gemini-1.5-flash'
                    }
                    
            except json.JSONDecodeError as json_error:
                print(f"⚠️ JSON parsing error: {json_error}")
                return {
                    "error": f"JSON parsing failed: {str(json_error)}",
                    "raw_analysis": analysis_text,
                    "analysis_timestamp": datetime.utcnow().isoformat(),
                    "frames_analyzed": len(frames),
                    "ai_model": 'gemini-1.5-flash'
                }
                
        except Exception as e:
            print(f"❌ Analysis error: {str(e)}")
            return {
                "error": f"Analysis failed: {str(e)}",
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "frames_analyzed": len(frames) if frames else 0
            }

    def analyze_video_file(self, video_path: str, technique_name: str = None, 
                          martial_art_style: str = None) -> Dict:
        """
        Complete video analysis pipeline: extract frames and analyze technique
        
        Args:
            video_path: Path to the video file to analyze
            technique_name: Specific technique being performed
            martial_art_style: Martial art style context
            
        Returns:
            Complete analysis results
        """
        try:
            print(f"🎥 Starting complete video analysis for: {video_path}")
            print(f"🥋 Technique: {technique_name or 'Auto-detect'}")
            print(f"🎯 Style: {martial_art_style or 'Auto-detect'}")
            
            # Step 1: Extract key frames
            frames = self.extract_key_frames(video_path, self.max_frames)
            
            if not frames:
                return {
                    "error": "Could not extract frames from video",
                    "video_path": video_path
                }
            
            # Step 2: Analyze technique
            analysis_results = self.analyze_technique_frames(
                frames, technique_name, martial_art_style
            )
            
            # Step 3: Add video metadata
            analysis_results['video_path'] = video_path
            analysis_results['extraction_success'] = len(frames) > 0
            
            print("🏆 Video analysis completed successfully!")
            return analysis_results
            
        except Exception as e:
            print(f"❌ Complete analysis failed: {str(e)}")
            return {
                "error": f"Complete analysis failed: {str(e)}",
                "video_path": video_path,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }

    def get_analysis_summary(self, analysis_results: Dict) -> str:
        """
        Generate a human-readable summary of the analysis results
        
        Args:
            analysis_results: Analysis results dictionary
            
        Returns:
            Formatted summary string
        """
        if "error" in analysis_results:
            return f"Analysis Error: {analysis_results['error']}"
        
        try:
            technique = analysis_results.get('technique_identified', 'Unknown')
            overall_score = analysis_results.get('overall_score', 0)
            style = analysis_results.get('martial_art_style', 'Unknown')
            
            summary = f"🥋 {technique} ({style})\n"
            summary += f"🎯 Overall Score: {overall_score}/10\n\n"
            
            # Add key strengths
            strengths = analysis_results.get('strengths', [])
            if strengths:
                summary += "💪 Strengths:\n"
                for strength in strengths[:3]:  # Top 3
                    summary += f"  • {strength}\n"
                summary += "\n"
            
            # Add key improvements
            improvements = analysis_results.get('areas_for_improvement', [])
            if improvements:
                summary += "🎓 Areas for Improvement:\n"
                for improvement in improvements[:3]:  # Top 3
                    summary += f"  • {improvement}\n"
            
            return summary
            
        except Exception as e:
            return f"Summary generation error: {str(e)}"

# Test function for development
def test_ai_analysis():
    """Test function to verify AI analysis setup"""
    try:
        service = AIVideoAnalysisService()
        print("✅ AI Analysis Service created successfully")
        
        # Test prompt generation
        prompt = service.generate_analysis_prompt("roundhouse kick", "Taekwondo")
        print(f"✅ Generated analysis prompt ({len(prompt)} characters)")
        
        return True
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Run test when script is executed directly
    test_ai_analysis()