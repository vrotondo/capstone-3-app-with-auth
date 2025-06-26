import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import Button from '../components/common/Button';
import LoadingSpinner from '../components/common/LoadingSpinner';
import '../styles/pages/techniques.css';

const Techniques = () => {
    const { user } = useAuth();
    const [activeTab, setActiveTab] = useState('browse');
    const [techniques, setTechniques] = useState([]);
    const [myTechniques, setMyTechniques] = useState([]);
    const [bookmarkedTechniques, setBookmarkedTechniques] = useState([]);
    const [popularTechniques, setPopularTechniques] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedStyle, setSelectedStyle] = useState('all');
    const [selectedCategory, setSelectedCategory] = useState('all');
    const [selectedDifficulty, setSelectedDifficulty] = useState('all');
    const [styles, setStyles] = useState([]);
    const [categories, setCategories] = useState([]);
    const [stats, setStats] = useState({});
    const [isLoading, setIsLoading] = useState(false);
    const [showAddForm, setShowAddForm] = useState(false);
    const [selectedTechnique, setSelectedTechnique] = useState(null);
    const [showImportModal, setShowImportModal] = useState(false);
    const [importLoading, setImportLoading] = useState(false);
    const [error, setError] = useState('');

    // API Configuration
    const API_BASE = 'http://localhost:8000/api';
    const getAuthHeaders = () => {
        const token = localStorage.getItem('token');
        return {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
        };
    };

    // API Functions
    const apiCall = async (endpoint, options = {}) => {
        try {
            const response = await fetch(`${API_BASE}${endpoint}`, {
                headers: getAuthHeaders(),
                ...options
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API call failed:', error);
            throw error;
        }
    };

    // Load techniques with search and filters
    const searchTechniques = useCallback(async () => {
        try {
            setIsLoading(true);
            setError('');

            const params = new URLSearchParams();
            if (searchTerm && searchTerm !== '') params.append('q', searchTerm);
            if (selectedStyle && selectedStyle !== 'all') params.append('style', selectedStyle);
            if (selectedCategory && selectedCategory !== 'all') params.append('category', selectedCategory);
            if (selectedDifficulty && selectedDifficulty !== 'all') params.append('difficulty', selectedDifficulty);
            params.append('limit', '20');

            const data = await apiCall(`/techniques/search?${params}`);
            setTechniques(data.techniques || []);
        } catch (error) {
            console.error('Search failed:', error);
            setError('Failed to search techniques. Please try again.');
            setTechniques([]);
        } finally {
            setIsLoading(false);
        }
    }, [searchTerm, selectedStyle, selectedCategory, selectedDifficulty]);

    // Load initial data
    const loadInitialData = async () => {
        try {
            setIsLoading(true);
            setError('');

            // Load initial techniques, styles, categories, and stats
            const [
                searchData,
                popularData,
                stylesData,
                categoriesData,
                statsData
            ] = await Promise.all([
                apiCall('/techniques/search?limit=12'),
                apiCall('/techniques/popular?limit=6'),
                apiCall('/techniques/styles'),
                apiCall('/techniques/categories'),
                apiCall('/techniques/stats')
            ]);

            setTechniques(searchData.techniques || []);
            setPopularTechniques(popularData.techniques || []);
            setStyles(stylesData.styles || []);
            setCategories(categoriesData.categories || []);
            setStats(statsData.stats || {});

            // Load user-specific data if authenticated
            if (user) {
                try {
                    const bookmarksData = await apiCall('/techniques/bookmarks');
                    setBookmarkedTechniques(bookmarksData.bookmarks || []);
                } catch (bookmarkError) {
                    console.warn('Failed to load bookmarks:', bookmarkError);
                }
            }
        } catch (error) {
            console.error('Failed to load initial data:', error);
            setError('Failed to load technique data. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    // Load user's personal techniques (your existing functionality)
    const loadMyTechniques = async () => {
        try {
            // Keep your existing API call when you implement it
            // For now, keeping empty array
            setMyTechniques([]);
        } catch (error) {
            console.error('Failed to load my techniques:', error);
        }
    };

    // Get technique details
    const getTechniqueDetail = async (techniqueId) => {
        try {
            const data = await apiCall(`/techniques/${techniqueId}`);
            setSelectedTechnique(data.technique);
        } catch (error) {
            console.error('Failed to get technique detail:', error);
            setError('Failed to load technique details.');
        }
    };

    // Bookmark/unbookmark technique
    const toggleBookmark = async (techniqueId, isCurrentlyBookmarked) => {
        if (!user) {
            setError('Please log in to bookmark techniques');
            return;
        }

        try {
            if (isCurrentlyBookmarked) {
                await apiCall(`/techniques/${techniqueId}/bookmark`, { method: 'DELETE' });
            } else {
                await apiCall(`/techniques/${techniqueId}/bookmark`, {
                    method: 'POST',
                    body: JSON.stringify({})
                });
            }

            // Refresh bookmarks
            const bookmarksData = await apiCall('/techniques/bookmarks');
            setBookmarkedTechniques(bookmarksData.bookmarks || []);

            // Update the technique in current list
            setTechniques(prev => prev.map(t =>
                t.id === techniqueId ? { ...t, is_bookmarked: !isCurrentlyBookmarked } : t
            ));

            // Update popular techniques too
            setPopularTechniques(prev => prev.map(t =>
                t.id === techniqueId ? { ...t, is_bookmarked: !isCurrentlyBookmarked } : t
            ));
        } catch (error) {
            console.error('Failed to toggle bookmark:', error);
            setError('Failed to update bookmark. Please try again.');
        }
    };

    // Import techniques from BlackBeltWiki
    const importTechniques = async () => {
        if (!user) {
            setError('Please log in to import techniques');
            return;
        }

        try {
            setImportLoading(true);
            const data = await apiCall('/techniques/import', {
                method: 'POST',
                body: JSON.stringify({
                    source: 'blackbeltwiki',
                    max_techniques: 10
                })
            });

            setError(''); // Clear any previous errors
            alert(`Import successful! Imported: ${data.import_result.imported}, Updated: ${data.import_result.updated}`);

            // Refresh the data
            await loadInitialData();
            setShowImportModal(false);
        } catch (error) {
            console.error('Import failed:', error);
            setError('Import failed. Please try again.');
        } finally {
            setImportLoading(false);
        }
    };

    // Form handling for your existing add technique functionality
    const [newTechnique, setNewTechnique] = useState({
        name: '',
        style: '',
        category: '',
        difficulty: 'Beginner',
        description: '',
        notes: '',
        mastery_level: 'Learning'
    });

    const handleAddTechnique = async (e) => {
        e.preventDefault();
        try {
            // TODO: Replace with actual API call to your backend
            const newTechniqueWithId = {
                ...newTechnique,
                id: Date.now(),
                date_added: new Date().toISOString()
            };
            setMyTechniques([...myTechniques, newTechniqueWithId]);
            setNewTechnique({
                name: '',
                style: '',
                category: '',
                difficulty: 'Beginner',
                description: '',
                notes: '',
                mastery_level: 'Learning'
            });
            setShowAddForm(false);
        } catch (error) {
            console.error('Failed to add technique:', error);
            setError('Failed to add technique. Please try again.');
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setNewTechnique(prev => ({
            ...prev,
            [name]: value
        }));
    };

    // Load data on component mount and when user changes
    useEffect(() => {
        loadInitialData();
        loadMyTechniques();
    }, [user]);

    // Debounced search
    useEffect(() => {
        const timeoutId = setTimeout(() => {
            if (activeTab === 'browse') {
                searchTechniques();
            }
        }, 300);
        return () => clearTimeout(timeoutId);
    }, [searchTechniques, activeTab]);

    // Filter techniques for browse tab
    const filteredTechniques = activeTab === 'popular' ? popularTechniques : techniques;

    if (isLoading && techniques.length === 0 && activeTab === 'browse') {
        return <LoadingSpinner />;
    }

    return (
        <div className="techniques-page">
            <div className="page-header">
                <div className="header-content">
                    <div>
                        <h1>Technique Library</h1>
                        <p>Discover and manage your martial arts techniques</p>
                    </div>
                    {user && (
                        <Button
                            variant="primary"
                            onClick={() => setShowImportModal(true)}
                        >
                            Import from BlackBeltWiki
                        </Button>
                    )}
                </div>
            </div>

            {error && (
                <div className="error-message">
                    {error}
                    <button onClick={() => setError('')} className="error-close">×</button>
                </div>
            )}

            {/* Stats Section */}
            {stats.total_techniques > 0 && (
                <div className="techniques-stats">
                    <div className="stat-item">
                        <span className="stat-number">{stats.total_techniques || 0}</span>
                        <span className="stat-label">Total Techniques</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-number">{stats.total_styles || 0}</span>
                        <span className="stat-label">Martial Arts Styles</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-number">{stats.total_categories || 0}</span>
                        <span className="stat-label">Categories</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-number">{stats.total_bookmarks || 0}</span>
                        <span className="stat-label">Total Bookmarks</span>
                    </div>
                </div>
            )}

            <div className="techniques-tabs">
                <button
                    className={`tab-button ${activeTab === 'browse' ? 'active' : ''}`}
                    onClick={() => setActiveTab('browse')}
                >
                    Browse Techniques
                </button>
                {user && (
                    <>
                        <button
                            className={`tab-button ${activeTab === 'bookmarks' ? 'active' : ''}`}
                            onClick={() => setActiveTab('bookmarks')}
                        >
                            My Bookmarks ({bookmarkedTechniques.length})
                        </button>
                        <button
                            className={`tab-button ${activeTab === 'my-techniques' ? 'active' : ''}`}
                            onClick={() => setActiveTab('my-techniques')}
                        >
                            My Techniques ({myTechniques.length})
                        </button>
                    </>
                )}
                <button
                    className={`tab-button ${activeTab === 'popular' ? 'active' : ''}`}
                    onClick={() => setActiveTab('popular')}
                >
                    Popular
                </button>
            </div>

            {(activeTab === 'browse' || activeTab === 'popular') && (
                <div className="browse-techniques">
                    {activeTab === 'browse' && (
                        <div className="techniques-filters">
                            <div className="search-bar">
                                <input
                                    type="text"
                                    placeholder="Search techniques..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    className="form-input"
                                />
                            </div>
                            <div className="style-filter">
                                <select
                                    value={selectedStyle}
                                    onChange={(e) => setSelectedStyle(e.target.value)}
                                    className="form-select"
                                >
                                    <option value="all">All Styles</option>
                                    {styles.map((style) => (
                                        <option key={style} value={style}>{style}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="category-filter">
                                <select
                                    value={selectedCategory}
                                    onChange={(e) => setSelectedCategory(e.target.value)}
                                    className="form-select"
                                >
                                    <option value="all">All Categories</option>
                                    {categories.map((category) => (
                                        <option key={category} value={category}>{category}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="difficulty-filter">
                                <select
                                    value={selectedDifficulty}
                                    onChange={(e) => setSelectedDifficulty(e.target.value)}
                                    className="form-select"
                                >
                                    <option value="all">All Levels</option>
                                    {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((level) => (
                                        <option key={level} value={level}>Level {level}/10</option>
                                    ))}
                                </select>
                            </div>
                        </div>
                    )}

                    <div className="techniques-results">
                        <div className="results-header">
                            <h2>
                                {activeTab === 'popular' ? 'Popular Techniques' :
                                    searchTerm || selectedStyle !== 'all' || selectedCategory !== 'all' ? 'Search Results' : 'Browse Techniques'}
                            </h2>
                            <span className="results-count">
                                {filteredTechniques.length} techniques found
                            </span>
                        </div>

                        {isLoading && activeTab === 'browse' ? (
                            <div className="loading-grid">
                                {[...Array(6)].map((_, i) => (
                                    <div key={i} className="technique-card loading">
                                        <div className="loading-content"></div>
                                    </div>
                                ))}
                            </div>
                        ) : filteredTechniques.length > 0 ? (
                            <div className="techniques-grid">
                                {filteredTechniques.map(technique => (
                                    <div key={technique.id} className="technique-card">
                                        <div className="technique-header">
                                            <h3>{technique.name}</h3>
                                            <div className="technique-badges">
                                                {technique.difficulty_level && (
                                                    <span className="difficulty-badge">
                                                        Level {technique.difficulty_level}/10
                                                    </span>
                                                )}
                                                {user && (
                                                    <button
                                                        onClick={() => toggleBookmark(technique.id, technique.is_bookmarked)}
                                                        className={`bookmark-btn ${technique.is_bookmarked ? 'bookmarked' : ''}`}
                                                        title={technique.is_bookmarked ? 'Remove bookmark' : 'Add bookmark'}
                                                    >
                                                        ♥
                                                    </button>
                                                )}
                                            </div>
                                        </div>
                                        <div className="technique-meta">
                                            <span className="technique-style">{technique.style}</span>
                                            {technique.category && (
                                                <span className="technique-category">{technique.category}</span>
                                            )}
                                        </div>
                                        {technique.description && (
                                            <p className="technique-description">
                                                {technique.description.length > 150
                                                    ? `${technique.description.substring(0, 150)}...`
                                                    : technique.description
                                                }
                                            </p>
                                        )}
                                        <div className="technique-stats">
                                            <span>👁 {technique.view_count || 0}</span>
                                            <span>♥ {technique.bookmark_count || 0}</span>
                                        </div>
                                        <div className="technique-actions">
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                onClick={() => getTechniqueDetail(technique.id)}
                                            >
                                                View Details
                                            </Button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="no-results">
                                <h3>No techniques found</h3>
                                <p>
                                    {activeTab === 'popular'
                                        ? 'Popular techniques will appear here based on community views and bookmarks.'
                                        : 'Try adjusting your search criteria or import techniques from BlackBeltWiki.'
                                    }
                                </p>
                                {user && activeTab !== 'popular' && (
                                    <Button
                                        variant="primary"
                                        onClick={() => setShowImportModal(true)}
                                    >
                                        Import Techniques
                                    </Button>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            )}

            {activeTab === 'bookmarks' && user && (
                <div className="bookmarks-section">
                    <div className="section-header">
                        <h2>My Bookmarked Techniques</h2>
                        <span className="results-count">{bookmarkedTechniques.length} bookmarks</span>
                    </div>

                    {bookmarkedTechniques.length > 0 ? (
                        <div className="techniques-grid">
                            {bookmarkedTechniques.map(bookmark => (
                                <div key={bookmark.id} className="technique-card bookmark-card">
                                    <div className="technique-header">
                                        <h3>{bookmark.technique?.name}</h3>
                                        <button
                                            onClick={() => toggleBookmark(bookmark.technique_id, true)}
                                            className="bookmark-btn bookmarked"
                                            title="Remove bookmark"
                                        >
                                            ♥
                                        </button>
                                    </div>
                                    <div className="technique-meta">
                                        <span className="technique-style">{bookmark.technique?.style}</span>
                                        {bookmark.mastery_level && (
                                            <span className="mastery-badge">
                                                Mastery: {bookmark.mastery_level}/10
                                            </span>
                                        )}
                                    </div>
                                    <div className="bookmark-stats">
                                        <span>Practiced: {bookmark.practice_count || 0}x</span>
                                        {bookmark.last_practiced && (
                                            <span>Last: {new Date(bookmark.last_practiced).toLocaleDateString()}</span>
                                        )}
                                    </div>
                                    {bookmark.personal_notes && (
                                        <div className="personal-notes">
                                            <strong>Notes:</strong> {bookmark.personal_notes}
                                        </div>
                                    )}
                                    <div className="technique-actions">
                                        <Button
                                            variant="outline"
                                            size="sm"
                                            onClick={() => getTechniqueDetail(bookmark.technique_id)}
                                        >
                                            View Details
                                        </Button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="no-results">
                            <h3>No bookmarks yet</h3>
                            <p>Start bookmarking techniques you want to practice and track your progress.</p>
                            <Button
                                variant="primary"
                                onClick={() => setActiveTab('browse')}
                            >
                                Browse Techniques
                            </Button>
                        </div>
                    )}
                </div>
            )}

            {activeTab === 'my-techniques' && (
                <div className="my-techniques">
                    <div className="my-techniques-header">
                        <h2>Your Personal Technique Collection</h2>
                        <Button
                            variant="primary"
                            onClick={() => setShowAddForm(true)}
                        >
                            Add New Technique
                        </Button>
                    </div>

                    {showAddForm && (
                        <div className="add-technique-form">
                            <div className="form-header">
                                <h3>Add New Technique</h3>
                                <button
                                    className="close-button"
                                    onClick={() => setShowAddForm(false)}
                                >
                                    ×
                                </button>
                            </div>
                            <form onSubmit={handleAddTechnique}>
                                <div className="form-grid">
                                    <div className="form-group">
                                        <label>Technique Name *</label>
                                        <input
                                            type="text"
                                            name="name"
                                            value={newTechnique.name}
                                            onChange={handleInputChange}
                                            className="form-input"
                                            required
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>Martial Art Style *</label>
                                        <input
                                            type="text"
                                            name="style"
                                            value={newTechnique.style}
                                            onChange={handleInputChange}
                                            className="form-input"
                                            required
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>Category</label>
                                        <select
                                            name="category"
                                            value={newTechnique.category}
                                            onChange={handleInputChange}
                                            className="form-select"
                                        >
                                            <option value="">Select category</option>
                                            <option value="Kicks">Kicks</option>
                                            <option value="Punches">Punches</option>
                                            <option value="Throws">Throws</option>
                                            <option value="Grappling">Grappling</option>
                                            <option value="Blocks">Blocks</option>
                                            <option value="Kata/Forms">Kata/Forms</option>
                                        </select>
                                    </div>
                                    <div className="form-group">
                                        <label>Difficulty Level</label>
                                        <select
                                            name="difficulty"
                                            value={newTechnique.difficulty}
                                            onChange={handleInputChange}
                                            className="form-select"
                                        >
                                            <option value="Beginner">Beginner</option>
                                            <option value="Intermediate">Intermediate</option>
                                            <option value="Advanced">Advanced</option>
                                        </select>
                                    </div>
                                    <div className="form-group">
                                        <label>Mastery Level</label>
                                        <select
                                            name="mastery_level"
                                            value={newTechnique.mastery_level}
                                            onChange={handleInputChange}
                                            className="form-select"
                                        >
                                            <option value="Learning">Learning</option>
                                            <option value="Practicing">Practicing</option>
                                            <option value="Proficient">Proficient</option>
                                            <option value="Mastered">Mastered</option>
                                        </select>
                                    </div>
                                </div>
                                <div className="form-group">
                                    <label>Description</label>
                                    <textarea
                                        name="description"
                                        value={newTechnique.description}
                                        onChange={handleInputChange}
                                        className="form-textarea"
                                        rows="3"
                                        placeholder="Describe the technique..."
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Personal Notes</label>
                                    <textarea
                                        name="notes"
                                        value={newTechnique.notes}
                                        onChange={handleInputChange}
                                        className="form-textarea"
                                        rows="3"
                                        placeholder="Your notes, tips, or observations..."
                                    />
                                </div>
                                <div className="form-actions">
                                    <Button
                                        type="button"
                                        variant="outline"
                                        onClick={() => setShowAddForm(false)}
                                    >
                                        Cancel
                                    </Button>
                                    <Button type="submit" variant="primary">
                                        Add Technique
                                    </Button>
                                </div>
                            </form>
                        </div>
                    )}

                    <div className="my-techniques-grid">
                        {myTechniques.map(technique => (
                            <div key={technique.id} className="my-technique-card">
                                <div className="technique-header">
                                    <h3>{technique.name}</h3>
                                    <span className={`mastery-badge ${technique.mastery_level.toLowerCase()}`}>
                                        {technique.mastery_level}
                                    </span>
                                </div>
                                <div className="technique-meta">
                                    <span className="technique-style">{technique.style}</span>
                                    {technique.category && (
                                        <span className="technique-category">{technique.category}</span>
                                    )}
                                </div>
                                {technique.description && (
                                    <p className="technique-description">{technique.description}</p>
                                )}
                                {technique.notes && (
                                    <div className="technique-notes">
                                        <strong>Notes:</strong> {technique.notes}
                                    </div>
                                )}
                                <div className="technique-actions">
                                    <Button variant="outline" size="sm">
                                        Edit
                                    </Button>
                                    <Button variant="outline" size="sm">
                                        Update Progress
                                    </Button>
                                </div>
                            </div>
                        ))}
                    </div>

                    {myTechniques.length === 0 && (
                        <div className="no-techniques">
                            <div className="empty-state">
                                <h3>No techniques added yet</h3>
                                <p>Start building your personal technique library by adding techniques you're learning or practicing.</p>
                                <Button
                                    variant="primary"
                                    onClick={() => setShowAddForm(true)}
                                >
                                    Add Your First Technique
                                </Button>
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Import Modal */}
            {showImportModal && (
                <div className="modal-overlay">
                    <div className="modal-content">
                        <div className="modal-header">
                            <h3>Import Techniques from BlackBeltWiki</h3>
                            <button
                                className="close-button"
                                onClick={() => setShowImportModal(false)}
                                disabled={importLoading}
                            >
                                ×
                            </button>
                        </div>
                        <div className="modal-body">
                            <p>This will import up to 10 techniques from BlackBeltWiki.com. The process may take a few minutes.</p>
                        </div>
                        <div className="modal-actions">
                            <Button
                                variant="outline"
                                onClick={() => setShowImportModal(false)}
                                disabled={importLoading}
                            >
                                Cancel
                            </Button>
                            <Button
                                variant="primary"
                                onClick={importTechniques}
                                disabled={importLoading}
                            >
                                {importLoading ? 'Importing...' : 'Import Techniques'}
                            </Button>
                        </div>
                    </div>
                </div>
            )}

            {/* Technique Detail Modal */}
            {selectedTechnique && (
                <div className="modal-overlay">
                    <div className="modal-content technique-detail-modal">
                        <div className="modal-header">
                            <h2>{selectedTechnique.name}</h2>
                            <button
                                className="close-button"
                                onClick={() => setSelectedTechnique(null)}
                            >
                                ×
                            </button>
                        </div>
                        <div className="modal-body">
                            <div className="technique-badges">
                                <span className="technique-style">{selectedTechnique.style}</span>
                                {selectedTechnique.category && (
                                    <span className="technique-category">{selectedTechnique.category}</span>
                                )}
                                {selectedTechnique.difficulty_level && (
                                    <span className="difficulty-badge">
                                        Level {selectedTechnique.difficulty_level}/10
                                    </span>
                                )}
                                {selectedTechnique.belt_level && (
                                    <span className="belt-badge">{selectedTechnique.belt_level}</span>
                                )}
                            </div>

                            {selectedTechnique.description && (
                                <div className="technique-section">
                                    <h3>Description</h3>
                                    <p>{selectedTechnique.description}</p>
                                </div>
                            )}

                            {selectedTechnique.instructions && (
                                <div className="technique-section">
                                    <h3>Instructions</h3>
                                    <div className="technique-content">
                                        {selectedTechnique.instructions.split('\n').map((line, index) => (
                                            <p key={index}>{line}</p>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {selectedTechnique.tips && (
                                <div className="technique-section">
                                    <h3>Tips</h3>
                                    <p>{selectedTechnique.tips}</p>
                                </div>
                            )}

                            {selectedTechnique.variations && (
                                <div className="technique-section">
                                    <h3>Variations</h3>
                                    <div className="technique-content">
                                        {selectedTechnique.variations.split('\n').map((line, index) => (
                                            <p key={index}>{line}</p>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {selectedTechnique.tags && selectedTechnique.tags.length > 0 && (
                                <div className="technique-section">
                                    <h3>Tags</h3>
                                    <div className="tags-container">
                                        {selectedTechnique.tags.map((tag, index) => (
                                            <span key={index} className="tag">#{tag}</span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* User Progress Section */}
                            {user && selectedTechnique.user_bookmark && (
                                <div className="technique-section user-progress">
                                    <h3>Your Progress</h3>
                                    <div className="progress-stats">
                                        <div className="progress-stat">
                                            <span className="progress-label">Mastery Level:</span>
                                            <span className="progress-value">{selectedTechnique.user_bookmark.mastery_level}/10</span>
                                        </div>
                                        <div className="progress-stat">
                                            <span className="progress-label">Practice Count:</span>
                                            <span className="progress-value">{selectedTechnique.user_bookmark.practice_count}</span>
                                        </div>
                                    </div>
                                    {selectedTechnique.user_bookmark.personal_notes && (
                                        <div className="personal-notes">
                                            <span className="progress-label">Your Notes:</span>
                                            <p>"{selectedTechnique.user_bookmark.personal_notes}"</p>
                                        </div>
                                    )}
                                </div>
                            )}

                            <div className="technique-metadata">
                                <div className="metadata-stats">
                                    <span>👁 {selectedTechnique.view_count || 0} views</span>
                                    <span>♥ {selectedTechnique.bookmark_count || 0} bookmarks</span>
                                    {selectedTechnique.source_url && (
                                        <a
                                            href={selectedTechnique.source_url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="source-link"
                                        >
                                            🔗 Source
                                        </a>
                                    )}
                                </div>
                            </div>
                        </div>
                        <div className="modal-actions">
                            {user && (
                                <Button
                                    variant={selectedTechnique.is_bookmarked ? "outline" : "primary"}
                                    onClick={() => toggleBookmark(selectedTechnique.id, selectedTechnique.is_bookmarked)}
                                >
                                    {selectedTechnique.is_bookmarked ? 'Remove Bookmark' : 'Bookmark Technique'}
                                </Button>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* No user message for auth-required tabs */}
            {(activeTab === 'bookmarks' || activeTab === 'my-techniques') && !user && (
                <div className="auth-required">
                    <h3>Sign in Required</h3>
                    <p>Please sign in to view and manage your techniques and bookmarks.</p>
                </div>
            )}
        </div>
    );
};

export default Techniques;