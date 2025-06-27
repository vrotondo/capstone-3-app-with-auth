import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

class WgerService {
    constructor() {
        this.api = axios.create({
            baseURL: `${API_BASE_URL}/wger`,
            timeout: 10000,
        });

        // Add auth interceptor
        this.api.interceptors.request.use((config) => {
            const token = localStorage.getItem('token');
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
            return config;
        });

        // Response interceptor for error handling
        this.api.interceptors.response.use(
            (response) => response,
            (error) => {
                console.error('wger API Error:', error);
                return Promise.reject(error);
            }
        );
    }

    // Test connection to wger API
    async testConnection() {
        try {
            const response = await this.api.get('/test');
            return response.data;
        } catch (error) {
            throw new Error(`Connection test failed: ${error.message}`);
        }
    }

    // Get exercise categories
    async getCategories() {
        try {
            const response = await this.api.get('/categories');
            return response.data;
        } catch (error) {
            console.error('Error fetching categories:', error);
            return { success: false, categories: [] };
        }
    }

    // Get muscle groups
    async getMuscles() {
        try {
            const response = await this.api.get('/muscles');
            return response.data;
        } catch (error) {
            console.error('Error fetching muscles:', error);
            return { success: false, muscles: [] };
        }
    }

    // Get equipment types
    async getEquipment() {
        try {
            const response = await this.api.get('/equipment');
            return response.data;
        } catch (error) {
            console.error('Error fetching equipment:', error);
            return { success: false, equipment: [] };
        }
    }

    // Get exercises with filtering
    async getExercises(params = {}) {
        try {
            const response = await this.api.get('/exercises', { params });
            return response.data;
        } catch (error) {
            console.error('Error fetching exercises:', error);
            return { success: false, exercises: [] };
        }
    }

    // Get exercise detail
    async getExerciseDetail(exerciseId) {
        try {
            const response = await this.api.get(`/exercises/${exerciseId}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching exercise detail:', error);
            return { success: false, exercise: null };
        }
    }

    // Search exercises
    async searchExercises(query, limit = 20) {
        try {
            const response = await this.api.get('/exercises/search', {
                params: { q: query, limit }
            });
            return response.data;
        } catch (error) {
            console.error('Error searching exercises:', error);
            return { success: false, exercises: [] };
        }
    }

    // Get martial arts specific exercises
    async getMartialArtsExercises(limit = 100) {
        try {
            const response = await this.api.get('/exercises/martial-arts', {
                params: { limit }
            });
            return response.data;
        } catch (error) {
            console.error('Error fetching martial arts exercises:', error);
            return { success: false, exercises: [] };
        }
    }

    // Get exercises by category
    async getExercisesByCategory(categoryName, limit = 50) {
        try {
            const response = await this.api.get(`/exercises/by-category/${categoryName}`, {
                params: { limit }
            });
            return response.data;
        } catch (error) {
            console.error('Error fetching exercises by category:', error);
            return { success: false, exercises: [] };
        }
    }

    // Get exercises by muscle
    async getExercisesByMuscle(muscleName, limit = 30) {
        try {
            const response = await this.api.get(`/exercises/by-muscle/${muscleName}`, {
                params: { limit }
            });
            return response.data;
        } catch (error) {
            console.error('Error fetching exercises by muscle:', error);
            return { success: false, exercises: [] };
        }
    }

    // Get exercises by equipment
    async getExercisesByEquipment(equipmentName, limit = 30) {
        try {
            const response = await this.api.get(`/exercises/by-equipment/${equipmentName}`, {
                params: { limit }
            });
            return response.data;
        } catch (error) {
            console.error('Error fetching exercises by equipment:', error);
            return { success: false, exercises: [] };
        }
    }

    // Get API statistics
    async getStats() {
        try {
            const response = await this.api.get('/stats');
            return response.data;
        } catch (error) {
            console.error('Error fetching API stats:', error);
            return { success: false, stats: {} };
        }
    }

    // User favorites (requires authentication)
    async getUserFavorites() {
        try {
            const response = await this.api.get('/user/favorites');
            return response.data;
        } catch (error) {
            console.error('Error fetching user favorites:', error);
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
            console.error('Error adding to favorites:', error);
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
            console.error('Error removing from favorites:', error);
            return { success: false, error: error.message };
        }
    }

    // Workout plans
    async getUserWorkoutPlans() {
        try {
            const response = await this.api.get('/user/workout-plans');
            return response.data;
        } catch (error) {
            console.error('Error fetching workout plans:', error);
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
            console.error('Error creating workout plan:', error);
            return { success: false, error: error.message };
        }
    }

    // Clear cache (admin function)
    async clearCache() {
        try {
            const response = await this.api.post('/cache/clear');
            return response.data;
        } catch (error) {
            console.error('Error clearing cache:', error);
            return { success: false, error: error.message };
        }
    }

    // Utility functions for frontend
    formatExerciseForDisplay(exercise) {
        return {
            id: exercise.id,
            name: exercise.name || `Exercise #${exercise.id}`,
            description: exercise.description || 'No description available',
            category: exercise.category_name || exercise.category || 'Unknown',
            muscles: Array.isArray(exercise.muscles) ? exercise.muscles : [],
            equipment: Array.isArray(exercise.equipment) ? exercise.equipment : [],
            uuid: exercise.uuid
        };
    }

    getExerciseDifficulty(exercise) {
        // Simple difficulty estimation based on equipment and muscle groups
        const equipmentCount = exercise.equipment?.length || 0;
        const muscleCount = (exercise.muscles?.length || 0) + (exercise.muscles_secondary?.length || 0);

        if (equipmentCount === 0 && muscleCount <= 2) return 'Beginner';
        if (equipmentCount <= 1 && muscleCount <= 4) return 'Intermediate';
        return 'Advanced';
    }

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
            'Plyometrics': '⚡'
        };

        return iconMap[categoryName] || '🏋️';
    }

    // Pagination helper
    async getAllExercises(maxPages = 5) {
        const allExercises = [];
        let offset = 0;
        const limit = 100;

        for (let page = 0; page < maxPages; page++) {
            const response = await this.getExercises({ limit, offset });

            if (!response.success || !response.exercises?.length) {
                break;
            }

            allExercises.push(...response.exercises);

            if (!response.next) {
                break; // No more pages
            }

            offset += limit;
        }

        return allExercises;
    }
}

// Create and export singleton instance
const wgerService = new WgerService();
export default wgerService;