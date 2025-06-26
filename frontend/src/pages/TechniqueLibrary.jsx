import React, { useState, useEffect } from 'react';
import { Search, Filter, Star, BookOpen, Eye, TrendingUp } from 'lucide-react';

const TechniqueLibrary = () => {
    const [techniques, setTechniques] = useState([]);
    const [filteredTechniques, setFilteredTechniques] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedStyle, setSelectedStyle] = useState('');
    const [selectedCategory, setSelectedCategory] = useState('');
    const [selectedDifficulty, setSelectedDifficulty] = useState('');
    const [sortBy, setSortBy] = useState('name');

    // Filter options
    const [styles, setStyles] = useState([]);
    const [categories, setCategories] = useState([]);
    const [stats, setStats] = useState({});

    // View mode
    const [viewMode, setViewMode] = useState('grid'); // grid or list

    useEffect(() => {
        loadTechniques();
        loadFilterOptions();
        loadStats();
    }, []);

    useEffect(() => {
        filterTechniques();
    }, [techniques, searchQuery, selectedStyle, selectedCategory, selectedDifficulty, sortBy]);

    const loadTechniques = async () => {
        try {
            const response = await fetch('/api/techniques/search?limit=100');
            const data = await response.json();
            setTechniques(data.techniques || []);
        } catch (error) {
            console.error('Error loading techniques:', error);
        } finally {
            setLoading(false);
        }
    };

    const loadFilterOptions = async () => {
        try {
            const [stylesRes, categoriesRes] = await Promise.all([
                fetch('/api/techniques/styles'),
                fetch('/api/techniques/categories')
            ]);

            const stylesData = await stylesRes.json();
            const categoriesData = await categoriesRes.json();

            setStyles(stylesData.styles || []);
            setCategories(categoriesData.categories || []);
        } catch (error) {
            console.error('Error loading filter options:', error);
        }
    };

    const loadStats = async () => {
        try {
            const response = await fetch('/api/techniques/stats');
            const data = await response.json();
            setStats(data.stats || {});
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    };

    const filterTechniques = () => {
        let filtered = [...techniques];

        // Search filter
        if (searchQuery) {
            const query = searchQuery.toLowerCase();
            filtered = filtered.filter(technique =>
                technique.name.toLowerCase().includes(query) ||
                technique.description?.toLowerCase().includes(query) ||
                technique.style?.toLowerCase().includes(query) ||
                technique.tags?.some(tag => tag.toLowerCase().includes(query))
            );
        }

        // Style filter
        if (selectedStyle) {
            filtered = filtered.filter(technique =>
                technique.style?.toLowerCase() === selectedStyle.toLowerCase()
            );
        }

        // Category filter
        if (selectedCategory) {
            filtered = filtered.filter(technique =>
                technique.category?.toLowerCase() === selectedCategory.toLowerCase()
            );
        }

        // Difficulty filter
        if (selectedDifficulty) {
            const difficulty = parseInt(selectedDifficulty);
            filtered = filtered.filter(technique =>
                technique.difficulty_level === difficulty
            );
        }

        // Sort
        filtered.sort((a, b) => {
            switch (sortBy) {
                case 'name':
                    return a.name.localeCompare(b.name);
                case 'difficulty':
                    return (a.difficulty_level || 5) - (b.difficulty_level || 5);
                case 'popular':
                    return (b.view_count || 0) - (a.view_count || 0);
                case 'style':
                    return (a.style || '').localeCompare(b.style || '');
                default:
                    return 0;
            }
        });

        setFilteredTechniques(filtered);
    };

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

    if (loading) {
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

                        {/* Stats */}
                        <div className="hidden md:flex space-x-6">
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
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Search and Filters */}
                <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
                    <div className="flex flex-col lg:flex-row gap-4">
                        {/* Search */}
                        <div className="flex-1">
                            <div className="relative">
                                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                                <input
                                    type="text"
                                    placeholder="Search techniques..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                />
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
                            </select>
                        </div>
                    </div>

                    {/* Results count */}
                    <div className="mt-4 flex items-center justify-between">
                        <p className="text-sm text-gray-600">
                            Showing {filteredTechniques.length} of {techniques.length} techniques
                        </p>

                        {/* View mode toggle */}
                        <div className="flex rounded-lg border border-gray-300">
                            <button
                                onClick={() => setViewMode('grid')}
                                className={`px-3 py-1 text-sm rounded-l-lg ${viewMode === 'grid'
                                        ? 'bg-blue-600 text-white'
                                        : 'bg-white text-gray-700 hover:bg-gray-50'
                                    }`}
                            >
                                Grid
                            </button>
                            <button
                                onClick={() => setViewMode('list')}
                                className={`px-3 py-1 text-sm rounded-r-lg ${viewMode === 'list'
                                        ? 'bg-blue-600 text-white'
                                        : 'bg-white text-gray-700 hover:bg-gray-50'
                                    }`}
                            >
                                List
                            </button>
                        </div>
                    </div>
                </div>

                {/* Techniques Grid/List */}
                {filteredTechniques.length === 0 ? (
                    <div className="text-center py-12">
                        <BookOpen className="mx-auto h-12 w-12 text-gray-400" />
                        <h3 className="mt-2 text-lg font-medium text-gray-900">No techniques found</h3>
                        <p className="mt-1 text-gray-500">Try adjusting your search or filters</p>
                    </div>
                ) : (
                    <div className={viewMode === 'grid'
                        ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                        : "space-y-4"
                    }>
                        {filteredTechniques.map((technique) => (
                            <TechniqueCard
                                key={technique.id}
                                technique={technique}
                                viewMode={viewMode}
                                getDifficultyColor={getDifficultyColor}
                                getDifficultyText={getDifficultyText}
                            />
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

// Technique Card Component
const TechniqueCard = ({ technique, viewMode, getDifficultyColor, getDifficultyText }) => {
    const [isBookmarked, setIsBookmarked] = useState(false);

    const handleBookmark = async (e) => {
        e.stopPropagation();
        // TODO: Implement bookmarking (requires authentication)
        setIsBookmarked(!isBookmarked);
    };

    const handleTechniqueClick = () => {
        // TODO: Navigate to technique detail page
        console.log('View technique:', technique.id);
    };

    if (viewMode === 'list') {
        return (
            <div
                className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow cursor-pointer"
                onClick={handleTechniqueClick}
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
                                    {technique.description}
                                </p>
                            )}

                            {technique.tags && technique.tags.length > 0 && (
                                <div className="mt-3 flex flex-wrap gap-1">
                                    {technique.tags.slice(0, 4).map((tag, index) => (
                                        <span key={index} className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">
                                            {tag}
                                        </span>
                                    ))}
                                </div>
                            )}
                        </div>

                        <button
                            onClick={handleBookmark}
                            className={`ml-4 p-2 rounded-full transition-colors ${isBookmarked
                                    ? 'text-yellow-500 hover:text-yellow-600'
                                    : 'text-gray-400 hover:text-yellow-500'
                                }`}
                        >
                            <Star className={`h-5 w-5 ${isBookmarked ? 'fill-current' : ''}`} />
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    // Grid view
    return (
        <div
            className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow cursor-pointer group"
            onClick={handleTechniqueClick}
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

                    <button
                        onClick={handleBookmark}
                        className={`ml-2 p-1 rounded-full transition-colors ${isBookmarked
                                ? 'text-yellow-500 hover:text-yellow-600'
                                : 'text-gray-400 hover:text-yellow-500'
                            }`}
                    >
                        <Star className={`h-4 w-4 ${isBookmarked ? 'fill-current' : ''}`} />
                    </button>
                </div>

                {technique.category && (
                    <div className="mt-3 text-sm text-gray-600">
                        Category: {technique.category}
                    </div>
                )}

                {technique.description && (
                    <p className="mt-3 text-sm text-gray-600 line-clamp-3">
                        {technique.description}
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
                                    {tag}
                                </span>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default TechniqueLibrary;