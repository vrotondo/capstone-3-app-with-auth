import os
import requests
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import time
import logging

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

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

        # Add API key authentication (will be removed for exercise endpoints)
        if self.api_key and self.api_key.strip():
            auth_header = f'Token {self.api_key.strip()}'
            self.session.headers.update({
                'Authorization': auth_header
            })
            print(f"🔑 wger API key configured for categories/muscles/equipment")
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
        
        # Initialize lookup maps for performance
        self._muscle_map = None
        self._equipment_map = None
        self._category_map = None
        
    def _rate_limit(self):
        """Implement simple rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
        
    def _make_request(self, endpoint: str, params: Dict = None, use_static_cache: bool = False) -> Dict:
        """Make request to wger API with enhanced caching"""
        cache_key = f"{endpoint}_{str(params)}"
        cache_duration = self.static_cache_duration if use_static_cache else self.cache_duration
        
        # Check cache first
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < cache_duration:
                return cached_data
        
        # Rate limiting
        self._rate_limit()
        
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            
            # Only add limit, don't add status parameter by default
            default_params = {
                'limit': 100  # Get more results per page
            }
            
            if params:
                default_params.update(params)
            
            response = self.session.get(url, params=default_params, timeout=15)
            
            if response.status_code == 403:
                print(f"❌ 403 Forbidden for {endpoint} - trying without auth...")
                return {}
                
            response.raise_for_status()
            
            data = response.json()
            
            # Cache the response
            self.cache[cache_key] = (data, time.time())
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ wger API request failed for {endpoint}: {str(e)}")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response from wger API: {str(e)}")
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

    def _get_lookup_maps(self):
        """Initialize and cache lookup maps for IDs to names"""
        try:
            if not self._muscle_map:
                muscles = self.get_muscles()
                self._muscle_map = {m['id']: m['name'] for m in muscles}
                
            if not self._equipment_map:
                equipment = self.get_equipment()
                self._equipment_map = {e['id']: e['name'] for e in equipment}
                
            if not self._category_map:
                categories = self.get_exercise_categories()
                self._category_map = {c['id']: c['name'] for c in categories}
                
        except Exception as e:
            print(f"⚠️ Error loading lookup maps: {e}")
            # Provide empty maps as fallback
            if not self._muscle_map:
                self._muscle_map = {}
            if not self._equipment_map:
                self._equipment_map = {}
            if not self._category_map:
                self._category_map = {}
    
    def _enhance_exercise_data(self, exercise: Dict) -> Dict:
        """Transform raw exercise data by resolving IDs to names - SIMPLIFIED VERSION"""
        self._get_lookup_maps()
        
        enhanced = exercise.copy()
        
        # Try to get name from various fields in the raw exercise data
        exercise_name = exercise.get('name', f"Exercise #{exercise.get('id', 'Unknown')}")
        enhanced['name'] = exercise_name
        
        # Try to get description from raw exercise data 
        exercise_description = exercise.get('description', 'No description available')
        enhanced['description'] = exercise_description
        
        # Resolve category ID to name
        category_id = exercise.get('category')
        if category_id and self._category_map:
            enhanced['category'] = self._category_map.get(category_id, f'Category {category_id}')
        else:
            enhanced['category'] = 'Unknown'
        enhanced['category_name'] = enhanced['category']
        
        # Resolve muscle IDs to names
        muscle_ids = exercise.get('muscles', [])
        if muscle_ids and self._muscle_map:
            enhanced['muscles'] = [
                self._muscle_map.get(muscle_id, f'Muscle {muscle_id}')
                for muscle_id in muscle_ids
            ]
        else:
            enhanced['muscles'] = []
        
        # Resolve secondary muscle IDs to names
        secondary_muscle_ids = exercise.get('muscles_secondary', [])
        if secondary_muscle_ids and self._muscle_map:
            enhanced['muscles_secondary'] = [
                self._muscle_map.get(muscle_id, f'Muscle {muscle_id}')
                for muscle_id in secondary_muscle_ids
            ]
        else:
            enhanced['muscles_secondary'] = []
        
        # Resolve equipment IDs to names
        equipment_ids = exercise.get('equipment', [])
        if equipment_ids and self._equipment_map:
            enhanced['equipment'] = [
                self._equipment_map.get(eq_id, f'Equipment {eq_id}')
                for eq_id in equipment_ids
            ]
        else:
            enhanced['equipment'] = []
        
        # Skip exercise info API for now since it's causing issues
        enhanced['instructions'] = []
        
        return enhanced
        
        # Resolve category ID to name
        category_id = exercise.get('category')
        enhanced['category'] = self._category_map.get(category_id, f'Category {category_id}')
        enhanced['category_name'] = enhanced['category']  # For compatibility
        
        # Resolve muscle IDs to names
        muscle_ids = exercise.get('muscles', [])
        enhanced['muscles'] = [
            self._muscle_map.get(muscle_id, f'Muscle {muscle_id}')
            for muscle_id in muscle_ids
        ]
        
        # Resolve secondary muscle IDs to names
        secondary_muscle_ids = exercise.get('muscles_secondary', [])
        enhanced['muscles_secondary'] = [
            self._muscle_map.get(muscle_id, f'Muscle {muscle_id}')
            for muscle_id in secondary_muscle_ids
        ]
        
        # Resolve equipment IDs to names
        equipment_ids = exercise.get('equipment', [])
        enhanced['equipment'] = [
            self._equipment_map.get(eq_id, f'Equipment {eq_id}')
            for eq_id in equipment_ids
        ]
        
        # Add instructions if available
        enhanced['instructions'] = exercise_info.get('instructions', [])
        
        return enhanced
    
    def get_exercise_categories(self) -> List[Dict]:
        """Get all exercise categories with public access"""
        print("🔍 Getting categories with public access...")
        
        # Use public access (remove auth temporarily)
        auth_header = self.session.headers.pop('Authorization', None)
        
        try:
            data = self._make_request("exercisecategory/", use_static_cache=True)
            categories = data.get('results', [])
            print(f"✅ Got {len(categories)} categories via public access")
            return categories
        finally:
            # Restore auth header
            if auth_header:
                self.session.headers['Authorization'] = auth_header
    
    def get_muscles(self) -> List[Dict]:
        """Get all muscle groups with public access"""
        print("🔍 Getting muscles with public access...")
        
        # Use public access (remove auth temporarily)
        auth_header = self.session.headers.pop('Authorization', None)
        
        try:
            data = self._make_request("muscle/", use_static_cache=True)
            muscles = data.get('results', [])
            print(f"✅ Got {len(muscles)} muscles via public access")
            return muscles
        finally:
            # Restore auth header
            if auth_header:
                self.session.headers['Authorization'] = auth_header
    
    def get_equipment(self) -> List[Dict]:
        """Get all equipment types with public access"""
        print("🔍 Getting equipment with public access...")
        
        # Use public access (remove auth temporarily)
        auth_header = self.session.headers.pop('Authorization', None)
        
        try:
            data = self._make_request("equipment/", use_static_cache=True)
            equipment = data.get('results', [])
            print(f"✅ Got {len(equipment)} equipment types via public access")
            return equipment
        finally:
            # Restore auth header
            if auth_header:
                self.session.headers['Authorization'] = auth_header
    
    def get_exercises(self, limit: int = 50, offset: int = 0, 
                     category: Optional[int] = None, 
                     muscle: Optional[int] = None,
                     equipment: Optional[int] = None,
                     language: int = 2,  # 2 = English
                     search: Optional[str] = None) -> Dict:
        """Get exercises with enhanced filtering options and ID resolution"""
        
        # Use simpler parameters that work with public access
        params = {
            'limit': limit,
            'offset': offset,
            'language': language,
            # Remove status parameter - might require special permissions
        }
        
        if category:
            params['category'] = category
        if muscle:
            params['muscles'] = muscle
        if equipment:
            params['equipment'] = equipment
        if search:
            params['search'] = search
            
        print(f"🔍 Getting exercises with params: {params}")
        
        # Try with public access (no auth) since exercise endpoint rejects our token
        print("🔍 Trying exercise endpoint with public access...")
        
        # Temporarily remove auth for exercise requests
        auth_header = self.session.headers.pop('Authorization', None)
        
        try:
            raw_data = self._make_request("exercise/", params)
            print(f"🔍 Public exercise request result: {bool(raw_data)}")
        finally:
            # Restore auth header for other endpoints
            if auth_header:
                self.session.headers['Authorization'] = auth_header
                print("🔍 Restored auth header for other endpoints")
        
        # Enhance each exercise with resolved IDs
        if raw_data and 'results' in raw_data:
            print(f"🔍 Got {len(raw_data['results'])} raw exercises, enhancing...")
            
            # DEBUG: Show first raw exercise to see what fields we actually have
            if raw_data['results']:
                first_exercise = raw_data['results'][0]
                print(f"🔍 Raw exercise fields: {list(first_exercise.keys())}")
                print(f"🔍 Raw exercise sample: {dict(list(first_exercise.items())[:8])}")
            
            enhanced_exercises = []
            
            for exercise in raw_data['results']:
                try:
                    enhanced_exercise = self._enhance_exercise_data(exercise)
                    enhanced_exercises.append(enhanced_exercise)
                        
                except Exception as e:
                    print(f"❌ Error enhancing exercise {exercise.get('id')}: {e}")
                    # Fallback to original data with basic formatting
                    enhanced_exercise = exercise.copy()
                    enhanced_exercise['name'] = exercise.get('name', f"Exercise #{exercise.get('id')}")
                    enhanced_exercise['description'] = exercise.get('description', 'No description available')
                    enhanced_exercise['category'] = 'Unknown'
                    enhanced_exercise['muscles'] = []
                    enhanced_exercise['equipment'] = []
                    enhanced_exercises.append(enhanced_exercise)
            
            raw_data['results'] = enhanced_exercises
            print(f"✅ Enhanced {len(enhanced_exercises)} exercises")
            
        return raw_data
    
    def get_exercise_details(self, exercise_id: int) -> Optional[WgerExercise]:
        """Get comprehensive details for a specific exercise"""
        exercise_data = self._make_request(f"exercise/{exercise_id}/")
        
        if not exercise_data:
            return None
        
        try:
            # Use the enhanced data method
            enhanced_exercise = self._enhance_exercise_data(exercise_data)
            
            return WgerExercise(
                id=enhanced_exercise.get('id'),
                name=enhanced_exercise.get('name'),
                description=enhanced_exercise.get('description'),
                category=enhanced_exercise.get('category'),
                muscles=enhanced_exercise.get('muscles', []),
                muscles_secondary=enhanced_exercise.get('muscles_secondary', []),
                equipment=enhanced_exercise.get('equipment', []),
                instructions=enhanced_exercise.get('instructions', []),
                variations=exercise_data.get('variations', []),
                license_author=exercise_data.get('license_author', ''),
                creation_date=exercise_data.get('creation_date', ''),
                uuid=exercise_data.get('uuid'),
                images=enhanced_exercise.get('images', [])
            )
        except Exception as e:
            self.logger.error(f"❌ Error creating WgerExercise object: {str(e)}")
            return None
    
    def _get_exercise_info(self, exercise_id: int) -> Dict:
        """Get exercise information including descriptions and instructions"""
        try:
            print(f"🔍 Getting exercise info for ID: {exercise_id}")
            
            # Try to get exercise info
            info_data = self._make_request(f"exerciseinfo/", {
                'exercise': exercise_id,
                'language': 2  # English
            })
            
            print(f"🔍 Exercise info raw response: {info_data}")
            
            if info_data and info_data.get('results'):
                info = info_data['results'][0]
                print(f"🔍 Exercise info first result: {info}")
                
                result = {
                    'name': info.get('name', ''),
                    'description': info.get('description', ''),
                    'instructions': [info.get('description', '')],  # Simplified
                    'images': []  # Could be enhanced to fetch actual images
                }
                print(f"🔍 Final exercise info result: {result}")
                return result
            else:
                print(f"⚠️ No exercise info found for {exercise_id}")
                return {
                    'name': '',
                    'description': 'No description available',
                    'instructions': [],
                    'images': []
                }
        except Exception as e:
            print(f"❌ Error getting exercise info for {exercise_id}: {e}")
            return {
                'name': '',
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
        
        # Enhance results with resolved IDs
        enhanced_results = []
        for exercise in results:
            try:
                enhanced_exercise = self._enhance_exercise_data(exercise)
                enhanced_results.append(enhanced_exercise)
            except Exception as e:
                self.logger.error(f"Error enhancing search result: {e}")
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
        """Get exercises particularly relevant for martial arts training - SIMPLIFIED VERSION"""
        print("🥋 Getting martial arts exercises (public access)...")
        
        try:
            # Just get general exercises using our enhanced method - much faster than multiple API calls
            exercises_data = self.get_exercises(limit=limit)
            exercises = exercises_data.get('results', [])
            
            if exercises:
                print(f"✅ Got {len(exercises)} general exercises for martial arts")
                return exercises
            else:
                print("⚠️ No exercises found, returning empty list")
                return []
                
        except Exception as e:
            print(f"❌ Error getting martial arts exercises: {e}")
            return []
    
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
            # Test basic connectivity first - try a simple endpoint without auth
            start_time = time.time()
            
            print("🔍 Testing WGER API connection...")
            
            # Test 1: Try public endpoint first
            try:
                print("🔍 Test 1: Trying public categories endpoint...")
                public_url = f"{self.base_url}/exercisecategory/"
                public_response = requests.get(public_url, timeout=10)
                print(f"🔍 Public endpoint status: {public_response.status_code}")
                
                if public_response.status_code == 200:
                    print("✅ Public endpoint works!")
                    categories_working = True
                else:
                    print(f"❌ Public endpoint failed: {public_response.status_code}")
                    categories_working = False
                    
            except Exception as e:
                print(f"❌ Public endpoint error: {e}")
                categories_working = False
            
            # Test 2: Try with authentication for categories
            try:
                print("🔍 Test 2: Trying authenticated categories endpoint...")
                auth_response = self.session.get(f"{self.base_url}/exercisecategory/", timeout=10)
                print(f"🔍 Auth endpoint status: {auth_response.status_code}")
                
                if auth_response.status_code == 200:
                    print("✅ Authenticated categories endpoint works!")
                    auth_categories_working = True
                elif auth_response.status_code == 403:
                    print("❌ Authentication failed for categories - API key issue")
                    print(f"❌ Headers sent: {dict(self.session.headers)}")
                    auth_categories_working = False
                else:
                    print(f"❌ Auth categories failed: {auth_response.status_code}")
                    auth_categories_working = False
                    
            except Exception as e:
                print(f"❌ Auth endpoint error: {e}")
                auth_categories_working = False
            
            # Test 3: Try exercises with PUBLIC access (no auth)
            try:
                print("🔍 Test 3: Trying exercises with PUBLIC access...")
                
                # Remove auth header temporarily
                auth_header = self.session.headers.pop('Authorization', None)
                
                exercise_response = requests.get(f"{self.base_url}/exercise/", 
                                               params={'limit': 5}, timeout=10)
                print(f"🔍 Public exercise endpoint status: {exercise_response.status_code}")
                
                # Restore auth header
                if auth_header:
                    self.session.headers['Authorization'] = auth_header
                
                if exercise_response.status_code == 200:
                    print("✅ Public exercise endpoint works!")
                    data = exercise_response.json()
                    exercises_count = len(data.get('results', []))
                    print(f"✅ Got {exercises_count} exercises")
                    exercises_working = True
                else:
                    print(f"❌ Public exercise endpoint failed: {exercise_response.status_code}")
                    print(f"❌ Response: {exercise_response.text[:200]}...")
                    exercises_working = False
                    
            except Exception as e:
                print(f"❌ Public exercise endpoint error: {e}")
                exercises_working = False
            
            response_time = time.time() - start_time
            
            # Determine overall success
            overall_success = categories_working and exercises_working
            
            if overall_success:
                message = "✅ WGER API connection successful (hybrid mode: public exercises, auth categories)"
            elif exercises_working:
                message = "⚠️ Partial success: exercises work with public access, categories may need auth"
            else:
                message = "❌ Connection failed: cannot access exercise data"
            
            return {
                'success': overall_success,
                'message': message,
                'response_time': round(response_time, 2),
                'api_stats': {
                    'categories_working': categories_working,
                    'auth_categories_working': auth_categories_working,
                    'exercises_working': exercises_working,
                    'access_mode': 'hybrid' if overall_success else 'failed'
                },
                'test_results': {
                    'categories_status': 'ok' if categories_working else 'failed',
                    'exercises_status': 'ok' if exercises_working else 'failed',
                    'auth_status': 'ok' if auth_categories_working else 'failed'
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
        # Clear lookup maps so they get refreshed
        self._muscle_map = None
        self._equipment_map = None
        self._category_map = None
        self.logger.info("API cache cleared")

# Fix: Create singleton instance with proper initialization
wger_service = WgerAPIService()