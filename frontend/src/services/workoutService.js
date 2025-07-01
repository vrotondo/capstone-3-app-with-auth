import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

class WorkoutService {
    constructor() {
        this.api = axios.create({
            baseURL: `${API_BASE_URL}/workout`,
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
                console.error('Workout API Error:', error.response?.data || error.message);
                return Promise.reject(error);
            }
        );
    }

    // ==================== FAVORITES ====================

    async getFavorites() {
        try {
            const response = await this.api.get('/favorites');
            return response.data;
        } catch (error) {
            return { success: false, error: error.message, favorites: [] };
        }
    }

    async addToFavorites(exercise) {
        try {
            const response = await this.api.post('/favorites', {
                exercise_id: exercise.id,
                exercise_name: exercise.displayName || exercise.name,
                exercise_category: exercise.category,
                exercise_muscles: exercise.muscles || [],
                exercise_equipment: exercise.equipment || []
            });
            return response.data;
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    async removeFromFavorites(exerciseId) {
        try {
            const response = await this.api.delete(`/favorites/${exerciseId}`);
            return response.data;
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    async checkFavoriteStatus(exerciseId) {
        try {
            const response = await this.api.get(`/favorites/check/${exerciseId}`);
            return response.data;
        } catch (error) {
            return { success: false, is_favorited: false };
        }
    }

    // ==================== WORKOUT PLANS ====================

    async getWorkoutPlans() {
        try {
            const response = await this.api.get('/plans');
            return response.data;
        } catch (error) {
            return { success: false, error: error.message, workout_plans: [] };
        }
    }

    async createWorkoutPlan(name, description = '') {
        try {
            const response = await this.api.post('/plans', {
                name,
                description
            });
            return response.data;
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    async getWorkoutPlan(planId) {
        try {
            const response = await this.api.get(`/plans/${planId}`);
            return response.data;
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    async updateWorkoutPlan(planId, name, description) {
        try {
            const response = await this.api.put(`/plans/${planId}`, {
                name,
                description
            });
            return response.data;
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    async deleteWorkoutPlan(planId) {
        try {
            const response = await this.api.delete(`/plans/${planId}`);
            return response.data;
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    // ==================== WORKOUT EXERCISES ====================

    async addExerciseToWorkout(planId, exercise, workoutDetails = {}) {
        try {
            const response = await this.api.post(`/plans/${planId}/exercises`, {
                exercise_id: exercise.id,
                exercise_name: exercise.displayName || exercise.name,
                exercise_category: exercise.category,
                exercise_muscles: exercise.muscles || [],
                exercise_equipment: exercise.equipment || [],
                sets: workoutDetails.sets || 3,
                reps: workoutDetails.reps || '10-12',
                rest_seconds: workoutDetails.rest_seconds || 60,
                notes: workoutDetails.notes || ''
            });
            return response.data;
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    async removeExerciseFromWorkout(planId, exerciseId) {
        try {
            const response = await this.api.delete(`/plans/${planId}/exercises/${exerciseId}`);
            return response.data;
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    // ==================== BULK OPERATIONS ====================

    async addMultipleExercisesToWorkout(planId, exercises) {
        const results = [];
        for (const exercise of exercises) {
            const result = await this.addExerciseToWorkout(planId, exercise);
            results.push(result);
        }
        return results;
    }

    async getFavoritesForExerciseIds(exerciseIds) {
        try {
            // Get all favorites and check which exercise IDs are in there
            const favoritesResponse = await this.getFavorites();
            if (!favoritesResponse.success) {
                return {};
            }

            const favoriteMap = {};
            favoritesResponse.favorites.forEach(fav => {
                favoriteMap[fav.exercise_id] = true;
            });

            return favoriteMap;
        } catch (error) {
            console.error('Error getting favorite status:', error);
            return {};
        }
    }
}

// Create and export singleton instance
const workoutService = new WorkoutService();
export default workoutService;