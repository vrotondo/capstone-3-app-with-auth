// Technique Service - Frontend API calls for technique library

const API_BASE = '/api/techniques';

class TechniqueService {
    // Get auth headers if user is logged in
    getAuthHeaders() {
        const token = localStorage.getItem('token');
        return token ? { 'Authorization': `Bearer ${token}` } : {};
    }

    // Search techniques
    async searchTechniques(params = {}) {
        const searchParams = new URLSearchParams();

        Object.entries(params).forEach(([key, value]) => {
            if (value !== undefined && value !== null && value !== '') {
                if (Array.isArray(value)) {
                    value.forEach(v => searchParams.append(key, v));
                } else {
                    searchParams.append(key, value);
                }
            }
        });

        const response = await fetch(`${API_BASE}/search?${searchParams}`, {
            headers: {
                'Content-Type': 'application/json',
                ...this.getAuthHeaders()
            }
        });

        if (!response.ok) {
            throw new Error('Failed to search techniques');
        }

        return response.json();
    }

    // Get technique by ID
    async getTechnique(id) {
        const response = await fetch(`${API_BASE}/${id}`, {
            headers: {
                'Content-Type': 'application/json',
                ...this.getAuthHeaders()
            }
        });

        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('Technique not found');
            }
            throw new Error('Failed to load technique');
        }

        return response.json();
    }

    // Get popular techniques
    async getPopularTechniques(limit = 10) {
        const response = await fetch(`${API_BASE}/popular?limit=${limit}`, {
            headers: {
                'Content-Type': 'application/json',
                ...this.getAuthHeaders()
            }
        });

        if (!response.ok) {
            throw new Error('Failed to load popular techniques');
        }

        return response.json();
    }

    // Get available styles
    async getStyles() {
        const response = await fetch(`${API_BASE}/styles`, {
            headers: {
                'Content-Type': 'application/json',
                ...this.getAuthHeaders()
            }
        });

        if (!response.ok) {
            throw new Error('Failed to load styles');
        }

        return response.json();
    }

    // Get available categories
    async getCategories() {
        const response = await fetch(`${API_BASE}/categories`, {
            headers: {
                'Content-Type': 'application/json',
                ...this.getAuthHeaders()
            }
        });

        if (!response.ok) {
            throw new Error('Failed to load categories');
        }

        return response.json();
    }

    // Get technique library stats
    async getStats() {
        const response = await fetch(`${API_BASE}/stats`, {
            headers: {
                'Content-Type': 'application/json',
                ...this.getAuthHeaders()
            }
        });

        if (!response.ok) {
            throw new Error('Failed to load stats');
        }

        return response.json();
    }

    // === Authenticated Methods ===

    // Get user's bookmarked techniques
    async getUserBookmarks(limit = 50) {
        const token = localStorage.getItem('token');
        if (!token) {
            throw new Error('Authentication required');
        }

        const response = await fetch(`${API_BASE}/bookmarks?limit=${limit}`, {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to load bookmarks');
        }

        return response.json();
    }

    // Bookmark a technique
    async bookmarkTechnique(techniqueId, notes = '') {
        const token = localStorage.getItem('token');
        if (!token) {
            throw new Error('Authentication required');
        }

        const response = await fetch(`${API_BASE}/${techniqueId}/bookmark`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ notes })
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.message || 'Failed to bookmark technique');
        }

        return response.json();
    }

    // Remove bookmark
    async removeBookmark(techniqueId) {
        const token = localStorage.getItem('token');
        if (!token) {
            throw new Error('Authentication required');
        }

        const response = await fetch(`${API_BASE}/${techniqueId}/bookmark`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.message || 'Failed to remove bookmark');
        }

        return response.json();
    }

    // Update technique progress
    async updateProgress(techniqueId, data) {
        const token = localStorage.getItem('token');
        if (!token) {
            throw new Error('Authentication required');
        }

        const response = await fetch(`${API_BASE}/${techniqueId}/progress`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const responseData = await response.json();
            throw new Error(responseData.message || 'Failed to update progress');
        }

        return response.json();
    }

    // === Admin Methods ===

    // Import techniques from external source
    async importTechniques(source, maxTechniques = 10) {
        const token = localStorage.getItem('token');
        if (!token) {
            throw new Error('Authentication required');
        }

        const response = await fetch(`${API_BASE}/import`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                source,
                max_techniques: maxTechniques
            })
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.message || 'Failed to import techniques');
        }

        return response.json();
    }

    // === Utility Methods ===

    // Get difficulty color class
    getDifficultyColor(level) {
        if (!level) return 'bg-gray-500';
        if (level <= 3) return 'bg-green-500';
        if (level <= 6) return 'bg-yellow-500';
        return 'bg-red-500';
    }

    // Get difficulty text
    getDifficultyText(level) {
        if (!level) return 'Unknown';
        if (level <= 3) return 'Beginner';
        if (level <= 6) return 'Intermediate';
        return 'Advanced';
    }

    // Get mastery level text
    getMasteryText(level) {
        if (level <= 2) return 'Learning';
        if (level <= 4) return 'Practicing';
        if (level <= 7) return 'Improving';
        return 'Mastered';
    }

    // Get mastery level color
    getMasteryColor(level) {
        if (level <= 2) return 'text-red-600';
        if (level <= 4) return 'text-yellow-600';
        if (level <= 7) return 'text-blue-600';
        return 'text-green-600';
    }

    // Format technique tags for display
    formatTags(tags) {
        if (!Array.isArray(tags)) return [];
        return tags.map(tag => tag.charAt(0).toUpperCase() + tag.slice(1));
    }

    // Check if user is authenticated
    isAuthenticated() {
        return !!localStorage.getItem('token');
    }

    // Validate mastery level
    validateMasteryLevel(level) {
        const num = parseInt(level);
        return num >= 1 && num <= 10 ? num : 1;
    }

    // Format date for display
    formatDate(dateString) {
        if (!dateString) return 'Never';

        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        } catch (error) {
            return 'Invalid date';
        }
    }

    // Truncate text for display
    truncateText(text, maxLength = 150) {
        if (!text || text.length <= maxLength) return text;
        return text.substring(0, maxLength).trim() + '...';
    }

    // Generate technique URL
    getTechniqueUrl(techniqueId) {
        return `/techniques/${techniqueId}`;
    }

    // Search suggestions based on current techniques
    getSearchSuggestions(techniques, query) {
        if (!query || query.length < 2) return [];

        const suggestions = new Set();
        const queryLower = query.toLowerCase();

        techniques.forEach(technique => {
            // Add technique name if it matches
            if (technique.name.toLowerCase().includes(queryLower)) {
                suggestions.add(technique.name);
            }

            // Add style if it matches
            if (technique.style && technique.style.toLowerCase().includes(queryLower)) {
                suggestions.add(technique.style);
            }

            // Add category if it matches
            if (technique.category && technique.category.toLowerCase().includes(queryLower)) {
                suggestions.add(technique.category);
            }

            // Add matching tags
            if (technique.tags) {
                technique.tags.forEach(tag => {
                    if (tag.toLowerCase().includes(queryLower)) {
                        suggestions.add(tag);
                    }
                });
            }
        });

        return Array.from(suggestions).slice(0, 5); // Limit to 5 suggestions
    }

    // Filter techniques by multiple criteria
    filterTechniques(techniques, filters) {
        let filtered = [...techniques];

        // Search query
        if (filters.query) {
            const query = filters.query.toLowerCase();
            filtered = filtered.filter(technique =>
                technique.name.toLowerCase().includes(query) ||
                technique.description?.toLowerCase().includes(query) ||
                technique.style?.toLowerCase().includes(query) ||
                technique.tags?.some(tag => tag.toLowerCase().includes(query))
            );
        }

        // Style filter
        if (filters.style) {
            filtered = filtered.filter(technique =>
                technique.style?.toLowerCase() === filters.style.toLowerCase()
            );
        }

        // Category filter
        if (filters.category) {
            filtered = filtered.filter(technique =>
                technique.category?.toLowerCase() === filters.category.toLowerCase()
            );
        }

        // Difficulty filter
        if (filters.difficulty) {
            const difficulty = parseInt(filters.difficulty);
            if (difficulty <= 3) {
                filtered = filtered.filter(technique =>
                    (technique.difficulty_level || 5) <= 3
                );
            } else if (difficulty <= 6) {
                filtered = filtered.filter(technique =>
                    (technique.difficulty_level || 5) >= 4 && (technique.difficulty_level || 5) <= 6
                );
            } else {
                filtered = filtered.filter(technique =>
                    (technique.difficulty_level || 5) >= 7
                );
            }
        }

        // Tag filter
        if (filters.tags && filters.tags.length > 0) {
            filtered = filtered.filter(technique =>
                technique.tags && filters.tags.some(tag =>
                    technique.tags.some(techTag =>
                        techTag.toLowerCase().includes(tag.toLowerCase())
                    )
                )
            );
        }

        return filtered;
    }

    // Sort techniques
    sortTechniques(techniques, sortBy) {
        const sorted = [...techniques];

        switch (sortBy) {
            case 'name':
                return sorted.sort((a, b) => a.name.localeCompare(b.name));

            case 'difficulty':
                return sorted.sort((a, b) => (a.difficulty_level || 5) - (b.difficulty_level || 5));

            case 'popular':
                return sorted.sort((a, b) => (b.view_count || 0) - (a.view_count || 0));

            case 'style':
                return sorted.sort((a, b) => (a.style || '').localeCompare(b.style || ''));

            case 'recent':
                return sorted.sort((a, b) => {
                    const dateA = new Date(a.last_updated || a.created_at || 0);
                    const dateB = new Date(b.last_updated || b.created_at || 0);
                    return dateB - dateA;
                });

            default:
                return sorted;
        }
    }
}

// Export singleton instance
const techniqueService = new TechniqueService();
export default techniqueService;