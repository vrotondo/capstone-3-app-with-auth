import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

class WgerService {
    constructor() {
        this.api = axios.create({
            baseURL: `${API_BASE_URL}/wger`,
            timeout: 15000, // Increased timeout
        });

        // Add auth interceptor with wger API key
        this.api.interceptors.request.use((config) => {
            const token = localStorage.getItem('token');
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }

            // Add wger API key if available
            const wgerApiKey = import.meta.env.VITE_WGER_API_KEY;
            if (wgerApiKey) {
                config.headers['X-WGER-API-KEY'] = wgerApiKey;
                console.log('🔑 Using wger API key');
            } else {
                console.log('⚠️ No wger API key found');
            }

            return config;
        });

        // Enhanced response interceptor
        this.api.interceptors.response.use(
            (response) => {
                console.log('✅ wger API Response:', response.config.url, response.status);
                return response;
            },
            (error) => {
                console.error('❌ wger API Error:', error.config?.url, error.message);
                return Promise.reject(error);
            }
        );
    }

    // Test connection to wger API
    async testConnection() {
        try {
            const response = await this.api.get('/test');
            console.log('🔍 wger Connection Test:', response.data);
            return response.data;
        } catch (error) {
            console.error('❌ wger Connection Test Failed:', error);
            throw new Error(`Connection test failed: ${error.message}`);
        }
    }

    // Get exercise categories
    async getCategories() {
        try {
            console.log('📂 Fetching exercise categories...');
            const response = await this.api.get('/categories');
            console.log('✅ Categories fetched:', response.data.count || 0);
            return response.data;
        } catch (error) {
            console.error('❌ Error fetching categories:', error);
            return { success: false, categories: [] };
        }
    }

    // Get muscle groups
    async getMuscles() {
        try {
            console.log('💪 Fetching muscle groups...');
            const response = await this.api.get('/muscles');
            console.log('✅ Muscles fetched:', response.data.count || 0);
            return response.data;
        } catch (error) {
            console.error('❌ Error fetching muscles:', error);
            return { success: false, muscles: [] };
        }
    }

    // Get equipment types
    async getEquipment() {
        try {
            console.log('🏋️ Fetching equipment types...');
            const response = await this.api.get('/equipment');
            console.log('✅ Equipment fetched:', response.data.count || 0);
            return response.data;
        } catch (error) {
            console.error('❌ Error fetching equipment:', error);
            return { success: false, equipment: [] };
        }
    }

    // Get exercises with enhanced filtering and better data
    async getExercises(params = {}) {
        try {
            console.log('🏃 Fetching exercises with params:', params);

            // Add default parameters for better results
            const defaultParams = {
                limit: 50,
                status: 2, // Only approved exercises
                ...params
            };

            const response = await this.api.get('/exercises', { params: defaultParams });
            console.log('✅ Exercises fetched:', response.data.count || 0);

            // Enhance exercises with better formatting
            if (response.data.success && response.data.exercises) {
                response.data.exercises = response.data.exercises.map(exercise =>
                    this.formatExerciseForDisplay(exercise)
                );
            }

            return response.data;
        } catch (error) {
            console.error('❌ Error fetching exercises:', error);
            return { success: false, exercises: [] };
        }
    }

    // Get exercise detail with full information
    async getExerciseDetail(exerciseId) {
        try {
            console.log(`🔍 Fetching exercise detail for ID: ${exerciseId}`);
            const response = await this.api.get(`/exercises/${exerciseId}`);
            console.log('✅ Exercise detail fetched:', response.data.success);
            return response.data;
        } catch (error) {
            console.error('❌ Error fetching exercise detail:', error);
            return { success: false, exercise: null };
        }
    }

    // Enhanced search with better results
    async searchExercises(query, limit = 20) {
        try {
            console.log(`🔍 Searching exercises for: "${query}"`);
            const response = await this.api.get('/exercises/search', {
                params: { q: query, limit }
            });
            console.log('✅ Search results:', response.data.count || 0);

            // Enhance search results
            if (response.data.success && response.data.exercises) {
                response.data.exercises = response.data.exercises.map(exercise =>
                    this.formatExerciseForDisplay(exercise)
                );
            }

            return response.data;
        } catch (error) {
            console.error('❌ Error searching exercises:', error);
            return { success: false, exercises: [] };
        }
    }

    // Get martial arts specific exercises with better formatting
    async getMartialArtsExercises(limit = 100) {
        try {
            console.log('🥋 Fetching martial arts exercises...');
            const response = await this.api.get('/exercises/martial-arts', {
                params: { limit }
            });
            console.log('✅ Martial arts exercises fetched:', response.data.count || 0);

            // Enhance martial arts exercises
            if (response.data.success && response.data.exercises) {
                response.data.exercises = response.data.exercises.map(exercise =>
                    this.formatExerciseForDisplay(exercise)
                );
            }

            return response.data;
        } catch (error) {
            console.error('❌ Error fetching martial arts exercises:', error);
            return { success: false, exercises: [] };
        }
    }

    // Get exercises by category
    async getExercisesByCategory(categoryName, limit = 50) {
        try {
            console.log(`📂 Fetching exercises for category: ${categoryName}`);
            const response = await this.api.get(`/exercises/by-category/${categoryName}`, {
                params: { limit }
            });
            console.log('✅ Category exercises fetched:', response.data.count || 0);
            return response.data;
        } catch (error) {
            console.error('❌ Error fetching exercises by category:', error);
            return { success: false, exercises: [] };
        }
    }

    // Get exercises by muscle
    async getExercisesByMuscle(muscleName, limit = 30) {
        try {
            console.log(`💪 Fetching exercises for muscle: ${muscleName}`);
            const response = await this.api.get(`/exercises/by-muscle/${muscleName}`, {
                params: { limit }
            });
            console.log('✅ Muscle exercises fetched:', response.data.count || 0);
            return response.data;
        } catch (error) {
            console.error('❌ Error fetching exercises by muscle:', error);
            return { success: false, exercises: [] };
        }
    }

    // Get exercises by equipment
    async getExercisesByEquipment(equipmentName, limit = 30) {
        try {
            console.log(`🏋️ Fetching exercises for equipment: ${equipmentName}`);
            const response = await this.api.get(`/exercises/by-equipment/${equipmentName}`, {
                params: { limit }
            });
            console.log('✅ Equipment exercises fetched:', response.data.count || 0);
            return response.data;
        } catch (error) {
            console.error('❌ Error fetching exercises by equipment:', error);
            return { success: false, exercises: [] };
        }
    }

    // Get API statistics
    async getStats() {
        try {
            console.log('📊 Fetching API stats...');
            const response = await this.api.get('/stats');
            console.log('✅ Stats fetched successfully');
            return response.data;
        } catch (error) {
            console.error('❌ Error fetching API stats:', error);
            return { success: false, stats: {} };
        }
    }

    // Enhanced exercise formatting for better display
    formatExerciseForDisplay(exercise) {
        // Try to get the exercise name from various possible fields
        let name = exercise.name ||
            exercise.exercise_name ||
            exercise.title ||
            `Exercise #${exercise.id}`;

        // Clean up the name
        if (name && name !== `Exercise #${exercise.id}`) {
            name = name.charAt(0).toUpperCase() + name.slice(1);
        }

        // Get description from various possible fields
        let description = exercise.description ||
            exercise.instructions ||
            exercise.exercise_description ||
            'No description available';

        // If description is an array, join it
        if (Array.isArray(description)) {
            description = description.join(' ');
        }

        // Clean up description
        if (description && description.length > 200) {
            description = description.substring(0, 200) + '...';
        }

        // Format category
        let category = exercise.category_name ||
            exercise.category ||
            (exercise.category_id ? `Category ${exercise.category_id}` : 'Unknown');

        return {
            id: exercise.id,
            name: name,
            description: description,
            category: category,
            muscles: Array.isArray(exercise.muscles) ? exercise.muscles : [],
            muscles_secondary: Array.isArray(exercise.muscles_secondary) ? exercise.muscles_secondary : [],
            equipment: Array.isArray(exercise.equipment) ? exercise.equipment : [],
            uuid: exercise.uuid,
            category_id: exercise.category || exercise.category_id,
            difficulty: this.getExerciseDifficulty(exercise),
            categoryIcon: this.getCategoryIcon(category)
        };
    }

    // Enhanced difficulty calculation
    getExerciseDifficulty(exercise) {
        const equipmentCount = (exercise.equipment?.length || 0);
        const muscleCount = (exercise.muscles?.length || 0) + (exercise.muscles_secondary?.length || 0);

        // Simple heuristic based on complexity
        if (equipmentCount === 0 && muscleCount <= 1) {
            return 'Beginner';
        } else if (equipmentCount <= 1 && muscleCount <= 3) {
            return 'Intermediate';
        } else {
            return 'Advanced';
        }
    }

    // Enhanced category icons
    getCategoryIcon(categoryName) {
        const iconMap = {
            'Abs': '🏋️',
            'Arms': '💪',
            'Back': '🏃',
            'Calves': '🦵',
            'Cardio': '❤️',
            'Chest': '💯',
            'Legs': '🦵',
            'Shoulders': '🏋️',
            'Stretching': '🧘',
            'Plyometrics': '⚡',
            'Strength': '💪',
            'Unknown': '🏋️'
        };

        return iconMap[categoryName] || '🏋️';
    }

    // User favorites (requires authentication)
    async getUserFavorites() {
        try {
            const response = await this.api.get('/user/favorites');
            return response.data;
        } catch (error) {
            console.error('❌ Error fetching user favorites:', error);
            return { success: false, favorites: [] };
        }
    }

    async addToFavorites(exerciseId) {
        try {
            const response = await this.api.post('/user/favorites', {
                exercise_id: exerciseId
            });
            return response.data;
        } catch (error) {
            console.error('❌ Error adding to favorites:', error);
            return { success: false, error: error.message };
        }
    }

    async removeFromFavorites(exerciseId) {
        try {
            const response = await this.api.delete('/user/favorites', {
                params: { exercise_id: exerciseId }
            });
            return response.data;
        } catch (error) {
            console.error('❌ Error removing from favorites:', error);
            return { success: false, error: error.message };
        }
    }

    // Workout plans
    async getUserWorkoutPlans() {
        try {
            const response = await this.api.get('/user/workout-plans');
            return response.data;
        } catch (error) {
            console.error('❌ Error fetching workout plans:', error);
            return { success: false, workout_plans: [] };
        }
    }

    async createWorkoutPlan(name, exerciseIds) {
        try {
            const response = await this.api.post('/user/workout-plans', {
                name,
                exercise_ids: exerciseIds
            });
            return response.data;
        } catch (error) {
            console.error('❌ Error creating workout plan:', error);
            return { success: false, error: error.message };
        }
    }

    // Clear cache (admin function)
    async clearCache() {
        try {
            const response = await this.api.post('/cache/clear');
            return response.data;
        } catch (error) {
            console.error('❌ Error clearing cache:', error);
            return { success: false, error: error.message };
        }
    }
}

// Create and export singleton instance
const wgerService = new WgerService();
export default wgerService;