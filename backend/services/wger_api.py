import os
import requests
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import time
import logging

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
    uuid: Optional[str] = None
    images: Optional[List[str]] = None

class WgerAPIService:
    """Enhanced service for interacting with wger Exercise Database API"""
    
    def __init__(self, api_key=None):
        # Fix: Add missing import and parameter
        self.base_url = "https://wger.de/api/v2"
        self.api_key = api_key or os.getenv('WGER_API_KEY')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DojoTracker/1.0 (Martial Arts Training App)',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

        # Fix: Add API key authentication
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Token {self.api_key}' 
            })
            print(f"🔑 wger API key configured")
        else:
            print("⚠️ No wger API key - using public endpoints only")
        
        # Enhanced cache with longer duration for static data
        self.cache = {}
        self.cache_duration = 3600  # 1 hour for dynamic data
        self.static_cache_duration = 86400  # 24 hours for categories, muscles, equipment
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Track API calls for rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests
        
    def _rate_limit(self):
        """Implement simple rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
        
    def _make_request(self, endpoint: str, params: Dict = None, use_static_cache: bool = False) -> Dict:
        """Make authenticated request to wger API with enhanced caching"""
        cache_key = f"{endpoint}_{str(params)}"
        cache_duration = self.static_cache_duration if use_static_cache else self.cache_duration
        
        # Check cache first
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < cache_duration:
                self.logger.info(f"📋 Using cached data for {endpoint}")
                return cached_data
        
        # Rate limiting
        self._rate_limit()
        
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            self.logger.info(f"🌐 Making request to: {url}")
            
            # Add default parameters for better results
            default_params = {
                'status': 2,  # Only approved exercises
                'limit': 100  # Get more results per page
            }
            
            if params:
                default_params.update(params)
            
            response = self.session.get(url, params=default_params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            # Cache the response
            self.cache[cache_key] = (data, time.time())
            self.logger.info(f"✅ Successfully fetched {endpoint}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ wger API request failed: {str(e)}")
            return {}
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ Invalid JSON response from wger API: {str(e)}")
            return {}
    
    def _fetch_all_pages(self, endpoint: str, params: Dict = None, max_pages: int = 10) -> List[Dict]:
        """Fetch multiple pages of results with limit to prevent infinite loops"""
        all_results = []
        current_params = params.copy() if params else {}
        page_count = 0
        
        while page_count < max_pages:
            data = self._make_request(endpoint, current_params)
            
            if not data or 'results' not in data:
                break
                
            results = data['results']
            if not results:
                break
                
            all_results.extend(results)
            
            # Check for next page
            next_url = data.get('next')
            if not next_url:
                break
                
            # Extract offset from next URL
            try:
                from urllib.parse import urlparse, parse_qs
                parsed = urlparse(next_url)
                query_params = parse_qs(parsed.query)
                if 'offset' in query_params:
                    current_params['offset'] = int(query_params['offset'][0])
                else:
                    break
            except (ValueError, IndexError):
                break
                
            page_count += 1
            
        self.logger.info(f"Fetched {len(all_results)} total results from {page_count + 1} pages")
        return all_results
    
    def get_exercise_categories(self) -> List[Dict]:
        """Get all exercise categories with enhanced data"""
        data = self._make_request("exercisecategory/", use_static_cache=True)
        categories = data.get('results', [])
        
        # Enhance categories with exercise counts
        for category in categories:
            try:
                # Get exercise count for this category
                exercise_data = self._make_request("exercise/", {
                    'category': category['id'],
                    'limit': 1
                })
                category['exercise_count'] = exercise_data.get('count', 0)
            except:
                category['exercise_count'] = 0
                
        return categories
    
    def get_muscles(self) -> List[Dict]:
        """Get all muscle groups"""
        data = self._make_request("muscle/", use_static_cache=True)
        return data.get('results', [])
    
    def get_equipment(self) -> List[Dict]:
        """Get all equipment types"""
        data = self._make_request("equipment/", use_static_cache=True)
        return data.get('results', [])
    
    def get_exercises(self, limit: int = 50, offset: int = 0, 
                     category: Optional[int] = None, 
                     muscle: Optional[int] = None,
                     equipment: Optional[int] = None,
                     language: int = 2,  # 2 = English
                     search: Optional[str] = None) -> Dict:
        """Get exercises with enhanced filtering options"""
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
        if search:
            params['search'] = search
            
        return self._make_request("exercise/", params)
    
    def get_exercise_details(self, exercise_id: int) -> Optional[WgerExercise]:
        """Get comprehensive details for a specific exercise"""
        exercise_data = self._make_request(f"exercise/{exercise_id}/")
        
        if not exercise_data:
            return None
        
        try:
            # Get exercise info (descriptions, instructions)
            exercise_info = self._get_exercise_info(exercise_id)
            
            # Get muscles from the exercise data itself
            primary_muscles = []
            secondary_muscles = []
            
            # Get muscle names from IDs
            all_muscles = self.get_muscles()
            muscle_map = {m['id']: m['name'] for m in all_muscles}
            
            for muscle_id in exercise_data.get('muscles', []):
                muscle_name = muscle_map.get(muscle_id, f'Muscle #{muscle_id}')
                primary_muscles.append(muscle_name)
                
            for muscle_id in exercise_data.get('muscles_secondary', []):
                muscle_name = muscle_map.get(muscle_id, f'Muscle #{muscle_id}')
                secondary_muscles.append(muscle_name)
            
            # Get equipment names from IDs
            all_equipment = self.get_equipment()
            equipment_map = {e['id']: e['name'] for e in all_equipment}
            
            equipment_names = []
            for eq_id in exercise_data.get('equipment', []):
                eq_name = equipment_map.get(eq_id, f'Equipment #{eq_id}')
                equipment_names.append(eq_name)
            
            # Get category name
            categories = self.get_exercise_categories()
            category_map = {c['id']: c['name'] for c in categories}
            category_name = category_map.get(exercise_data.get('category'), 'Unknown')
            
            return WgerExercise(
                id=exercise_data.get('id'),
                name=exercise_info.get('name', f'Exercise #{exercise_id}'),
                description=exercise_info.get('description', ''),
                category=category_name,
                muscles=primary_muscles,
                muscles_secondary=secondary_muscles,
                equipment=equipment_names,
                instructions=exercise_info.get('instructions', []),
                variations=exercise_data.get('variations', []),
                license_author=exercise_data.get('license_author', ''),
                creation_date=exercise_data.get('creation_date', ''),
                uuid=exercise_data.get('uuid'),
                images=exercise_info.get('images', [])
            )
        except Exception as e:
            self.logger.error(f"❌ Error creating WgerExercise object: {str(e)}")
            return None
    
    def _get_exercise_info(self, exercise_id: int) -> Dict:
        """Get exercise information including descriptions and instructions"""
        try:
            # Try to get exercise info
            info_data = self._make_request(f"exerciseinfo/", {
                'exercise': exercise_id,
                'language': 2  # English
            })
            
            if info_data and info_data.get('results'):
                info = info_data['results'][0]
                return {
                    'name': info.get('name', ''),
                    'description': info.get('description', ''),
                    'instructions': [info.get('description', '')],  # Simplified
                    'images': []  # Could be enhanced to fetch actual images
                }
            else:
                return {
                    'name': f'Exercise #{exercise_id}',
                    'description': 'No description available',
                    'instructions': [],
                    'images': []
                }
        except Exception as e:
            self.logger.error(f"Error getting exercise info: {e}")
            return {
                'name': f'Exercise #{exercise_id}',
                'description': 'No description available',
                'instructions': [],
                'images': []
            }
    
    def search_exercises(self, query: str, limit: int = 20) -> List[Dict]:
        """Enhanced exercise search with better relevance"""
        params = {
            'search': query,
            'limit': limit,
            'language': 2,  # English
            'status': 2     # Only approved
        }
        
        data = self._make_request("exercise/", params)
        results = data.get('results', [])
        
        # Enhance results with additional info
        enhanced_results = []
        for exercise in results:
            try:
                # Add muscle and equipment names
                enhanced_exercise = exercise.copy()
                
                # Get category name
                categories = self.get_exercise_categories()
                category_map = {c['id']: c['name'] for c in categories}
                enhanced_exercise['category_name'] = category_map.get(exercise.get('category'), 'Unknown')
                
                enhanced_results.append(enhanced_exercise)
            except:
                enhanced_results.append(exercise)
        
        return enhanced_results
    
    def get_exercises_by_category(self, category_name: str, limit: int = 50) -> List[Dict]:
        """Get exercises for a specific category with enhanced filtering"""
        # First get category ID
        categories = self.get_exercise_categories()
        category_id = None
        
        for cat in categories:
            if cat.get('name', '').lower() == category_name.lower():
                category_id = cat.get('id')
                break
        
        if not category_id:
            self.logger.warning(f"❌ Category '{category_name}' not found")
            return []
        
        data = self.get_exercises(limit=limit, category=category_id)
        return data.get('results', [])
    
    def get_martial_arts_relevant_exercises(self, limit: int = 100) -> List[Dict]:
        """Get exercises particularly relevant for martial arts training"""
        # First, let's get all available categories to see what's actually there
        all_categories = self.get_exercise_categories()
        print("🔍 Available categories:")
        for cat in all_categories:
            print(f"   - {cat.get('name', 'Unknown')}")
        
        # Use category names that actually exist in wger
        # These are more common wger category names
        martial_arts_categories = [
            'Arms',      # Usually exists
            'Legs',      # Usually exists  
            'Abs',       # Usually exists
            'Back',      # Usually exists
            'Chest',     # Usually exists
            'Shoulders', # Usually exists
            'Cardio'     # If it exists
        ]
        
        all_exercises = []
        
        # Get exercises by category - only use categories that exist
        for category in martial_arts_categories:
            try:
                exercises = self.get_exercises_by_category(category, limit=10)
                if exercises:
                    print(f"✅ Found {len(exercises)} exercises in category: {category}")
                    all_exercises.extend(exercises)
                else:
                    print(f"⚠️ No exercises found in category: {category}")
            except Exception as e:
                print(f"❌ Error fetching {category} exercises: {e}")
        
        # If no category exercises found, get some general exercises
        if not all_exercises:
            print("⚠️ No category exercises found, getting general exercises")
            try:
                general_exercises = self.get_exercises(limit=50)
                if general_exercises.get('results'):
                    all_exercises = general_exercises['results']
                    print(f"✅ Got {len(all_exercises)} general exercises")
            except Exception as e:
                print(f"❌ Error getting general exercises: {e}")
        
        # Add specific martial arts exercises by keyword search
        martial_arts_keywords = [
            'push', 'pull', 'squat', 'lunge', 'plank',
            'burpee', 'jump', 'core', 'balance'
        ]
        
        for keyword in martial_arts_keywords:
            try:
                keyword_exercises = self.search_exercises(keyword, limit=5)
                if keyword_exercises:
                    print(f"✅ Found {len(keyword_exercises)} exercises for keyword: {keyword}")
                    all_exercises.extend(keyword_exercises)
            except Exception as e:
                print(f"❌ Error searching for {keyword} exercises: {e}")
        
        # Remove duplicates based on exercise ID and limit results
        seen_ids = set()
        unique_exercises = []
        for exercise in all_exercises:
            exercise_id = exercise.get('id')
            if exercise_id and exercise_id not in seen_ids:
                unique_exercises.append(exercise)
                seen_ids.add(exercise_id)
                
                if len(unique_exercises) >= limit:
                    break
        
        print(f"✅ Final result: {len(unique_exercises)} unique martial arts relevant exercises")
        return unique_exercises
    
    def get_equipment_exercises(self, equipment_name: str, limit: int = 30) -> List[Dict]:
        """Get exercises that use specific equipment"""
        # Find equipment ID
        all_equipment = self.get_equipment()
        equipment_id = None
        
        for eq in all_equipment:
            if equipment_name.lower() in eq.get('name', '').lower():
                equipment_id = eq.get('id')
                break
        
        if not equipment_id:
            self.logger.warning(f"Equipment '{equipment_name}' not found")
            return []
        
        data = self.get_exercises(limit=limit, equipment=equipment_id)
        return data.get('results', [])
    
    def get_muscle_exercises(self, muscle_name: str, limit: int = 30) -> List[Dict]:
        """Get exercises that target a specific muscle"""
        # Find muscle ID
        all_muscles = self.get_muscles()
        muscle_id = None
        
        for muscle in all_muscles:
            if muscle_name.lower() in muscle.get('name', '').lower():
                muscle_id = muscle.get('id')
                break
        
        if not muscle_id:
            self.logger.warning(f"Muscle '{muscle_name}' not found")
            return []
        
        data = self.get_exercises(limit=limit, muscle=muscle_id)
        return data.get('results', [])
    
    def get_api_stats(self) -> Dict:
        """Get statistics about the wger API data"""
        try:
            categories = self.get_exercise_categories()
            muscles = self.get_muscles()
            equipment = self.get_equipment()
            
            # Get total exercise count
            exercises_data = self._make_request("exercise/", {'limit': 1})
            total_exercises = exercises_data.get('count', 0)
            
            return {
                'total_exercises': total_exercises,
                'total_categories': len(categories),
                'total_muscles': len(muscles),
                'total_equipment': len(equipment),
                'categories': [c['name'] for c in categories],
                'cache_size': len(self.cache)
            }
        except Exception as e:
            self.logger.error(f"Error getting API stats: {e}")
            return {}
    
    def test_connection(self) -> Dict:
        """Enhanced connection test with more comprehensive checks"""
        try:
            # Test basic connectivity
            start_time = time.time()
            
            # Test different endpoints
            tests = {
                'categories': self.get_exercise_categories(),
                'muscles': self.get_muscles(),
                'equipment': self.get_equipment(),
                'exercises': self.get_exercises(limit=5)
            }
            
            response_time = time.time() - start_time
            
            # Check if all tests passed
            all_passed = all(len(test_data) > 0 if isinstance(test_data, list) 
                           else test_data.get('results', []) for test_data in tests.values())
            
            stats = self.get_api_stats()
            
            return {
                'success': all_passed,
                'message': 'Successfully connected to wger API' if all_passed else 'Partial connection issues',
                'response_time': round(response_time, 2),
                'api_stats': stats,
                'test_results': {
                    'categories_count': len(tests['categories']),
                    'muscles_count': len(tests['muscles']),
                    'equipment_count': len(tests['equipment']),
                    'exercises_count': len(tests['exercises'].get('results', []))
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to connect to wger API: {str(e)}',
                'response_time': 0,
                'api_stats': {},
                'test_results': {}
            }
    
    def clear_cache(self):
        """Clear the API cache"""
        self.cache.clear()
        self.logger.info("API cache cleared")

# Fix: Create singleton instance with proper initialization
wger_service = WgerAPIService()