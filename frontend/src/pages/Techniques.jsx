import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
    Search, Filter, Star, BookOpen, Eye, TrendingUp,
    ChevronLeft, ChevronRight, Plus, Download, Upload,
    Grid, List, SortAsc, X, Loader
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
    const [viewMode, setViewMode] = useState('grid'); // grid or list

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
        // Search will be triggered by useEffect when searchQuery changes
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
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">Loading technique library...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <div className="bg-white shadow-sm border-b">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900 flex items-center">
                                <BookOpen className="mr-3 h-8 w-8 text-blue-600" />
                                Technique Library
                            </h1>
                            <p className="mt-2 text-gray-600">
                                Discover and master martial arts techniques from around the world
                            </p>
                        </div>

                        <div className="flex items-center gap-4">
                            {/* Stats */}
                            <div className="hidden lg:flex space-x-6">
                                <div className="text-center">
                                    <div className="text-2xl font-bold text-blue-600">{stats.total_techniques || 0}</div>
                                    <div className="text-sm text-gray-500">Techniques</div>
                                </div>
                                <div className="text-center">
                                    <div className="text-2xl font-bold text-green-600">{stats.total_styles || 0}</div>
                                    <div className="text-sm text-gray-500">Styles</div>
                                </div>
                                <div className="text-center">
                                    <div className="text-2xl font-bold text-purple-600">{stats.total_categories || 0}</div>
                                    <div className="text-sm text-gray-500">Categories</div>
                                </div>
                            </div>

                            {/* Action Buttons */}
                            <div className="flex gap-2">
                                {user && (
                                    <>
                                        <Button
                                            variant="outline"
                                            size="sm"
                                            onClick={() => navigate('/my-techniques')}
                                        >
                                            <Star className="h-4 w-4 mr-2" />
                                            My Techniques
                                        </Button>

                                        <Button
                                            variant="primary"
                                            size="sm"
                                            onClick={handleImportFromBlackBeltWiki}
                                            disabled={importing}
                                        >
                                            {importing ? (
                                                <Loader className="h-4 w-4 mr-2 animate-spin" />
                                            ) : (
                                                <Download className="h-4 w-4 mr-2" />
                                            )}
                                            {importing ? 'Importing...' : 'Import from Wiki'}
                                        </Button>
                                    </>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Search and Filters */}
                <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
                    <form onSubmit={handleSearch} className="flex flex-col lg:flex-row gap-4">
                        {/* Search */}
                        <div className="flex-1">
                            <div className="relative">
                                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                                <input
                                    type="text"
                                    placeholder="Search techniques, styles, or categories..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                />
                                {searchQuery && (
                                    <button
                                        type="button"
                                        onClick={() => setSearchQuery('')}
                                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                                    >
                                        <X className="h-4 w-4" />
                                    </button>
                                )}
                            </div>
                        </div>

                        {/* Filters */}
                        <div className="flex flex-wrap gap-4">
                            <select
                                value={selectedStyle}
                                onChange={(e) => setSelectedStyle(e.target.value)}
                                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="">All Styles</option>
                                {styles.map(style => (
                                    <option key={style} value={style}>{style}</option>
                                ))}
                            </select>

                            <select
                                value={selectedCategory}
                                onChange={(e) => setSelectedCategory(e.target.value)}
                                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="">All Categories</option>
                                {categories.map(category => (
                                    <option key={category} value={category}>{category}</option>
                                ))}
                            </select>

                            <select
                                value={selectedDifficulty}
                                onChange={(e) => setSelectedDifficulty(e.target.value)}
                                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="">All Levels</option>
                                <option value="1">Beginner (1-3)</option>
                                <option value="4">Intermediate (4-6)</option>
                                <option value="7">Advanced (7-10)</option>
                            </select>

                            <select
                                value={sortBy}
                                onChange={(e) => setSortBy(e.target.value)}
                                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="name">Sort by Name</option>
                                <option value="difficulty">Sort by Difficulty</option>
                                <option value="popular">Sort by Popularity</option>
                                <option value="style">Sort by Style</option>
                                <option value="recent">Sort by Recent</option>
                            </select>
                        </div>
                    </form>

                    {/* Active filters and results */}
                    <div className="mt-4 flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <p className="text-sm text-gray-600">
                                Showing {techniques.length} techniques
                                {hasMore && ' (loading more available)'}
                            </p>

                            {hasActiveFilters && (
                                <button
                                    onClick={clearFilters}
                                    className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center"
                                >
                                    <X className="h-4 w-4 mr-1" />
                                    Clear Filters
                                </button>
                            )}
                        </div>

                        {/* View mode toggle */}
                        <div className="flex rounded-lg border border-gray-300">
                            <button
                                onClick={() => setViewMode('grid')}
                                className={`px-3 py-1 text-sm rounded-l-lg transition-colors ${viewMode === 'grid'
                                        ? 'bg-blue-600 text-white'
                                        : 'bg-white text-gray-700 hover:bg-gray-50'
                                    }`}
                            >
                                <Grid className="h-4 w-4" />
                            </button>
                            <button
                                onClick={() => setViewMode('list')}
                                className={`px-3 py-1 text-sm rounded-r-lg transition-colors ${viewMode === 'list'
                                        ? 'bg-blue-600 text-white'
                                        : 'bg-white text-gray-700 hover:bg-gray-50'
                                    }`}
                            >
                                <List className="h-4 w-4" />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Error State */}
                {error && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
                        <div className="flex items-center">
                            <div className="text-red-800">
                                <strong>Error:</strong> {error}
                            </div>
                            <button
                                onClick={loadTechniques}
                                className="ml-auto px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm"
                            >
                                Try Again
                            </button>
                        </div>
                    </div>
                )}

                {/* Techniques Grid/List */}
                {techniques.length === 0 && !loading ? (
                    <div className="text-center py-12">
                        <BookOpen className="mx-auto h-12 w-12 text-gray-400" />
                        <h3 className="mt-2 text-lg font-medium text-gray-900">No techniques found</h3>
                        <p className="mt-1 text-gray-500 mb-6">
                            {hasActiveFilters
                                ? 'Try adjusting your search or filters'
                                : 'The technique library is being built. Import some techniques to get started!'
                            }
                        </p>
                        {hasActiveFilters ? (
                            <Button onClick={clearFilters}>
                                Clear Filters
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
                ) : (
                    <>
                        <div className={viewMode === 'grid'
                            ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                            : "space-y-4"
                        }>
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
                            <div className="mt-8 text-center">
                                <Button
                                    onClick={() => setCurrentPage(currentPage + 1)}
                                    disabled={loading}
                                    variant="outline"
                                >
                                    {loading ? (
                                        <>
                                            <Loader className="h-4 w-4 mr-2 animate-spin" />
                                            Loading...
                                        </>
                                    ) : (
                                        <>
                                            <Plus className="h-4 w-4 mr-2" />
                                            Load More Techniques
                                        </>
                                    )}
                                </Button>
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
};

// Individual Technique Card Component
const TechniqueCard = ({ technique, viewMode, user, onClick, onBookmarkToggle }) => {
    const [bookmarkLoading, setBookmarkLoading] = useState(false);

    const getDifficultyColor = (level) => {
        if (!level) return 'bg-gray-500';
        if (level <= 3) return 'bg-green-500';
        if (level <= 6) return 'bg-yellow-500';
        return 'bg-red-500';
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
                className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow cursor-pointer"
                onClick={onClick}
            >
                <div className="p-6">
                    <div className="flex items-start justify-between">
                        <div className="flex-1">
                            <div className="flex items-center gap-3">
                                <h3 className="text-lg font-semibold text-gray-900 hover:text-blue-600">
                                    {technique.name}
                                </h3>
                                <span className={`px-2 py-1 text-xs font-medium text-white rounded-full ${getDifficultyColor(technique.difficulty_level)}`}>
                                    {getDifficultyText(technique.difficulty_level)}
                                </span>
                            </div>

                            <div className="mt-2 flex items-center gap-4 text-sm text-gray-600">
                                <span className="font-medium text-blue-600">{technique.style}</span>
                                {technique.category && (
                                    <span className="text-gray-500">• {technique.category}</span>
                                )}
                                <div className="flex items-center gap-1">
                                    <Eye className="h-4 w-4" />
                                    <span>{technique.view_count || 0}</span>
                                </div>
                            </div>

                            {technique.description && (
                                <p className="mt-3 text-gray-600 line-clamp-2">
                                    {technique.description.length > 150
                                        ? `${technique.description.substring(0, 150)}...`
                                        : technique.description
                                    }
                                </p>
                            )}

                            {technique.tags && technique.tags.length > 0 && (
                                <div className="mt-3 flex flex-wrap gap-1">
                                    {technique.tags.slice(0, 4).map((tag, index) => (
                                        <span key={index} className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">
                                            #{tag}
                                        </span>
                                    ))}
                                </div>
                            )}
                        </div>

                        {user && (
                            <button
                                onClick={handleBookmark}
                                disabled={bookmarkLoading}
                                className={`ml-4 p-2 rounded-full transition-colors ${technique.is_bookmarked
                                        ? 'text-yellow-500 hover:text-yellow-600'
                                        : 'text-gray-400 hover:text-yellow-500'
                                    } ${bookmarkLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                            >
                                <Star className={`h-5 w-5 ${technique.is_bookmarked ? 'fill-current' : ''}`} />
                            </button>
                        )}
                    </div>
                </div>
            </div>
        );
    }

    // Grid view
    return (
        <div
            className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow cursor-pointer group"
            onClick={onClick}
        >
            <div className="p-6">
                <div className="flex items-start justify-between">
                    <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                            {technique.name}
                        </h3>
                        <div className="mt-2 flex items-center justify-between">
                            <span className="text-sm font-medium text-blue-600">{technique.style}</span>
                            <span className={`px-2 py-1 text-xs font-medium text-white rounded-full ${getDifficultyColor(technique.difficulty_level)}`}>
                                {getDifficultyText(technique.difficulty_level)}
                            </span>
                        </div>
                    </div>

                    {user && (
                        <button
                            onClick={handleBookmark}
                            disabled={bookmarkLoading}
                            className={`ml-2 p-1 rounded-full transition-colors ${technique.is_bookmarked
                                    ? 'text-yellow-500 hover:text-yellow-600'
                                    : 'text-gray-400 hover:text-yellow-500'
                                } ${bookmarkLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                        >
                            <Star className={`h-4 w-4 ${technique.is_bookmarked ? 'fill-current' : ''}`} />
                        </button>
                    )}
                </div>

                {technique.category && (
                    <div className="mt-3 text-sm text-gray-600">
                        Category: {technique.category}
                    </div>
                )}

                {technique.description && (
                    <p className="mt-3 text-sm text-gray-600 line-clamp-3">
                        {technique.description.length > 120
                            ? `${technique.description.substring(0, 120)}...`
                            : technique.description
                        }
                    </p>
                )}

                <div className="mt-4 flex items-center justify-between text-sm text-gray-500">
                    <div className="flex items-center gap-1">
                        <Eye className="h-4 w-4" />
                        <span>{technique.view_count || 0} views</span>
                    </div>

                    {technique.tags && technique.tags.length > 0 && (
                        <div className="flex gap-1">
                            {technique.tags.slice(0, 2).map((tag, index) => (
                                <span key={index} className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">
                                    #{tag}
                                </span>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Techniques;