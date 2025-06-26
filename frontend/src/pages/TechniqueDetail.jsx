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
        if (!level) return 'difficulty-unknown';
        if (level <= 3) return 'difficulty-beginner';
        if (level <= 6) return 'difficulty-intermediate';
        return 'difficulty-advanced';
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
        if (level <= 2) return 'mastery-learning';
        if (level <= 4) return 'mastery-practicing';
        if (level <= 7) return 'mastery-improving';
        return 'mastery-mastered';
    };

    if (loading) {
        return (
            <div className="technique-detail-page">
                <div className="loading-container">
                    <div className="spinner spinner-md"></div>
                    <p>Loading technique details...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="technique-detail-page">
                <div className="techniques-empty-state">
                    <div className="empty-icon">⚠️</div>
                    <h3 className="empty-title">Technique Not Found</h3>
                    <p className="empty-subtitle">{error}</p>
                    <button
                        onClick={() => navigate('/techniques')}
                        className="get-started-btn"
                    >
                        Back to Library
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="technique-detail-page">
            {/* Enhanced Header */}
            <div className="technique-detail-header">
                <h1 className="technique-title">{technique.name}</h1>

                <div className="technique-meta">
                    <span className="meta-badge style-badge">{technique.style}</span>
                    {technique.difficulty_level && (
                        <span className={`meta-badge difficulty-badge ${getDifficultyColor(technique.difficulty_level)}`}>
                            {getDifficultyText(technique.difficulty_level)} ({technique.difficulty_level}/10)
                        </span>
                    )}
                    {technique.category && (
                        <span className="meta-badge category-badge">{technique.category}</span>
                    )}
                    {technique.belt_level && (
                        <span className="meta-badge source-badge">{technique.belt_level}</span>
                    )}
                    <span className="meta-badge source-badge">{technique.source_site || 'BlackBeltWiki'}</span>
                </div>

                {/* Stats Row */}
                <div className="technique-stats-row">
                    <div className="stat-item">
                        <Eye size={16} />
                        <span>{technique.view_count || 0} views</span>
                    </div>
                    <div className="stat-item">
                        <Star size={16} />
                        <span>{technique.bookmark_count || 0} bookmarks</span>
                    </div>
                    {technique.last_updated && (
                        <div className="stat-item">
                            <Clock size={16} />
                            <span>Updated {new Date(technique.last_updated).toLocaleDateString()}</span>
                        </div>
                    )}
                </div>

                {/* Tags */}
                {technique.tags && technique.tags.length > 0 && (
                    <div className="tags-container">
                        {technique.tags.map((tag, index) => (
                            <span key={index} className="tag">
                                #{tag}
                            </span>
                        ))}
                    </div>
                )}

                <div className="technique-actions">
                    <button onClick={() => navigate('/techniques')} className="action-btn back-btn">
                        <ArrowLeft size={20} />
                        Back to Library
                    </button>

                    {isAuthenticated && (
                        <button
                            onClick={handleBookmark}
                            className={`action-btn bookmark-btn ${isBookmarked ? 'bookmarked' : ''}`}
                        >
                            <Star size={20} fill={isBookmarked ? 'currentColor' : 'none'} />
                            {isBookmarked ? 'Bookmarked' : 'Bookmark'}
                        </button>
                    )}
                </div>
            </div>

            {/* Main Content */}
            <div className="technique-content">
                {/* Left Column - Main Content */}
                <div className="content-main">
                    {/* Description */}
                    {technique.description && (
                        <div className="content-section">
                            <h2 className="section-title description">Description</h2>
                            <div className="content-text">
                                {technique.description.split('\n').map((paragraph, index) => (
                                    <p key={index}>{paragraph}</p>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Instructions */}
                    {technique.instructions && (
                        <div className="content-section">
                            <h2 className="section-title execution">Instructions</h2>
                            <div className="content-text">
                                {technique.instructions.split('\n').map((instruction, index) => (
                                    <p key={index}>{instruction}</p>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Tips */}
                    {technique.tips && (
                        <div className="content-section">
                            <h2 className="section-title common-mistakes">Tips & Reminders</h2>
                            <div className="content-text">
                                {technique.tips.split('\n').map((tip, index) => (
                                    <p key={index}>{tip}</p>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Variations */}
                    {technique.variations && (
                        <div className="content-section">
                            <h2 className="section-title variations">Variations</h2>
                            <div className="content-text">
                                {technique.variations.split('\n').map((variation, index) => (
                                    <p key={index}>{variation}</p>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Media Placeholder */}
                    <div className="media-section">
                        <div className="media-placeholder">
                            <div className="media-icon">🎥</div>
                            <p className="media-text">
                                Instructional videos and demonstrations coming soon
                            </p>
                        </div>
                    </div>
                </div>

                {/* Right Column - Sidebar */}
                <div className="content-sidebar">
                    {/* Quick Info Card */}
                    <div className="sidebar-card">
                        <h3 className="sidebar-title stats">Quick Info</h3>
                        <div className="quick-info-grid">
                            <div className="info-item">
                                <span className="info-label">Martial Art:</span>
                                <span className="info-value">{technique.style}</span>
                            </div>
                            {technique.category && (
                                <div className="info-item">
                                    <span className="info-label">Category:</span>
                                    <span className="info-value">{technique.category}</span>
                                </div>
                            )}
                            <div className="info-item">
                                <span className="info-label">Difficulty:</span>
                                <span className="info-value">
                                    {getDifficultyText(technique.difficulty_level)}
                                    {technique.difficulty_level && ` (${technique.difficulty_level}/10)`}
                                </span>
                            </div>
                            {technique.belt_level && (
                                <div className="info-item">
                                    <span className="info-label">Belt Level:</span>
                                    <span className="info-value">{technique.belt_level}</span>
                                </div>
                            )}
                            <div className="info-item">
                                <span className="info-label">Source:</span>
                                <span className="info-value">{technique.source_site || 'BlackBeltWiki'}</span>
                            </div>
                        </div>
                    </div>

                    {/* User Progress Card */}
                    {isAuthenticated && isBookmarked && (
                        <div className="sidebar-card">
                            <h3 className="sidebar-title progress">Your Progress</h3>
                            <div className="progress-tracking">
                                <div className="progress-level">
                                    Level {masteryLevel}/10
                                </div>
                                <div className={`progress-status ${getMasteryColor(masteryLevel)}`}>
                                    {getMasteryText(masteryLevel)}
                                </div>
                                <div className="progress-bar">
                                    <div
                                        className="progress-fill"
                                        style={{ width: `${(masteryLevel / 10) * 100}%` }}
                                    ></div>
                                </div>

                                {/* Mastery Level Slider */}
                                <div className="mastery-slider">
                                    <label className="slider-label">
                                        Update Level: {masteryLevel}/10
                                    </label>
                                    <input
                                        type="range"
                                        min="1"
                                        max="10"
                                        value={masteryLevel}
                                        onChange={(e) => setMasteryLevel(parseInt(e.target.value))}
                                        className="progress-slider"
                                    />
                                    <div className="slider-labels">
                                        <span>Learning</span>
                                        <span>Mastered</span>
                                    </div>
                                </div>

                                {/* Personal Notes */}
                                <div className="notes-section">
                                    <div className="notes-header">
                                        <label className="notes-label">Personal Notes</label>
                                        {!isEditingNotes ? (
                                            <button
                                                onClick={() => setIsEditingNotes(true)}
                                                className="edit-notes-btn"
                                            >
                                                <Edit3 size={14} />
                                                Edit
                                            </button>
                                        ) : (
                                            <div className="notes-actions">
                                                <button
                                                    onClick={updateProgress}
                                                    disabled={isSaving}
                                                    className="save-notes-btn"
                                                >
                                                    <Save size={14} />
                                                    {isSaving ? 'Saving...' : 'Save'}
                                                </button>
                                                <button
                                                    onClick={() => {
                                                        setIsEditingNotes(false);
                                                        setPersonalNotes(userBookmark?.personal_notes || '');
                                                    }}
                                                    className="cancel-notes-btn"
                                                >
                                                    <X size={14} />
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
                                            className="notes-textarea"
                                            rows="4"
                                        />
                                    ) : (
                                        <div className="notes-display">
                                            {personalNotes || (
                                                <span className="notes-placeholder">
                                                    No notes yet. Click edit to add your thoughts!
                                                </span>
                                            )}
                                        </div>
                                    )}
                                </div>

                                {/* Practice Stats */}
                                {userBookmark && (
                                    <div className="practice-stats">
                                        <div className="practice-stat">
                                            <div className="stat-value">{userBookmark.practice_count || 0}</div>
                                            <div className="stat-label">Practice Sessions</div>
                                        </div>
                                        <div className="practice-stat">
                                            <div className="stat-value">
                                                {userBookmark.last_practiced
                                                    ? new Date(userBookmark.last_practiced).toLocaleDateString()
                                                    : 'Never'
                                                }
                                            </div>
                                            <div className="stat-label">Last Practiced</div>
                                        </div>
                                    </div>
                                )}

                                <button
                                    onClick={updateProgress}
                                    disabled={isSaving}
                                    className="practice-btn mark-practiced"
                                >
                                    <Plus size={16} />
                                    {isSaving ? 'Updating...' : 'Mark as Practiced'}
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Authentication Prompt */}
                    {!isAuthenticated && (
                        <div className="sidebar-card auth-prompt">
                            <h3 className="auth-title">Track Your Progress</h3>
                            <p className="auth-description">
                                Log in to bookmark techniques, track your progress, and add personal notes.
                            </p>
                            <button
                                onClick={() => navigate('/login')}
                                className="auth-login-btn"
                            >
                                Log In
                            </button>
                        </div>
                    )}

                    {/* Source Link */}
                    {technique.source_url && (
                        <div className="sidebar-card">
                            <h3 className="sidebar-title related">Source</h3>
                            <a
                                href={technique.source_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="source-link"
                            >
                                View Original Source →
                            </a>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default TechniqueDetail;