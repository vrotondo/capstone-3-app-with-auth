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
            <div className="my-techniques-page">
                <div className="loading-container">
                    <div className="spinner spinner-md"></div>
                    <p>Loading your techniques...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="my-techniques-page">
                <div className="techniques-empty-state">
                    <div className="empty-icon">⚠️</div>
                    <h3 className="empty-title">Error Loading Techniques</h3>
                    <p className="empty-subtitle">{error}</p>
                    <button
                        onClick={loadBookmarks}
                        className="get-started-btn"
                    >
                        Try Again
                    </button>
                </div>
            </div>
        );
    }

    const filteredBookmarks = getFilteredAndSortedBookmarks();

    return (
        <div className="my-techniques-page">
            {/* Enhanced Header */}
            <div className="my-techniques-header">
                <h1 className="my-techniques-title">My Techniques</h1>
                <p className="my-techniques-subtitle">
                    Track your progress and practice your bookmarked techniques
                </p>
            </div>

            {bookmarks.length === 0 ? (
                // Enhanced Empty State
                <div className="techniques-empty-state">
                    <div className="empty-icon">🥋</div>
                    <h3 className="empty-title">No techniques bookmarked yet</h3>
                    <p className="empty-subtitle">
                        Start building your personal technique collection by bookmarking techniques from the library
                    </p>
                    <button
                        onClick={() => navigate('/techniques')}
                        className="get-started-btn"
                    >
                        Explore Technique Library
                    </button>
                </div>
            ) : (
                <>
                    {/* Enhanced Stats Grid */}
                    <div className="techniques-stats-grid">
                        <div className="technique-stat-card">
                            <span className="stat-icon total">📚</span>
                            <span className="stat-number">{stats.total}</span>
                            <span className="stat-label">Total Techniques</span>
                        </div>

                        <div className="technique-stat-card">
                            <span className="stat-icon learning">🌱</span>
                            <span className="stat-number">{stats.learning}</span>
                            <span className="stat-label">Learning</span>
                        </div>

                        <div className="technique-stat-card">
                            <span className="stat-icon practicing">⚡</span>
                            <span className="stat-number">{stats.practicing}</span>
                            <span className="stat-label">Practicing</span>
                        </div>

                        <div className="technique-stat-card">
                            <span className="stat-icon improving">📈</span>
                            <span className="stat-number">{stats.improving}</span>
                            <span className="stat-label">Improving</span>
                        </div>

                        <div className="technique-stat-card">
                            <span className="stat-icon mastered">🏆</span>
                            <span className="stat-number">{stats.mastered}</span>
                            <span className="stat-label">Mastered</span>
                        </div>
                    </div>

                    {/* Enhanced Controls */}
                    <div className="techniques-controls">
                        <div className="controls-header">
                            <h3 className="controls-title">Filter & Sort</h3>
                            <button
                                onClick={() => navigate('/techniques')}
                                className="browse-library-btn"
                            >
                                Browse Library
                            </button>
                        </div>

                        <div className="controls-row">
                            <div className="control-group">
                                <label className="control-label">📂 Filter by Progress</label>
                                <select
                                    value={filterBy}
                                    onChange={(e) => setFilterBy(e.target.value)}
                                    className="control-select"
                                >
                                    <option value="all">All Techniques</option>
                                    <option value="learning">Learning (1-2)</option>
                                    <option value="practicing">Practicing (3-4)</option>
                                    <option value="improving">Improving (5-7)</option>
                                    <option value="mastered">Mastered (8-10)</option>
                                </select>
                            </div>

                            <div className="control-group">
                                <label className="control-label">🔄 Sort by</label>
                                <select
                                    value={sortBy}
                                    onChange={(e) => setSortBy(e.target.value)}
                                    className="control-select"
                                >
                                    <option value="recent">Most Recent</option>
                                    <option value="name">Name A-Z</option>
                                    <option value="mastery">Highest Mastery</option>
                                    <option value="practice">Most Practiced</option>
                                </select>
                            </div>

                            <div className="control-group">
                                <label className="control-label">📊 Results</label>
                                <div className="techniques-count">
                                    {filteredBookmarks.length} of {bookmarks.length}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Enhanced Techniques List */}
                    <div className="techniques-list-section">
                        <div className="list-header">
                            <h2 className="list-title">Your Techniques</h2>
                        </div>

                        <div className="my-techniques-grid">
                            {filteredBookmarks.map((bookmark) => (
                                <EnhancedTechniqueCard
                                    key={bookmark.id}
                                    bookmark={bookmark}
                                    onRemove={removeBookmark}
                                    onUpdateProgress={updateProgress}
                                    onViewDetail={(id) => navigate(`/techniques/${id}`)}
                                />
                            ))}
                        </div>
                    </div>
                </>
            )}
        </div>
    );
};

// Enhanced Individual Technique Card Component
const EnhancedTechniqueCard = ({ bookmark, onRemove, onUpdateProgress, onViewDetail }) => {
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

    const getMasteryClass = (level) => {
        if (level <= 2) return 'learning';
        if (level <= 4) return 'practicing';
        if (level <= 7) return 'improving';
        return 'mastered';
    };

    const handleMasteryChange = (newLevel) => {
        setNewMasteryLevel(newLevel);
        onUpdateProgress(technique.id, newLevel);
    };

    return (
        <div className="enhanced-technique-card">
            {/* Level Badge */}
            <div className={`level-badge ${getMasteryClass(masteryLevel)}`}>
                Level {technique.difficulty_level || '?'}
            </div>

            {/* Enhanced Header */}
            <div className="enhanced-technique-header">
                <h3
                    className="enhanced-technique-name"
                    onClick={() => onViewDetail(technique.id)}
                    style={{ cursor: 'pointer' }}
                >
                    {technique.name}
                </h3>
                <div className="technique-meta-badges">
                    <span className="style-badge">{technique.style}</span>
                    <span className="bookmark-badge">Bookmarked</span>
                </div>
            </div>

            {/* Enhanced Progress Section */}
            <div className="technique-progress-section">
                <div className="progress-header">
                    <h4 className="progress-title">Progress</h4>
                    <div className="sessions-count">
                        {bookmark.practice_count || 0} sessions
                    </div>
                </div>

                <div className="mastery-progress">
                    <div className="mastery-label">
                        {getMasteryText(masteryLevel)} ({masteryLevel}/10)
                    </div>
                    <div className="mastery-bar">
                        <div
                            className="mastery-fill"
                            style={{ width: `${(masteryLevel / 10) * 100}%` }}
                        ></div>
                    </div>
                </div>

                {/* Mastery Level Slider */}
                <div style={{ margin: '1rem 0' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                        <label style={{ fontSize: '0.875rem', fontWeight: '600', color: 'var(--text-primary)' }}>
                            Update Level:
                        </label>
                        <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                            {newMasteryLevel}/10
                        </span>
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
                        style={{
                            width: '100%',
                            height: '8px',
                            background: '#e5e7eb',
                            borderRadius: '4px',
                            outline: 'none',
                            cursor: 'pointer'
                        }}
                    />
                </div>

                {bookmark.last_practiced && (
                    <div className="last-practiced">
                        Last practiced: {techniqueService.formatDate(bookmark.last_practiced)}
                    </div>
                )}
            </div>

            {/* Personal Notes */}
            {bookmark.personal_notes && (
                <div className="personal-notes">
                    <h5 className="notes-title">Personal Notes:</h5>
                    <p className="notes-text">{bookmark.personal_notes}</p>
                </div>
            )}

            {/* Description */}
            {technique.description && (
                <div style={{ margin: '1rem 0', flex: '1' }}>
                    <p style={{
                        fontSize: '0.875rem',
                        color: 'var(--text-secondary)',
                        lineHeight: '1.4',
                        textAlign: 'left'
                    }}>
                        {isExpanded
                            ? technique.description
                            : techniqueService.truncateText(technique.description, 120)
                        }
                    </p>
                    {technique.description.length > 120 && (
                        <button
                            onClick={() => setIsExpanded(!isExpanded)}
                            style={{
                                color: 'var(--primary-color)',
                                background: 'none',
                                border: 'none',
                                fontSize: '0.875rem',
                                fontWeight: '500',
                                cursor: 'pointer',
                                marginTop: '0.5rem'
                            }}
                        >
                            {isExpanded ? 'Show less' : 'Show more'}
                        </button>
                    )}
                </div>
            )}

            {/* Tags */}
            {technique.tags && technique.tags.length > 0 && (
                <div style={{
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: '0.5rem',
                    margin: '1rem 0',
                    textAlign: 'left'
                }}>
                    {technique.tags.slice(0, 3).map((tag, index) => (
                        <span
                            key={index}
                            style={{
                                padding: '0.25rem 0.5rem',
                                fontSize: '0.75rem',
                                background: '#f3f4f6',
                                color: '#6b7280',
                                borderRadius: '4px'
                            }}
                        >
                            #{tag}
                        </span>
                    ))}
                </div>
            )}

            {/* Enhanced Card Actions */}
            <div className="enhanced-card-actions">
                <div className="action-buttons">
                    <button
                        onClick={() => onViewDetail(technique.id)}
                        className="action-btn view-btn"
                        title="View Details"
                    >
                        👁️ View
                    </button>

                    <button
                        onClick={() => onRemove(technique.id)}
                        className="action-btn delete-btn"
                        title="Remove Bookmark"
                    >
                        🗑️ Remove
                    </button>
                </div>
            </div>
        </div>
    );
};

export default MyTechniques;