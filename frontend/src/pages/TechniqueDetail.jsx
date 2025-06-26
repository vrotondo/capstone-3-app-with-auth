import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    ArrowLeft, Star, BookOpen, Eye, Clock, Target,
    Lightbulb, List, Users, Award, Plus, Edit3, Save, X
} from 'lucide-react';

const TechniqueDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [technique, setTechnique] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isBookmarked, setIsBookmarked] = useState(false);
    const [userBookmark, setUserBookmark] = useState(null);

    // Progress tracking
    const [masteryLevel, setMasteryLevel] = useState(1);
    const [personalNotes, setPersonalNotes] = useState('');
    const [isEditingNotes, setIsEditingNotes] = useState(false);
    const [isSaving, setIsSaving] = useState(false);

    // Check if user is authenticated
    const isAuthenticated = !!localStorage.getItem('token');

    useEffect(() => {
        loadTechnique();
    }, [id]);

    const loadTechnique = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem('token');
            const headers = {};

            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }

            const response = await fetch(`/api/techniques/${id}`, { headers });

            if (!response.ok) {
                throw new Error('Technique not found');
            }

            const data = await response.json();
            setTechnique(data.technique);

            // Set bookmark data if user is authenticated
            if (data.technique.user_bookmark) {
                setUserBookmark(data.technique.user_bookmark);
                setIsBookmarked(true);
                setMasteryLevel(data.technique.user_bookmark.mastery_level || 1);
                setPersonalNotes(data.technique.user_bookmark.personal_notes || '');
            } else {
                setIsBookmarked(data.technique.is_bookmarked || false);
            }
        } catch (error) {
            setError(error.message);
        } finally {
            setLoading(false);
        }
    };

    const handleBookmark = async () => {
        if (!isAuthenticated) {
            alert('Please log in to bookmark techniques');
            return;
        }

        try {
            const token = localStorage.getItem('token');
            const method = isBookmarked ? 'DELETE' : 'POST';
            const body = isBookmarked ? undefined : JSON.stringify({
                notes: personalNotes
            });

            const response = await fetch(`/api/techniques/${id}/bookmark`, {
                method,
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body
            });

            if (response.ok) {
                setIsBookmarked(!isBookmarked);
                if (!isBookmarked) {
                    // Just bookmarked - reload to get bookmark data
                    loadTechnique();
                } else {
                    // Unbookmarked - clear data
                    setUserBookmark(null);
                    setMasteryLevel(1);
                    setPersonalNotes('');
                }
            }
        } catch (error) {
            console.error('Bookmark error:', error);
        }
    };

    const updateProgress = async () => {
        if (!isAuthenticated || !isBookmarked) return;

        try {
            setIsSaving(true);
            const token = localStorage.getItem('token');

            const response = await fetch(`/api/techniques/${id}/progress`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    mastery_level: masteryLevel,
                    notes: personalNotes
                })
            });

            if (response.ok) {
                const data = await response.json();
                setUserBookmark(data.bookmark);
                setIsEditingNotes(false);
            }
        } catch (error) {
            console.error('Progress update error:', error);
        } finally {
            setIsSaving(false);
        }
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

    const getMasteryText = (level) => {
        if (level <= 2) return 'Learning';
        if (level <= 4) return 'Practicing';
        if (level <= 7) return 'Improving';
        return 'Mastered';
    };

    const getMasteryColor = (level) => {
        if (level <= 2) return 'text-red-600';
        if (level <= 4) return 'text-yellow-600';
        if (level <= 7) return 'text-blue-600';
        return 'text-green-600';
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">Loading technique...</p>
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
                        onClick={() => navigate('/techniques')}
                        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                        Back to Library
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <div className="bg-white shadow-sm border-b">
                <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                    <div className="flex items-center justify-between">
                        <button
                            onClick={() => navigate('/techniques')}
                            className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
                        >
                            <ArrowLeft className="h-5 w-5 mr-2" />
                            Back to Library
                        </button>

                        {isAuthenticated && (
                            <button
                                onClick={handleBookmark}
                                className={`flex items-center px-4 py-2 rounded-lg transition-colors ${isBookmarked
                                        ? 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'
                                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                    }`}
                            >
                                <Star className={`h-5 w-5 mr-2 ${isBookmarked ? 'fill-current' : ''}`} />
                                {isBookmarked ? 'Bookmarked' : 'Bookmark'}
                            </button>
                        )}
                    </div>
                </div>
            </div>

            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Technique Header */}
                <div className="bg-white rounded-lg shadow-sm p-8 mb-8">
                    <div className="flex items-start justify-between">
                        <div className="flex-1">
                            <h1 className="text-3xl font-bold text-gray-900 mb-4">
                                {technique.name}
                            </h1>

                            <div className="flex flex-wrap items-center gap-4 mb-6">
                                <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                                    {technique.style}
                                </span>

                                {technique.category && (
                                    <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
                                        {technique.category}
                                    </span>
                                )}

                                <span className={`px-3 py-1 text-white rounded-full text-sm font-medium ${getDifficultyColor(technique.difficulty_level)}`}>
                                    {getDifficultyText(technique.difficulty_level)}
                                    {technique.difficulty_level && ` (${technique.difficulty_level}/10)`}
                                </span>

                                {technique.belt_level && (
                                    <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm">
                                        {technique.belt_level}
                                    </span>
                                )}
                            </div>

                            <div className="flex items-center gap-6 text-sm text-gray-600">
                                <div className="flex items-center gap-1">
                                    <Eye className="h-4 w-4" />
                                    <span>{technique.view_count || 0} views</span>
                                </div>

                                <div className="flex items-center gap-1">
                                    <Star className="h-4 w-4" />
                                    <span>{technique.bookmark_count || 0} bookmarks</span>
                                </div>

                                {technique.last_updated && (
                                    <div className="flex items-center gap-1">
                                        <Clock className="h-4 w-4" />
                                        <span>Updated {new Date(technique.last_updated).toLocaleDateString()}</span>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Tags */}
                    {technique.tags && technique.tags.length > 0 && (
                        <div className="mt-6 flex flex-wrap gap-2">
                            {technique.tags.map((tag, index) => (
                                <span key={index} className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-sm">
                                    #{tag}
                                </span>
                            ))}
                        </div>
                    )}
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Main Content */}
                    <div className="lg:col-span-2 space-y-8">
                        {/* Description */}
                        {technique.description && (
                            <div className="bg-white rounded-lg shadow-sm p-6">
                                <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                                    <BookOpen className="h-5 w-5 mr-2 text-blue-600" />
                                    Description
                                </h2>
                                <div className="prose prose-sm max-w-none text-gray-700">
                                    {technique.description.split('\n').map((paragraph, index) => (
                                        <p key={index} className="mb-3">{paragraph}</p>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Instructions */}
                        {technique.instructions && (
                            <div className="bg-white rounded-lg shadow-sm p-6">
                                <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                                    <List className="h-5 w-5 mr-2 text-green-600" />
                                    Instructions
                                </h2>
                                <div className="prose prose-sm max-w-none text-gray-700">
                                    {technique.instructions.split('\n').map((instruction, index) => (
                                        <p key={index} className="mb-3">{instruction}</p>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Tips */}
                        {technique.tips && (
                            <div className="bg-white rounded-lg shadow-sm p-6">
                                <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                                    <Lightbulb className="h-5 w-5 mr-2 text-yellow-600" />
                                    Tips & Reminders
                                </h2>
                                <div className="prose prose-sm max-w-none text-gray-700">
                                    {technique.tips.split('\n').map((tip, index) => (
                                        <p key={index} className="mb-3">{tip}</p>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Variations */}
                        {technique.variations && (
                            <div className="bg-white rounded-lg shadow-sm p-6">
                                <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                                    <Target className="h-5 w-5 mr-2 text-purple-600" />
                                    Variations
                                </h2>
                                <div className="prose prose-sm max-w-none text-gray-700">
                                    {technique.variations.split('\n').map((variation, index) => (
                                        <p key={index} className="mb-2">{variation}</p>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Sidebar */}
                    <div className="space-y-6">
                        {/* Quick Info */}
                        <div className="bg-white rounded-lg shadow-sm p-6">
                            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Info</h3>
                            <div className="space-y-3">
                                <div>
                                    <span className="text-sm font-medium text-gray-500">Martial Art:</span>
                                    <div className="text-sm text-gray-900">{technique.style}</div>
                                </div>

                                {technique.category && (
                                    <div>
                                        <span className="text-sm font-medium text-gray-500">Category:</span>
                                        <div className="text-sm text-gray-900">{technique.category}</div>
                                    </div>
                                )}

                                <div>
                                    <span className="text-sm font-medium text-gray-500">Difficulty:</span>
                                    <div className="text-sm text-gray-900">
                                        {getDifficultyText(technique.difficulty_level)}
                                        {technique.difficulty_level && ` (${technique.difficulty_level}/10)`}
                                    </div>
                                </div>

                                {technique.belt_level && (
                                    <div>
                                        <span className="text-sm font-medium text-gray-500">Belt Level:</span>
                                        <div className="text-sm text-gray-900">{technique.belt_level}</div>
                                    </div>
                                )}

                                <div>
                                    <span className="text-sm font-medium text-gray-500">Source:</span>
                                    <div className="text-sm text-gray-900">{technique.source_site}</div>
                                </div>
                            </div>
                        </div>

                        {/* User Progress (if bookmarked) */}
                        {isAuthenticated && isBookmarked && (
                            <div className="bg-white rounded-lg shadow-sm p-6">
                                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                                    <Award className="h-5 w-5 mr-2 text-blue-600" />
                                    Your Progress
                                </h3>

                                <div className="space-y-4">
                                    {/* Mastery Level */}
                                    <div>
                                        <label className="text-sm font-medium text-gray-500 block mb-2">
                                            Mastery Level: {masteryLevel}/10
                                        </label>
                                        <div className="flex items-center gap-2 mb-2">
                                            <span className={`text-sm font-medium ${getMasteryColor(masteryLevel)}`}>
                                                {getMasteryText(masteryLevel)}
                                            </span>
                                        </div>
                                        <input
                                            type="range"
                                            min="1"
                                            max="10"
                                            value={masteryLevel}
                                            onChange={(e) => setMasteryLevel(parseInt(e.target.value))}
                                            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                                        />
                                        <div className="flex justify-between text-xs text-gray-500 mt-1">
                                            <span>Learning</span>
                                            <span>Mastered</span>
                                        </div>
                                    </div>

                                    {/* Personal Notes */}
                                    <div>
                                        <div className="flex items-center justify-between mb-2">
                                            <label className="text-sm font-medium text-gray-500">
                                                Personal Notes
                                            </label>
                                            {!isEditingNotes ? (
                                                <button
                                                    onClick={() => setIsEditingNotes(true)}
                                                    className="text-blue-600 hover:text-blue-700 text-sm flex items-center"
                                                >
                                                    <Edit3 className="h-4 w-4 mr-1" />
                                                    Edit
                                                </button>
                                            ) : (
                                                <div className="flex gap-2">
                                                    <button
                                                        onClick={updateProgress}
                                                        disabled={isSaving}
                                                        className="text-green-600 hover:text-green-700 text-sm flex items-center"
                                                    >
                                                        <Save className="h-4 w-4 mr-1" />
                                                        {isSaving ? 'Saving...' : 'Save'}
                                                    </button>
                                                    <button
                                                        onClick={() => {
                                                            setIsEditingNotes(false);
                                                            setPersonalNotes(userBookmark?.personal_notes || '');
                                                        }}
                                                        className="text-gray-600 hover:text-gray-700 text-sm flex items-center"
                                                    >
                                                        <X className="h-4 w-4 mr-1" />
                                                        Cancel
                                                    </button>
                                                </div>
                                            )}
                                        </div>

                                        {isEditingNotes ? (
                                            <textarea
                                                value={personalNotes}
                                                onChange={(e) => setPersonalNotes(e.target.value)}
                                                placeholder="Add your notes, tips, or observations..."
                                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                                                rows="4"
                                            />
                                        ) : (
                                            <div className="text-sm text-gray-700 bg-gray-50 rounded-lg p-3 min-h-[80px]">
                                                {personalNotes || (
                                                    <span className="text-gray-500 italic">
                                                        No notes yet. Click edit to add your thoughts!
                                                    </span>
                                                )}
                                            </div>
                                        )}
                                    </div>

                                    {/* Practice Stats */}
                                    {userBookmark && (
                                        <div className="pt-4 border-t border-gray-200">
                                            <div className="grid grid-cols-2 gap-4 text-center">
                                                <div>
                                                    <div className="text-lg font-semibold text-blue-600">
                                                        {userBookmark.practice_count || 0}
                                                    </div>
                                                    <div className="text-xs text-gray-500">Practice Sessions</div>
                                                </div>
                                                <div>
                                                    <div className="text-lg font-semibold text-green-600">
                                                        {userBookmark.last_practiced
                                                            ? new Date(userBookmark.last_practiced).toLocaleDateString()
                                                            : 'Never'
                                                        }
                                                    </div>
                                                    <div className="text-xs text-gray-500">Last Practiced</div>
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    {/* Quick Action Button */}
                                    <button
                                        onClick={updateProgress}
                                        disabled={isSaving}
                                        className="w-full mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center"
                                    >
                                        <Plus className="h-4 w-4 mr-2" />
                                        {isSaving ? 'Updating...' : 'Mark as Practiced'}
                                    </button>
                                </div>
                            </div>
                        )}

                        {/* Authentication prompt */}
                        {!isAuthenticated && (
                            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                                <h3 className="text-lg font-medium text-blue-900 mb-2">
                                    Track Your Progress
                                </h3>
                                <p className="text-sm text-blue-700 mb-4">
                                    Log in to bookmark techniques, track your progress, and add personal notes.
                                </p>
                                <button
                                    onClick={() => navigate('/login')}
                                    className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                                >
                                    Log In
                                </button>
                            </div>
                        )}

                        {/* Source Link */}
                        {technique.source_url && (
                            <div className="bg-white rounded-lg shadow-sm p-6">
                                <h3 className="text-lg font-semibold text-gray-900 mb-4">Source</h3>
                                <a
                                    href={technique.source_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-blue-600 hover:text-blue-700 text-sm underline"
                                >
                                    View Original Source
                                </a>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Custom styles for the range slider */}
            <style jsx>{`
        .slider::-webkit-slider-thumb {
          appearance: none;
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: #3B82F6;
          cursor: pointer;
          box-shadow: 0 0 2px rgba(0,0,0,.2);
        }
        
        .slider::-moz-range-thumb {
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: #3B82F6;
          cursor: pointer;
          border: none;
          box-shadow: 0 0 2px rgba(0,0,0,.2);
        }
      `}</style>
        </div>
    );
};

export default TechniqueDetail;