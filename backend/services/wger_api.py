# Create this file: backend/services/wger_api.py

import requests
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import time

@dataclass
class WgerExercise:
    """Data class for wger exercise"""
    id: int
    name: str
    description: str
    category: str
    muscles: List[str]
    muscles_secondary: List[str]
    equipment: List[str]
    instructions: List[str]
    variations: List[str]
    license_author: str
    creation_date: str

class WgerAPIService:
    """Service for interacting with wger Exercise Database API"""
    
    def __init__(self):
        self.base_url = "https://wger.de/api/v2"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DojoTracker/1.0 (Martial Arts Training App)',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # Cache for API responses to avoid repeated calls
        self.cache = {}
        self.cache_duration = 3600  # 1 hour
        
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make authenticated request to wger API with caching"""
        cache_key = f"{endpoint}_{str(params)}"
        
        # Check cache first
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_duration:
                print(f"📋 Using cached data for {endpoint}")
                return cached_data
        
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            print(f"🌐 Making request to: {url}")
            
            response = self.session.get(url, params=params or {}, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Cache the response
            self.cache[cache_key] = (data, time.time())
            print(f"✅ Successfully fetched {endpoint}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ wger API request failed: {str(e)}")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response from wger API: {str(e)}")
            return {}
    
    def get_exercise_categories(self) -> List[Dict]:
        """Get all exercise categories"""
        data = self._make_request("exercisecategory/")
        return data.get('results', [])
    
    def get_muscles(self) -> List[Dict]:
        """Get all muscle groups"""
        data = self._make_request("muscle/")
        return data.get('results', [])
    
    def get_equipment(self) -> List[Dict]:
        """Get all equipment types"""
        data = self._make_request("equipment/")
        return data.get('results', [])
    
    def get_exercises(self, limit: int = 50, offset: int = 0, 
                     category: Optional[int] = None, 
                     muscle: Optional[int] = None,
                     equipment: Optional[int] = None,
                     language: int = 2) -> Dict:  # 2 = English
        """Get exercises with optional filtering"""
        params = {
            'limit': limit,
            'offset': offset,
            'language': language,
            'status': 2  # Only approved exercises
        }
        
        if category:
            params['category'] = category
        if muscle:
            params['muscles'] = muscle
        if equipment:
            params['equipment'] = equipment
            
        return self._make_request("exercise/", params)
    
    def get_exercise_details(self, exercise_id: int) -> Optional[WgerExercise]:
        """Get detailed information for a specific exercise"""
        exercise_data = self._make_request(f"exercise/{exercise_id}/")
        
        if not exercise_data:
            return None
        
        # Get additional details
        muscles = self._get_exercise_muscles(exercise_id)
        equipment = self._get_exercise_equipment(exercise_id)
        instructions = self._get_exercise_instructions(exercise_id)
        
        try:
            return WgerExercise(
                id=exercise_data.get('id'),
                name=exercise_data.get('name', ''),
                description=exercise_data.get('description', ''),
                category=exercise_data.get('category', {}).get('name', ''),
                muscles=muscles.get('primary', []),
                muscles_secondary=muscles.get('secondary', []),
                equipment=equipment,
                instructions=instructions,
                variations=exercise_data.get('variations', []),
                license_author=exercise_data.get('license_author', ''),
                creation_date=exercise_data.get('creation_date', '')
            )
        except Exception as e:
            print(f"❌ Error creating WgerExercise object: {str(e)}")
            return None
    
    def _get_exercise_muscles(self, exercise_id: int) -> Dict[str, List[str]]:
        """Get muscle groups for an exercise"""
        try:
            muscles_data = self._make_request(f"exercise/{exercise_id}/muscles/")
            primary = [m.get('name', '') for m in muscles_data.get('primary', [])]
            secondary = [m.get('name', '') for m in muscles_data.get('secondary', [])]
            return {'primary': primary, 'secondary': secondary}
        except:
            return {'primary': [], 'secondary': []}
    
    def _get_exercise_equipment(self, exercise_id: int) -> List[str]:
        """Get equipment needed for an exercise"""
        try:
            equipment_data = self._make_request(f"exercise/{exercise_id}/equipment/")
            return [eq.get('name', '') for eq in equipment_data.get('results', [])]
        except:
            return []
    
    def _get_exercise_instructions(self, exercise_id: int) -> List[str]:
        """Get step-by-step instructions for an exercise"""
        try:
            instructions_data = self._make_request(f"exerciseinfo/{exercise_id}/")
            return [inst.get('description', '') for inst in instructions_data.get('results', [])]
        except:
            return []
    
    def search_exercises(self, query: str, limit: int = 20) -> List[Dict]:
        """Search exercises by name"""
        params = {
            'search': query,
            'limit': limit,
            'language': 2,  # English
            'status': 2     # Only approved
        }
        
        data = self._make_request("exercise/", params)
        return data.get('results', [])
    
    def get_exercises_by_category(self, category_name: str, limit: int = 50) -> List[Dict]:
        """Get exercises for a specific category (e.g., 'Cardio', 'Strength')"""
        # First get category ID
        categories = self.get_exercise_categories()
        category_id = None
        
        for cat in categories:
            if cat.get('name', '').lower() == category_name.lower():
                category_id = cat.get('id')
                break
        
        if not category_id:
            print(f"❌ Category '{category_name}' not found")
            return []
        
        data = self.get_exercises(limit=limit, category=category_id)
        return data.get('results', [])
    
    def get_martial_arts_relevant_exercises(self) -> List[Dict]:
        """Get exercises particularly relevant for martial arts training"""
        martial_arts_categories = [
            'Cardio',
            'Strength', 
            'Stretching',
            'Plyometrics'
        ]
        
        all_exercises = []
        for category in martial_arts_categories:
            exercises = self.get_exercises_by_category(category, limit=20)
            all_exercises.extend(exercises)
        
        # Add specific martial arts exercises if available
        martial_arts_keywords = [
            'kick', 'punch', 'balance', 'flexibility', 'core', 
            'agility', 'coordination', 'reaction', 'speed'
        ]
        
        for keyword in martial_arts_keywords:
            keyword_exercises = self.search_exercises(keyword, limit=10)
            all_exercises.extend(keyword_exercises)
        
        # Remove duplicates based on exercise ID
        seen_ids = set()
        unique_exercises = []
        for exercise in all_exercises:
            if exercise.get('id') not in seen_ids:
                unique_exercises.append(exercise)
                seen_ids.add(exercise.get('id'))
        
        return unique_exercises[:100]  # Limit to 100 most relevant
    
    def test_connection(self) -> Dict:
        """Test the connection to wger API"""
        try:
            data = self._make_request("info/")
            return {
                'success': True,
                'message': 'Successfully connected to wger API',
                'api_info': data
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to connect to wger API: {str(e)}',
                'api_info': {}
            }

# Singleton instance
wger_service = WgerAPIService()