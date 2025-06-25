import api from './api';

const trainingService = {
    // Training Sessions

    // Get all training sessions
    getSessions: async (params = {}) => {
        const queryParams = new URLSearchParams();

        if (params.limit) queryParams.append('limit', params.limit);
        if (params.style) queryParams.append('style', params.style);
        if (params.from) queryParams.append('from', params.from);
        if (params.to) queryParams.append('to', params.to);

        const queryString = queryParams.toString();
        const url = queryString ? `/training/sessions?${queryString}` : '/training/sessions';

        const response = await api.get(url);
        return response.data;
    },

    // Get a specific training session
    getSession: async (sessionId) => {
        const response = await api.get(`/training/sessions/${sessionId}`);
        return response.data;
    },

    // Create a new training session
    createSession: async (sessionData) => {
        const response = await api.post('/training/sessions', sessionData);
        return response.data;
    },

    // Update a training session
    updateSession: async (sessionId, sessionData) => {
        const response = await api.put(`/training/sessions/${sessionId}`, sessionData);
        return response.data;
    },

    // Delete a training session
    deleteSession: async (sessionId) => {
        const response = await api.delete(`/training/sessions/${sessionId}`);
        return response.data;
    },

    // Techniques

    // Get all techniques
    getTechniques: async (params = {}) => {
        const queryParams = new URLSearchParams();

        if (params.style) queryParams.append('style', params.style);
        if (params.status) queryParams.append('status', params.status);

        const queryString = queryParams.toString();
        const url = queryString ? `/training/techniques?${queryString}` : '/training/techniques';

        const response = await api.get(url);
        return response.data;
    },

    // Create a new technique
    createTechnique: async (techniqueData) => {
        const response = await api.post('/training/techniques', techniqueData);
        return response.data;
    },

    // Update a technique
    updateTechnique: async (techniqueId, techniqueData) => {
        const response = await api.put(`/training/techniques/${techniqueId}`, techniqueData);
        return response.data;
    },

    // Delete a technique
    deleteTechnique: async (techniqueId) => {
        const response = await api.delete(`/training/techniques/${techniqueId}`);
        return response.data;
    },

    // Statistics and Analytics

    // Get training statistics
    getStats: async () => {
        const response = await api.get('/training/stats');
        return response.data;
    },

    // Get user's martial arts styles
    getStyles: async () => {
        const response = await api.get('/training/styles');
        return response.data;
    },

    // Utility functions

    // Format duration for display
    formatDuration: (minutes) => {
        if (minutes < 60) {
            return `${minutes} min`;
        }
        const hours = Math.floor(minutes / 60);
        const remainingMinutes = minutes % 60;
        return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
    },

    // Format date for API
    formatDateForAPI: (date) => {
        if (date instanceof Date) {
            return date.toISOString().split('T')[0]; // YYYY-MM-DD
        }
        return date;
    },

    // Parse API date
    parseDateFromAPI: (dateString) => {
        return new Date(dateString);
    },

    // Get intensity level label
    getIntensityLabel: (level) => {
        const labels = {
            1: 'Very Light',
            2: 'Light',
            3: 'Light-Moderate',
            4: 'Moderate',
            5: 'Moderate',
            6: 'Moderate-Hard',
            7: 'Hard',
            8: 'Hard',
            9: 'Very Hard',
            10: 'Maximum'
        };
        return labels[level] || 'Unknown';
    },

    // Get mastery status color
    getMasteryColor: (status) => {
        const colors = {
            'learning': '#f59e0b',    // yellow
            'practicing': '#3b82f6',  // blue
            'competent': '#10b981',   // green
            'mastery': '#8b5cf6'      // purple
        };
        return colors[status] || '#6b7280'; // gray
    },

    // Get mastery status label
    getMasteryLabel: (status) => {
        const labels = {
            'learning': 'Learning',
            'practicing': 'Practicing',
            'competent': 'Competent',
            'mastery': 'Mastery'
        };
        return labels[status] || 'Unknown';
    },

    // Validate session data
    validateSessionData: (data) => {
        const errors = {};

        if (!data.duration || data.duration <= 0) {
            errors.duration = 'Duration must be a positive number';
        }

        if (!data.style || data.style.trim() === '') {
            errors.style = 'Style is required';
        }

        if (data.intensity_level && (data.intensity_level < 1 || data.intensity_level > 10)) {
            errors.intensity_level = 'Intensity level must be between 1 and 10';
        }

        if (data.energy_before && (data.energy_before < 1 || data.energy_before > 10)) {
            errors.energy_before = 'Energy before must be between 1 and 10';
        }

        if (data.energy_after && (data.energy_after < 1 || data.energy_after > 10)) {
            errors.energy_after = 'Energy after must be between 1 and 10';
        }

        return {
            isValid: Object.keys(errors).length === 0,
            errors
        };
    },

    // Validate technique data
    validateTechniqueData: (data) => {
        const errors = {};

        if (!data.technique_name || data.technique_name.trim() === '') {
            errors.technique_name = 'Technique name is required';
        }

        if (!data.style || data.style.trim() === '') {
            errors.style = 'Style is required';
        }

        if (data.proficiency_level && (data.proficiency_level < 1 || data.proficiency_level > 10)) {
            errors.proficiency_level = 'Proficiency level must be between 1 and 10';
        }

        return {
            isValid: Object.keys(errors).length === 0,
            errors
        };
    }
};

export default trainingService;