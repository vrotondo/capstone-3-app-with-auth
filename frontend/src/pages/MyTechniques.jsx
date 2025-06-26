import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Star, BookOpen, TrendingUp, Target, Clock,
    Edit3, Trash2, Plus, Award, BarChart3, Calendar
} from 'lucide-react';
import techniqueService from '../services/techniqueService';

const MyTechniques = () => {
    const navigate = useNavigate();
    const [bookmarks, setBookmarks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [sortBy, setSortBy] = useState('recent');
    const [filterBy, setFilterBy] = useState('all');

    // Stats
    const [stats, setStats] = useState({
        total: 0,
        learning: 0,
        practicing: 0,
        improving: 0,
        mastered: 0
    });

    useEffect(() => {
        if (!techniqueService.isAuthenticated()) {
            navigate('/login');
            return;
        }

        loadBookmarks();
    }, [navigate]);

    useEffect(() => {
        calculateStats();
    }, [bookmarks]);

    const loadBookmarks = async () => {
        try {
            setLoading(true);
            const data = await techniqueService.getUserBookmarks(100);
            setBookmarks(data.bookmarks || []);
        } catch (error) {
            setError(error.message);
        } finally {
            setLoading(false);
        }
    };

    const calculateStats = () => {
        const newStats = {
            total: bookmarks.length,
            learning: 0,
            practicing: 0,
            improving: 0,
            mastered: 0
        };

        bookmarks.forEach(bookmark => {
            const level = bookmark.mastery_level || 1;
            if (level <= 2) newStats.learning++;
            else if (level <= 4) newStats.practicing++;
            else if (level <= 7) newStats.improving++;
            else newStats.mastered++;
        });

        setStats(newStats);
    };

    const removeBookmark = async (techniqueId) => {
        if (!confirm('Are you sure you want to remove this bookmark?')) return;

        try {
            await techniqueService.removeBookmark(techniqueId);
            setBookmarks(bookmarks.filter(b => b.technique.id !== techniqueId));
        } catch (error) {
            alert('Failed to remove bookmark: ' + error.message);
        }
    };

    const updateProgress = async (techniqueId, masteryLevel) => {
        try {
            const data = await techniqueService.updateProgress(techniqueId, {
                mastery_level: masteryLevel
            });

            // Update local state
            setBookmarks(bookmarks.map(b =>
                b.technique.id === techniqueId
                    ? { ...b, ...data.bookmark }
                    : b
            ));
        } catch (error) {
            alert('Failed to update progress: ' + error.message);
        }
    };

    const getFilteredAndSortedBookmarks = () => {
        let filtered = [...bookmarks];

        // Filter by mastery level
        if (filterBy !== 'all') {
            filtered = filtered.filter(bookmark => {
                const level = bookmark.mastery_level || 1;
                switch (filterBy) {
                    case 'learning': return level <= 2;
                    case 'practicing': return level > 2 && level <= 4;
                    case 'improving': return level > 4 && level <= 7;
                    case 'mastered': return level > 7;
                    default: return true;
                }
            });
        }

        // Sort
        switch (sortBy) {
            case 'name':
                return filtered.sort((a, b) => a.technique.name.localeCompare(b.technique.name));

            case 'mastery':
                return filtered.sort((a, b) => (b.mastery_level || 1) - (a.mastery_level || 1));

            case 'practice':
                return filtered.sort((a, b) => (b.practice_count || 0) - (a.practice_count || 0));

            case 'recent':
            default:
                return filtered.sort((a, b) => {
                    const dateA = new Date(a.updated_at || a.bookmarked_at);
                    const dateB = new Date(b.updated_at || b.bookmarked_at);
                    return dateB - dateA;
                });
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">Loading your techniques...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="text-red-500 text-lg font-medium">{error}</div>
                    <button
                        onClick={loadBookmarks}
                        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                        Try Again
                    </button>
                </div>
            </div>
        );
    }

    const filteredBookmarks = getFilteredAndSortedBookmarks();

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <div className="bg-white shadow-sm border-b">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900 flex items-center">
                                <Star className="mr-3 h-8 w-8 text-yellow-500 fill-current" />
                                My Techniques
                            </h1>
                            <p className="mt-2 text-gray-600">
                                Track your progress and practice your bookmarked techniques
                            </p>
                        </div>

                        <button
                            onClick={() => navigate('/techniques')}
                            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                        >
                            <Plus className="h-5 w-5 mr-2" />
                            Browse Library
                        </button>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {bookmarks.length === 0 ? (
                    // Empty state
                    <div className="text-center py-12">
                        <BookOpen className="mx-auto h-12 w-12 text-gray-400" />
                        <h3 className="mt-2 text-lg font-medium text-gray-900">No techniques bookmarked yet</h3>
                        <p className="mt-1 text-gray-500 mb-6">
                            Start building your personal technique collection by bookmarking techniques from the library
                        </p>
                        <button
                            onClick={() => navigate('/techniques')}
                            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                        >
                            Explore Technique Library
                        </button>
                    </div>
                ) : (
                    <>
                        {/* Stats Cards */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
                            <div className="bg-white rounded-lg shadow-sm p-6 border-l-4 border-blue-500">
                                <div className="flex items-center">
                                    <BookOpen className="h-8 w-8 text-blue-500" />
                                    <div className="ml-3">
                                        <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
                                        <div className="text-sm text-gray-500">Total Techniques</div>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-white rounded-lg shadow-sm p-6 border-l-4 border-red-500">
                                <div className="flex items-center">
                                    <Target className="h-8 w-8 text-red-500" />
                                    <div className="ml-3">
                                        <div className="text-2xl font-bold text-gray-900">{stats.learning}</div>
                                        <div className="text-sm text-gray-500">Learning</div>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-white rounded-lg shadow-sm p-6 border-l-4 border-yellow-500">
                                <div className="flex items-center">
                                    <Clock className="h-8 w-8 text-yellow-500" />
                                    <div className="ml-3">
                                        <div className="text-2xl font-bold text-gray-900">{stats.practicing}</div>
                                        <div className="text-sm text-gray-500">Practicing</div>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-white rounded-lg shadow-sm p-6 border-l-4 border-blue-500">
                                <div className="flex items-center">
                                    <TrendingUp className="h-8 w-8 text-blue-500" />
                                    <div className="ml-3">
                                        <div className="text-2xl font-bold text-gray-900">{stats.improving}</div>
                                        <div className="text-sm text-gray-500">Improving</div>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-white rounded-lg shadow-sm p-6 border-l-4 border-green-500">
                                <div className="flex items-center">
                                    <Award className="h-8 w-8 text-green-500" />
                                    <div className="ml-3">
                                        <div className="text-2xl font-bold text-gray-900">{stats.mastered}</div>
                                        <div className="text-sm text-gray-500">Mastered</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Filters and Sorting */}
                        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
                            <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
                                <div className="flex flex-wrap gap-4">
                                    <select
                                        value={filterBy}
                                        onChange={(e) => setFilterBy(e.target.value)}
                                        className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                    >
                                        <option value="all">All Techniques</option>
                                        <option value="learning">Learning (1-2)</option>
                                        <option value="practicing">Practicing (3-4)</option>
                                        <option value="improving">Improving (5-7)</option>
                                        <option value="mastered">Mastered (8-10)</option>
                                    </select>

                                    <select
                                        value={sortBy}
                                        onChange={(e) => setSortBy(e.target.value)}
                                        className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                    >
                                        <option value="recent">Most Recent</option>
                                        <option value="name">Name A-Z</option>
                                        <option value="mastery">Highest Mastery</option>
                                        <option value="practice">Most Practiced</option>
                                    </select>
                                </div>

                                <div className="text-sm text-gray-600">
                                    Showing {filteredBookmarks.length} of {bookmarks.length} techniques
                                </div>
                            </div>
                        </div>

                        {/* Techniques List */}
                        <div className="space-y-6">
                            {filteredBookmarks.map((bookmark) => (
                                <TechniqueCard
                                    key={bookmark.id}
                                    bookmark={bookmark}
                                    onRemove={removeBookmark}
                                    onUpdateProgress={updateProgress}
                                    onViewDetail={(id) => navigate(`/techniques/${id}`)}
                                />
                            ))}
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

// Individual Technique Card Component
const TechniqueCard = ({ bookmark, onRemove, onUpdateProgress, onViewDetail }) => {
    const [isExpanded, setIsExpanded] = useState(false);
    const [newMasteryLevel, setNewMasteryLevel] = useState(bookmark.mastery_level || 1);

    const technique = bookmark.technique;
    const masteryLevel = bookmark.mastery_level || 1;

    const getMasteryText = (level) => {
        if (level <= 2) return 'Learning';
        if (level <= 4) return 'Practicing';
        if (level <= 7) return 'Improving';
        return 'Mastered';
    };

    const getMasteryColor = (level) => {
        if (level <= 2) return 'text-red-600 bg-red-50';
        if (level <= 4) return 'text-yellow-600 bg-yellow-50';
        if (level <= 7) return 'text-blue-600 bg-blue-50';
        return 'text-green-600 bg-green-50';
    };

    const getDifficultyColor = (level) => {
        if (!level) return 'bg-gray-500';
        if (level <= 3) return 'bg-green-500';
        if (level <= 6) return 'bg-yellow-500';
        return 'bg-red-500';
    };

    const handleMasteryChange = (newLevel) => {
        setNewMasteryLevel(newLevel);
        onUpdateProgress(technique.id, newLevel);
    };

    return (
        <div className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow">
            <div className="p-6">
                {/* Header */}
                <div className="flex items-start justify-between">
                    <div className="flex-1">
                        <div className="flex items-center gap-3 mb-3">
                            <h3
                                className="text-xl font-semibold text-gray-900 hover:text-blue-600 cursor-pointer"
                                onClick={() => onViewDetail(technique.id)}
                            >
                                {technique.name}
                            </h3>

                            <span className={`px-2 py-1 text-xs font-medium text-white rounded-full ${getDifficultyColor(technique.difficulty_level)}`}>
                                {technique.difficulty_level ? `Level ${technique.difficulty_level}` : 'Unknown'}
                            </span>
                        </div>

                        <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
                            <span className="font-medium text-blue-600">{technique.style}</span>
                            {technique.category && (
                                <span className="text-gray-500">• {technique.category}</span>
                            )}
                            <span className="text-gray-500">
                                • Bookmarked {techniqueService.formatDate(bookmark.bookmarked_at)}
                            </span>
                        </div>

                        {/* Progress Section */}
                        <div className="flex items-center gap-6 mb-4">
                            <div className="flex items-center gap-2">
                                <span className="text-sm font-medium text-gray-700">Progress:</span>
                                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getMasteryColor(masteryLevel)}`}>
                                    {getMasteryText(masteryLevel)} ({masteryLevel}/10)
                                </span>
                            </div>

                            <div className="flex items-center gap-2 text-sm text-gray-600">
                                <BarChart3 className="h-4 w-4" />
                                <span>{bookmark.practice_count || 0} sessions</span>
                            </div>

                            {bookmark.last_practiced && (
                                <div className="flex items-center gap-2 text-sm text-gray-600">
                                    <Calendar className="h-4 w-4" />
                                    <span>Last: {techniqueService.formatDate(bookmark.last_practiced)}</span>
                                </div>
                            )}
                        </div>

                        {/* Mastery Level Slider */}
                        <div className="mb-4">
                            <div className="flex items-center justify-between mb-2">
                                <label className="text-sm font-medium text-gray-700">
                                    Update Mastery Level:
                                </label>
                                <span className="text-sm text-gray-600">{newMasteryLevel}/10</span>
                            </div>
                            <input
                                type="range"
                                min="1"
                                max="10"
                                value={newMasteryLevel}
                                onChange={(e) => {
                                    const level = parseInt(e.target.value);
                                    setNewMasteryLevel(level);
                                    handleMasteryChange(level);
                                }}
                                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                            />
                            <div className="flex justify-between text-xs text-gray-500 mt-1">
                                <span>Learning</span>
                                <span>Practicing</span>
                                <span>Improving</span>
                                <span>Mastered</span>
                            </div>
                        </div>

                        {/* Personal Notes */}
                        {bookmark.personal_notes && (
                            <div className="bg-gray-50 rounded-lg p-3 mb-4">
                                <div className="text-sm font-medium text-gray-700 mb-1">Personal Notes:</div>
                                <div className="text-sm text-gray-600">{bookmark.personal_notes}</div>
                            </div>
                        )}

                        {/* Description Preview */}
                        {technique.description && (
                            <div className="mb-4">
                                <p className="text-sm text-gray-600 line-clamp-2">
                                    {isExpanded
                                        ? technique.description
                                        : techniqueService.truncateText(technique.description, 200)
                                    }
                                </p>
                                {technique.description.length > 200 && (
                                    <button
                                        onClick={() => setIsExpanded(!isExpanded)}
                                        className="text-blue-600 hover:text-blue-700 text-sm font-medium mt-1"
                                    >
                                        {isExpanded ? 'Show less' : 'Show more'}
                                    </button>
                                )}
                            </div>
                        )}

                        {/* Tags */}
                        {technique.tags && technique.tags.length > 0 && (
                            <div className="flex flex-wrap gap-1 mb-4">
                                {technique.tags.slice(0, 5).map((tag, index) => (
                                    <span key={index} className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">
                                        #{tag}
                                    </span>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Actions */}
                    <div className="flex flex-col gap-2 ml-4">
                        <button
                            onClick={() => onViewDetail(technique.id)}
                            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                            title="View Details"
                        >
                            <BookOpen className="h-5 w-5" />
                        </button>

                        <button
                            onClick={() => onRemove(technique.id)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="Remove Bookmark"
                        >
                            <Trash2 className="h-5 w-5" />
                        </button>
                    </div>
                </div>
            </div>

            {/* Progress Bar */}
            <div className="px-6 pb-4">
                <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${(masteryLevel / 10) * 100}%` }}
                    ></div>
                </div>
            </div>
        </div>
    );
};

export default MyTechniques;