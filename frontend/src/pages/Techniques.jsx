import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
    Search, Filter, Star, BookOpen, Eye, TrendingUp,
    ChevronLeft, ChevronRight, Plus, Download, Upload,
    Grid, List, SortAsc, X, Loader, Target, Award,
    Users, Zap, Calendar, BarChart3
} from 'lucide-react';
import Button from '../components/common/Button';
import techniqueService from '../services/techniqueService';

const Techniques = () => {
    const navigate = useNavigate();
    const { user } = useAuth();

    // State management
    const [techniques, setTechniques] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [importing, setImporting] = useState(false);

    // Search and filters
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedStyle, setSelectedStyle] = useState('');
    const [selectedCategory, setSelectedCategory] = useState('');
    const [selectedDifficulty, setSelectedDifficulty] = useState('');
    const [sortBy, setSortBy] = useState('name');

    // Pagination
    const [currentPage, setCurrentPage] = useState(1);
    const [hasMore, setHasMore] = useState(false);
    const techniquesPerPage = 20;

    // Filter options
    const [styles, setStyles] = useState([]);
    const [categories, setCategories] = useState([]);
    const [stats, setStats] = useState({});

    // View mode
    const [viewMode, setViewMode] = useState('grid');

    // Load initial data
    useEffect(() => {
        loadInitialData();
    }, []);

    // Reload techniques when filters change
    useEffect(() => {
        setCurrentPage(1);
        loadTechniques();
    }, [searchQuery, selectedStyle, selectedCategory, selectedDifficulty, sortBy]);

    // Load more techniques when page changes
    useEffect(() => {
        if (currentPage > 1) {
            loadTechniques();
        }
    }, [currentPage]);

    const loadInitialData = async () => {
        try {
            await Promise.all([
                loadFilterOptions(),
                loadStats(),
                loadTechniques()
            ]);
        } catch (error) {
            console.error('Error loading initial data:', error);
            setError('Failed to load technique library');
        }
    };

    const loadTechniques = async () => {
        try {
            setLoading(true);
            setError(null);

            const params = {
                q: searchQuery || undefined,
                style: selectedStyle || undefined,
                category: selectedCategory || undefined,
                difficulty: selectedDifficulty || undefined,
                sort: sortBy,
                limit: techniquesPerPage,
                offset: (currentPage - 1) * techniquesPerPage
            };

            const response = await techniqueService.searchTechniques(params);

            if (currentPage === 1) {
                setTechniques(response.techniques || []);
            } else {
                setTechniques(prev => [...prev, ...(response.techniques || [])]);
            }

            setHasMore(response.has_more || false);

        } catch (error) {
            console.error('Error loading techniques:', error);
            setError('Failed to load techniques. Please try again.');
            setTechniques([]);
        } finally {
            setLoading(false);
        }
    };

    const loadFilterOptions = async () => {
        try {
            const [stylesRes, categoriesRes] = await Promise.all([
                techniqueService.getStyles(),
                techniqueService.getCategories()
            ]);

            setStyles(stylesRes.styles || []);
            setCategories(categoriesRes.categories || []);
        } catch (error) {
            console.error('Error loading filter options:', error);
        }
    };

    const loadStats = async () => {
        try {
            const response = await techniqueService.getStats();
            setStats(response.stats || {});
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    };

    const handleImportFromBlackBeltWiki = async () => {
        if (!user) {
            alert('Please log in to import techniques');
            return;
        }

        if (!confirm('This will import techniques from Black Belt Wiki. Continue?')) {
            return;
        }

        try {
            setImporting(true);
            const result = await techniqueService.importTechniques('blackbeltwiki', 20);

            alert(`Successfully imported ${result.imported_count} techniques!`);

            // Refresh the technique list
            setCurrentPage(1);
            await loadTechniques();
            await loadStats();

        } catch (error) {
            console.error('Import error:', error);
            alert(`Import failed: ${error.message}`);
        } finally {
            setImporting(false);
        }
    };

    const handleSearch = (e) => {
        e.preventDefault();
    };

    const clearFilters = () => {
        setSearchQuery('');
        setSelectedStyle('');
        setSelectedCategory('');
        setSelectedDifficulty('');
        setSortBy('name');
    };

    const hasActiveFilters = searchQuery || selectedStyle || selectedCategory || selectedDifficulty;

    const handleTechniqueClick = (technique) => {
        navigate(`/techniques/${technique.id}`);
    };

    const handleBookmarkToggle = async (techniqueId, isCurrentlyBookmarked) => {
        if (!user) {
            alert('Please log in to bookmark techniques');
            return;
        }

        try {
            if (isCurrentlyBookmarked) {
                await techniqueService.removeBookmark(techniqueId);
            } else {
                await techniqueService.bookmarkTechnique(techniqueId);
            }

            // Update local state
            setTechniques(prev => prev.map(tech =>
                tech.id === techniqueId
                    ? { ...tech, is_bookmarked: !isCurrentlyBookmarked }
                    : tech
            ));
        } catch (error) {
            console.error('Bookmark error:', error);
            alert('Failed to update bookmark');
        }
    };

    if (loading && techniques.length === 0) {
        return (
            <div className="loading-container">
                <div className="spinner spinner-md"></div>
                <p className="mt-md text-secondary">Loading technique library...</p>
            </div>
        );
    }

    return (
        <div className="techniques-page">
            {/* Hero Header */}
            <div className="page-header">
                <div className="container">
                    <div className="header-content">
                        <div className="hero-section">
                            <h1 className="flex items-center gap-md">
                                <BookOpen className="text-primary" size={48} />
                                Technique Library
                            </h1>
                            <p>
                                Discover, learn, and master martial arts techniques from around the world.
                                Build your personal collection and track your progress.
                            </p>
                        </div>

                        <div className="header-actions">
                            {user && (
                                <div className="flex gap-sm">
                                    <Button
                                        variant="outline"
                                        onClick={() => navigate('/my-techniques')}
                                        className="btn-md"
                                    >
                                        <Star size={20} />
                                        My Techniques
                                    </Button>

                                    <Button
                                        variant="primary"
                                        onClick={handleImportFromBlackBeltWiki}
                                        disabled={importing}
                                        className="btn-md"
                                    >
                                        {importing ? (
                                            <Loader className="animate-spin" size={20} />
                                        ) : (
                                            <Download size={20} />
                                        )}
                                        {importing ? 'Importing...' : 'Import Techniques'}
                                    </Button>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            <div className="container">
                {/* Stats Overview */}
                <div className="techniques-stats">
                    <div className="stat-item">
                        <BookOpen className="text-primary mb-sm" size={32} />
                        <span className="stat-number">{stats.total_techniques || 0}</span>
                        <span className="stat-label">Total Techniques</span>
                    </div>
                    <div className="stat-item">
                        <Target className="text-success mb-sm" size={32} />
                        <span className="stat-number">{stats.total_styles || 0}</span>
                        <span className="stat-label">Martial Arts Styles</span>
                    </div>
                    <div className="stat-item">
                        <Award className="text-warning mb-sm" size={32} />
                        <span className="stat-number">{stats.total_categories || 0}</span>
                        <span className="stat-label">Categories</span>
                    </div>
                    <div className="stat-item">
                        <Users className="text-secondary mb-sm" size={32} />
                        <span className="stat-number">{stats.total_bookmarks || 0}</span>
                        <span className="stat-label">Total Bookmarks</span>
                    </div>
                </div>

                {/* Search and Filters */}
                <div className="form-section">
                    <div className="form-header">
                        <h2>Find Techniques</h2>
                        <p>Search and filter to find exactly what you're looking for</p>
                    </div>

                    <form onSubmit={handleSearch} className="techniques-filters">
                        {/* Search Bar */}
                        <div className="form-field">
                            <label className="form-label">Search Techniques</label>
                            <div className="relative">
                                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted" />
                                <input
                                    type="text"
                                    placeholder="Search by name, style, or description..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    className="form-input pl-10"
                                />
                                {searchQuery && (
                                    <button
                                        type="button"
                                        onClick={() => setSearchQuery('')}
                                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted hover:text-primary"
                                    >
                                        <X size={16} />
                                    </button>
                                )}
                            </div>
                        </div>

                        {/* Filter Row */}
                        <div className="filter-row">
                            <div className="form-field">
                                <label className="form-label">Martial Art Style</label>
                                <select
                                    value={selectedStyle}
                                    onChange={(e) => setSelectedStyle(e.target.value)}
                                    className="form-input"
                                >
                                    <option value="">All Styles</option>
                                    {styles.map(style => (
                                        <option key={style} value={style}>{style}</option>
                                    ))}
                                </select>
                            </div>

                            <div className="form-field">
                                <label className="form-label">Category</label>
                                <select
                                    value={selectedCategory}
                                    onChange={(e) => setSelectedCategory(e.target.value)}
                                    className="form-input"
                                >
                                    <option value="">All Categories</option>
                                    {categories.map(category => (
                                        <option key={category} value={category}>{category}</option>
                                    ))}
                                </select>
                            </div>

                            <div className="form-field">
                                <label className="form-label">Difficulty Level</label>
                                <select
                                    value={selectedDifficulty}
                                    onChange={(e) => setSelectedDifficulty(e.target.value)}
                                    className="form-input"
                                >
                                    <option value="">All Levels</option>
                                    <option value="1">Beginner (1-3)</option>
                                    <option value="4">Intermediate (4-6)</option>
                                    <option value="7">Advanced (7-10)</option>
                                </select>
                            </div>

                            <div className="form-field">
                                <label className="form-label">Sort By</label>
                                <select
                                    value={sortBy}
                                    onChange={(e) => setSortBy(e.target.value)}
                                    className="form-input"
                                >
                                    <option value="name">Name A-Z</option>
                                    <option value="difficulty">Difficulty Level</option>
                                    <option value="popular">Most Popular</option>
                                    <option value="style">Martial Art Style</option>
                                    <option value="recent">Recently Added</option>
                                </select>
                            </div>
                        </div>

                        {/* Active Filters */}
                        {hasActiveFilters && (
                            <div className="active-filters">
                                <span className="filter-label">Active filters:</span>
                                {searchQuery && (
                                    <span className="filter-tag">
                                        Search: "{searchQuery}"
                                        <button onClick={() => setSearchQuery('')}>
                                            <X size={14} />
                                        </button>
                                    </span>
                                )}
                                {selectedStyle && (
                                    <span className="filter-tag">
                                        Style: {selectedStyle}
                                        <button onClick={() => setSelectedStyle('')}>
                                            <X size={14} />
                                        </button>
                                    </span>
                                )}
                                {selectedCategory && (
                                    <span className="filter-tag">
                                        Category: {selectedCategory}
                                        <button onClick={() => setSelectedCategory('')}>
                                            <X size={14} />
                                        </button>
                                    </span>
                                )}
                                {selectedDifficulty && (
                                    <span className="filter-tag">
                                        Difficulty: {selectedDifficulty === '1' ? 'Beginner' : selectedDifficulty === '4' ? 'Intermediate' : 'Advanced'}
                                        <button onClick={() => setSelectedDifficulty('')}>
                                            <X size={14} />
                                        </button>
                                    </span>
                                )}
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={clearFilters}
                                    className="text-error"
                                >
                                    Clear All Filters
                                </Button>
                            </div>
                        )}
                    </form>
                </div>

                {/* Results Header */}
                <div className="results-header">
                    <div className="results-info">
                        <h2>
                            {searchQuery ? `Search Results` : 'All Techniques'}
                        </h2>
                        <p className="results-count">
                            {loading ? 'Loading...' : `${techniques.length} techniques found`}
                            {hasMore && ' (showing first results)'}
                        </p>
                    </div>

                    {/* View Toggle */}
                    <div className="view-controls">
                        <div className="view-toggle">
                            <button
                                onClick={() => setViewMode('grid')}
                                className={`view-btn ${viewMode === 'grid' ? 'active' : ''}`}
                                title="Grid View"
                            >
                                <Grid size={18} />
                            </button>
                            <button
                                onClick={() => setViewMode('list')}
                                className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
                                title="List View"
                            >
                                <List size={18} />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Error State */}
                {error && (
                    <div className="error-message">
                        <span>{error}</span>
                        <button
                            onClick={loadTechniques}
                            className="error-close"
                        >
                            <X size={16} />
                        </button>
                    </div>
                )}

                {/* Techniques Grid/List */}
                {techniques.length === 0 && !loading ? (
                    <div className="no-results">
                        <div className="no-results-content">
                            <BookOpen className="no-results-icon text-muted" size={64} />
                            <h3>No techniques found</h3>
                            <p>
                                {hasActiveFilters
                                    ? 'Try adjusting your search criteria or filters to find more techniques.'
                                    : 'The technique library is growing! Import some techniques to get started.'
                                }
                            </p>
                            {hasActiveFilters ? (
                                <Button onClick={clearFilters} variant="outline">
                                    Clear All Filters
                                </Button>
                            ) : user ? (
                                <Button onClick={handleImportFromBlackBeltWiki} disabled={importing}>
                                    {importing ? 'Importing...' : 'Import Techniques'}
                                </Button>
                            ) : (
                                <Button onClick={() => navigate('/login')}>
                                    Log In to Import Techniques
                                </Button>
                            )}
                        </div>
                    </div>
                ) : (
                    <>
                        <div className={viewMode === 'grid' ? 'techniques-grid' : 'techniques-list'}>
                            {techniques.map((technique) => (
                                <TechniqueCard
                                    key={technique.id}
                                    technique={technique}
                                    viewMode={viewMode}
                                    user={user}
                                    onClick={() => handleTechniqueClick(technique)}
                                    onBookmarkToggle={handleBookmarkToggle}
                                />
                            ))}
                        </div>

                        {/* Load More */}
                        {hasMore && (
                            <div className="load-more-section">
                                <Button
                                    onClick={() => setCurrentPage(currentPage + 1)}
                                    disabled={loading}
                                    variant="outline"
                                    size="lg"
                                >
                                    {loading ? (
                                        <>
                                            <Loader className="animate-spin" size={20} />
                                            Loading more...
                                        </>
                                    ) : (
                                        <>
                                            <Plus size={20} />
                                            Load More Techniques
                                        </>
                                    )}
                                </Button>
                            </div>
                        )}
                    </>
                )}

                {/* Call to Action */}
                {!user && techniques.length > 0 && (
                    <div className="cta-section">
                        <div className="cta-content">
                            <h3>Start Your Martial Arts Journey</h3>
                            <p>
                                Join DojoTracker to bookmark techniques, track your progress,
                                and build your personal training library.
                            </p>
                            <div className="cta-actions">
                                <Button onClick={() => navigate('/register')} size="lg">
                                    Get Started Free
                                </Button>
                                <Button onClick={() => navigate('/login')} variant="outline" size="lg">
                                    Sign In
                                </Button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

// Enhanced Technique Card Component
const TechniqueCard = ({ technique, viewMode, user, onClick, onBookmarkToggle }) => {
    const [bookmarkLoading, setBookmarkLoading] = useState(false);

    const getDifficultyColor = (level) => {
        if (!level) return 'bg-secondary';
        if (level <= 3) return 'bg-success';
        if (level <= 6) return 'bg-warning';
        return 'bg-error';
    };

    const getDifficultyText = (level) => {
        if (!level) return 'Unknown';
        if (level <= 3) return 'Beginner';
        if (level <= 6) return 'Intermediate';
        return 'Advanced';
    };

    const handleBookmark = async (e) => {
        e.stopPropagation();

        if (!user) {
            alert('Please log in to bookmark techniques');
            return;
        }

        try {
            setBookmarkLoading(true);
            await onBookmarkToggle(technique.id, technique.is_bookmarked);
        } catch (error) {
            console.error('Bookmark error:', error);
        } finally {
            setBookmarkLoading(false);
        }
    };

    if (viewMode === 'list') {
        return (
            <div
                className="technique-card list-view"
                onClick={onClick}
            >
                <div className="card-content">
                    <div className="technique-header">
                        <div className="technique-info">
                            <h3 className="technique-title">{technique.name}</h3>
                            <div className="technique-meta">
                                <span className="technique-style">{technique.style}</span>
                                {technique.category && (
                                    <span className="technique-category">{technique.category}</span>
                                )}
                                <span className={`difficulty-badge ${getDifficultyColor(technique.difficulty_level)}`}>
                                    {getDifficultyText(technique.difficulty_level)}
                                </span>
                            </div>
                        </div>

                        {user && (
                            <button
                                onClick={handleBookmark}
                                disabled={bookmarkLoading}
                                className={`bookmark-btn ${technique.is_bookmarked ? 'bookmarked' : ''}`}
                                title={technique.is_bookmarked ? 'Remove bookmark' : 'Add bookmark'}
                            >
                                <Star
                                    size={20}
                                    className={technique.is_bookmarked ? 'fill-current' : ''}
                                />
                            </button>
                        )}
                    </div>

                    {technique.description && (
                        <p className="technique-description">
                            {technique.description.length > 200
                                ? `${technique.description.substring(0, 200)}...`
                                : technique.description
                            }
                        </p>
                    )}

                    <div className="technique-stats">
                        <div className="stat-item">
                            <Eye size={16} />
                            <span>{technique.view_count || 0} views</span>
                        </div>
                        <div className="stat-item">
                            <Star size={16} />
                            <span>{technique.bookmark_count || 0} bookmarks</span>
                        </div>
                    </div>

                    {technique.tags && technique.tags.length > 0 && (
                        <div className="technique-tags">
                            {technique.tags.slice(0, 4).map((tag, index) => (
                                <span key={index} className="tag">
                                    #{tag}
                                </span>
                            ))}
                            {technique.tags.length > 4 && (
                                <span className="tag-more">
                                    +{technique.tags.length - 4} more
                                </span>
                            )}
                        </div>
                    )}
                </div>
            </div>
        );
    }

    // Grid view
    return (
        <div
            className="technique-card grid-view"
            onClick={onClick}
        >
            <div className="card-header">
                <div className="technique-badges">
                    <span className={`difficulty-badge ${getDifficultyColor(technique.difficulty_level)}`}>
                        {getDifficultyText(technique.difficulty_level)}
                    </span>
                    {user && (
                        <button
                            onClick={handleBookmark}
                            disabled={bookmarkLoading}
                            className={`bookmark-btn ${technique.is_bookmarked ? 'bookmarked' : ''}`}
                            title={technique.is_bookmarked ? 'Remove bookmark' : 'Add bookmark'}
                        >
                            <Star
                                size={18}
                                className={technique.is_bookmarked ? 'fill-current' : ''}
                            />
                        </button>
                    )}
                </div>
            </div>

            <div className="card-content">
                <h3 className="technique-title">{technique.name}</h3>

                <div className="technique-meta">
                    <span className="technique-style">{technique.style}</span>
                    {technique.category && (
                        <span className="technique-category">{technique.category}</span>
                    )}
                </div>

                {technique.description && (
                    <p className="technique-description">
                        {technique.description.length > 120
                            ? `${technique.description.substring(0, 120)}...`
                            : technique.description
                        }
                    </p>
                )}

                {technique.tags && technique.tags.length > 0 && (
                    <div className="technique-tags">
                        {technique.tags.slice(0, 3).map((tag, index) => (
                            <span key={index} className="tag">
                                #{tag}
                            </span>
                        ))}
                    </div>
                )}
            </div>

            <div className="card-footer">
                <div className="technique-stats">
                    <div className="stat-item">
                        <Eye size={14} />
                        <span>{technique.view_count || 0}</span>
                    </div>
                    <div className="stat-item">
                        <Star size={14} />
                        <span>{technique.bookmark_count || 0}</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Techniques;