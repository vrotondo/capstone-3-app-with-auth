// Create this file as: frontend/src/services/aiService.js

// Use the same base URL pattern as your other services
const API_BASE_URL = 'http://localhost:8000/api';

class AIService {
    constructor() {
        this.baseURL = `${API_BASE_URL}/ai`;
    }

    // Helper method to get auth headers
    getAuthHeaders() {
        const token = localStorage.getItem('token');
        return {
            'Content-Type': 'application/json',
            'Authorization': token ? `Bearer ${token}` : '',
        };
    }

    // Helper method to handle API responses
    async handleResponse(response) {
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ message: 'Network error' }));
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }
        return response.json();
    }

    // Check if AI service is available and enabled
    async checkHealth() {
        try {
            const response = await fetch(`${this.baseURL}/health`, {
                method: 'GET',
                headers: this.getAuthHeaders(),
            });
            return await this.handleResponse(response);
        } catch (error) {
            console.error('AI health check failed:', error);
            return { ai_service_enabled: false, error: error.message };
        }
    }

    // Get AI-powered training insights
    async getInsights(options = {}) {
        try {
            const {
                timeframe = 'last_30_days',
                includeTechniques = true
            } = options;

            const params = new URLSearchParams({
                timeframe,
                include_techniques: includeTechniques.toString()
            });

            const response = await fetch(`${this.baseURL}/insights?${params}`, {
                method: 'GET',
                headers: this.getAuthHeaders(),
            });

            return await this.handleResponse(response);
        } catch (error) {
            console.error('Failed to get AI insights:', error);
            throw error;
        }
    }

    // Get AI-powered workout suggestions
    async getWorkoutSuggestions(preferences = {}) {
        try {
            const response = await fetch(`${this.baseURL}/workout-suggestions`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({ preferences }),
            });

            return await this.handleResponse(response);
        } catch (error) {
            console.error('Failed to get workout suggestions:', error);
            throw error;
        }
    }

    // Get AI analysis of technique progress
    async getTechniqueAnalysis() {
        try {
            const response = await fetch(`${this.baseURL}/technique-analysis`, {
                method: 'GET',
                headers: this.getAuthHeaders(),
            });

            return await this.handleResponse(response);
        } catch (error) {
            console.error('Failed to get technique analysis:', error);
            throw error;
        }
    }

    // Test the AI service
    async testService() {
        try {
            const response = await fetch(`${this.baseURL}/test`, {
                method: 'GET',
                headers: this.getAuthHeaders(),
            });

            return await this.handleResponse(response);
        } catch (error) {
            console.error('AI service test failed:', error);
            throw error;
        }
    }

    // Get AI service status
    async getStatus() {
        try {
            const response = await fetch(`${this.baseURL}/status`, {
                method: 'GET',
                headers: this.getAuthHeaders(),
            });

            return await this.handleResponse(response);
        } catch (error) {
            console.error('Failed to get AI status:', error);
            return {
                ai_enabled: false,
                error: error.message
            };
        }
    }

    // Format insights for display
    formatInsight(insight) {
        return {
            ...insight,
            icon: this.getInsightIcon(insight.type),
            confidenceLabel: this.getConfidenceLabel(insight.confidence),
            shortMessage: insight.message.length > 150
                ? insight.message.substring(0, 150) + '...'
                : insight.message
        };
    }

    // Get appropriate icon for insight type
    getInsightIcon(type) {
        const icons = {
            'pattern': '📊',
            'recommendation': '💡',
            'achievement': '🏆',
            'warning': '⚠️',
            'technique': '🥋',
            'general': '📝',
            'progress': '📈',
            'consistency': '🎯',
            'balance': '⚖️'
        };
        return icons[type] || '💭';
    }

    // Convert confidence score to human-readable label
    getConfidenceLabel(confidence) {
        if (confidence >= 0.8) return 'High Confidence';
        if (confidence >= 0.6) return 'Medium Confidence';
        if (confidence >= 0.4) return 'Low Confidence';
        return 'Very Low Confidence';
    }

    // Get color for insight type (for UI styling)
    getInsightColor(type) {
        const colors = {
            'pattern': '#3b82f6',
            'recommendation': '#f59e0b',
            'achievement': '#10b981',
            'warning': '#ef4444',
            'technique': '#8b5cf6',
            'general': '#6b7280',
            'progress': '#06b6d4',
            'consistency': '#84cc16',
            'balance': '#f97316'
        };
        return colors[type] || '#6b7280';
    }

    // Format timeframe for display
    getTimeframeName(timeframe) {
        const names = {
            'last_7_days': 'Last 7 Days',
            'last_30_days': 'Last 30 Days',
            'last_90_days': 'Last 90 Days',
            'last_6_months': 'Last 6 Months',
            'last_year': 'Last Year'
        };
        return names[timeframe] || 'Last 30 Days';
    }

    // Check if AI features should be shown
    async shouldShowAIFeatures() {
        try {
            const health = await this.checkHealth();
            return health.ai_service_enabled === true;
        } catch (error) {
            return false;
        }
    }
}

// Create and export a singleton instance
const aiService = new AIService();
export default aiService;

// Also export the class for testing purposes
export { AIService };