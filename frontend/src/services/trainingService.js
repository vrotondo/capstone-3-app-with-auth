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

    // Video Management

    // Get all videos for the current user
    getVideos: async (params = {}) => {
        const queryParams = new URLSearchParams();

        if (params.limit) queryParams.append('limit', params.limit);
        if (params.technique_name) queryParams.append('technique_name', params.technique_name);
        if (params.style) queryParams.append('style', params.style);
        if (params.analysis_status) queryParams.append('analysis_status', params.analysis_status);

        const queryString = queryParams.toString();
        const url = queryString ? `/training/videos/list?${queryString}` : '/training/videos/list';

        const response = await api.get(url);
        return response.data;
    },

    // Get a specific video
    getVideo: async (videoId) => {
        const response = await api.get(`/training/videos/${videoId}/details`);
        return response.data;
    },

    // Upload a training video
    uploadVideo: async (videoFile, metadata = {}, onProgress = null) => {
        const formData = new FormData();
        formData.append('video', videoFile);

        // Add metadata
        if (metadata.title) formData.append('title', metadata.title);
        if (metadata.description) formData.append('description', metadata.description);
        if (metadata.technique_name) formData.append('technique_name', metadata.technique_name);
        if (metadata.style) formData.append('style', metadata.style);
        if (metadata.is_private !== undefined) formData.append('is_private', metadata.is_private.toString());
        if (metadata.tags) formData.append('tags', Array.isArray(metadata.tags) ? metadata.tags.join(',') : metadata.tags);

        const config = {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        };

        // Add progress tracking if callback provided
        if (onProgress) {
            config.onUploadProgress = (progressEvent) => {
                const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                onProgress(percentCompleted);
            };
        }

        const response = await api.post('/training/videos/upload', formData, config);
        return response.data;
    },

    // Update video metadata
    updateVideo: async (videoId, videoData) => {
        const response = await api.put(`/training/videos/${videoId}/update`, videoData);
        return response.data;
    },

    // Delete a video
    deleteVideo: async (videoId) => {
        const response = await api.delete(`/training/videos/${videoId}/delete`);
        return response.data;
    },

    // Get video statistics
    getVideoStats: async () => {
        const response = await api.get('/training/videos/stats');
        return response.data;
    },

    // Get video file URL for playback - WITH AUTHENTICATION
    getVideoFileUrl: (videoId) => {
        const token = localStorage.getItem('token');
        return `http://localhost:8000/api/training/videos/${videoId}/stream?token=${token}`;
    },

    // Get video download URL - WITH AUTHENTICATION
    getVideoDownloadUrl: (videoId) => {
        const token = localStorage.getItem('token');
        return `http://localhost:8000/api/training/videos/${videoId}/stream?download=true&token=${token}`;
    },

    // Video utility functions

    // Validate video file
    validateVideoFile: (file) => {
        const errors = [];

        // Check file type
        const allowedTypes = ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska', 'video/x-ms-wmv', 'video/x-flv', 'video/webm'];
        const allowedExtensions = ['mp4', 'mov', 'avi', 'mkv', 'wmv', 'flv', 'webm', 'm4v'];

        if (!allowedTypes.includes(file.type)) {
            const extension = file.name.split('.').pop().toLowerCase();
            if (!allowedExtensions.includes(extension)) {
                errors.push(`Invalid file type. Allowed formats: ${allowedExtensions.join(', ')}`);
            }
        }

        // Check file size (500MB limit)
        const maxSize = 500 * 1024 * 1024; // 500MB
        if (file.size > maxSize) {
            errors.push(`File too large. Maximum size is ${Math.round(maxSize / (1024 * 1024))}MB`);
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    },

    // Format file size for display
    formatFileSize: (bytes) => {
        if (bytes === 0) return '0 Bytes';

        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));

        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    // Format video duration for display
    formatVideoDuration: (seconds) => {
        if (!seconds) return '0:00';

        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);

        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    },

    // Get video analysis status label
    getAnalysisStatusLabel: (status) => {
        const labels = {
            'pending': 'Pending Analysis',
            'processing': 'Analyzing...',
            'completed': 'Analysis Complete',
            'failed': 'Analysis Failed'
        };
        return labels[status] || 'Unknown';
    },

    // Get video analysis status color
    getAnalysisStatusColor: (status) => {
        const colors = {
            'pending': '#f59e0b',      // yellow
            'processing': '#3b82f6',   // blue
            'completed': '#10b981',    // green
            'failed': '#ef4444'        // red
        };
        return colors[status] || '#6b7280'; // gray
    },

    // Get video upload status label
    getUploadStatusLabel: (status) => {
        const labels = {
            'uploaded': 'Uploaded',
            'processing': 'Processing...',
            'analyzed': 'Analyzed',
            'error': 'Upload Error'
        };
        return labels[status] || 'Unknown';
    },

    // Validate video metadata
    validateVideoMetadata: (metadata) => {
        const errors = {};

        if (metadata.title && metadata.title.length > 200) {
            errors.title = 'Title must be less than 200 characters';
        }

        if (metadata.description && metadata.description.length > 1000) {
            errors.description = 'Description must be less than 1000 characters';
        }

        if (metadata.technique_name && metadata.technique_name.length > 100) {
            errors.technique_name = 'Technique name must be less than 100 characters';
        }

        if (metadata.style && metadata.style.length > 50) {
            errors.style = 'Style must be less than 50 characters';
        }

        return {
            isValid: Object.keys(errors).length === 0,
            errors
        };
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