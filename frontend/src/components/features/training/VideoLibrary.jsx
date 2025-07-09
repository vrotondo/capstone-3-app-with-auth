import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../../common/Button';
import LoadingSpinner from '../../common/LoadingSpinner';
import trainingService from '../../../services/trainingService';

const VideoLibrary = ({ onSelectVideo, onEditVideo, refreshTrigger }) => {
    const navigate = useNavigate();
    const [videos, setVideos] = useState([]);
    const [filteredVideos, setFilteredVideos] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');
    const [stats, setStats] = useState(null);
    const [filters, setFilters] = useState({
        search: '',
        style: '',
        technique: '',
        analysis_status: ''
    });
    const [sortBy, setSortBy] = useState('newest');

    // Load videos
    const loadVideos = async () => {
        try {
            setIsLoading(true);
            setError('');

            const response = await trainingService.getVideos();
            setVideos(response.videos || []);
            setStats(response.stats);
        } catch (error) {
            console.error('Failed to load videos:', error);
            setError('Failed to load videos. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    // Load videos on mount and when refreshTrigger changes
    useEffect(() => {
        loadVideos();
    }, [refreshTrigger]);

    // Filter and sort videos when filters or videos change
    useEffect(() => {
        let filtered = [...videos];

        // Apply filters
        if (filters.search) {
            const searchTerm = filters.search.toLowerCase();
            filtered = filtered.filter(video =>
                video.title.toLowerCase().includes(searchTerm) ||
                video.description?.toLowerCase().includes(searchTerm) ||
                video.technique_name?.toLowerCase().includes(searchTerm) ||
                video.original_filename.toLowerCase().includes(searchTerm)
            );
        }

        if (filters.style) {
            filtered = filtered.filter(video => video.style === filters.style);
        }

        if (filters.technique) {
            filtered = filtered.filter(video => video.technique_name === filters.technique);
        }

        if (filters.analysis_status) {
            filtered = filtered.filter(video => video.analysis_status === filters.analysis_status);
        }

        // Apply sorting
        filtered.sort((a, b) => {
            switch (sortBy) {
                case 'newest':
                    return new Date(b.created_at) - new Date(a.created_at);
                case 'oldest':
                    return new Date(a.created_at) - new Date(b.created_at);
                case 'title':
                    return a.title.localeCompare(b.title);
                case 'size':
                    return b.file_size - a.file_size;
                case 'score':
                    return (b.analysis_score || 0) - (a.analysis_score || 0);
                default:
                    return 0;
            }
        });

        setFilteredVideos(filtered);
    }, [videos, filters, sortBy]);

    const handleFilterChange = (field, value) => {
        setFilters(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const handleDeleteVideo = async (videoId) => {
        if (!window.confirm('Are you sure you want to delete this video? This action cannot be undone.')) {
            return;
        }

        try {
            await trainingService.deleteVideo(videoId);
            setVideos(prev => prev.filter(video => video.id !== videoId));
        } catch (error) {
            console.error('Failed to delete video:', error);
            setError('Failed to delete video. Please try again.');
        }
    };

    const getUniqueStyles = () => {
        return [...new Set(videos.map(video => video.style).filter(Boolean))];
    };

    const getUniqueTechniques = () => {
        return [...new Set(videos.map(video => video.technique_name).filter(Boolean))];
    };

    if (isLoading) {
        return (
            <div className="video-library-loading">
                <LoadingSpinner />
                <p>Loading your video library...</p>
            </div>
        );
    }

    return (
        <div className="video-library">
            {/* Stats Summary */}
            {stats && (
                <div className="video-stats">
                    <div className="stats-grid">
                        <div className="stat-item">
                            <div className="stat-number">{stats.total_videos}</div>
                            <div className="stat-label">Videos</div>
                        </div>
                        <div className="stat-item">
                            <div className="stat-number">{stats.total_size_mb}MB</div>
                            <div className="stat-label">Storage Used</div>
                        </div>
                        <div className="stat-item">
                            <div className="stat-number">{stats.total_duration_formatted}</div>
                            <div className="stat-label">Total Duration</div>
                        </div>
                        <div className="stat-item">
                            <div className="stat-number">{stats.avg_score || 'N/A'}</div>
                            <div className="stat-label">Avg. Score</div>
                        </div>
                    </div>
                </div>
            )}

            {error && (
                <div className="error-message">
                    {error}
                    <button onClick={() => setError('')} className="error-close">×</button>
                </div>
            )}

            {/* Filters and Search */}
            <div className="video-filters">
                <div className="search-box">
                    <input
                        type="text"
                        placeholder="Search videos..."
                        value={filters.search}
                        onChange={(e) => handleFilterChange('search', e.target.value)}
                        className="search-input"
                    />
                </div>

                <div className="filter-controls">
                    <select
                        value={filters.style}
                        onChange={(e) => handleFilterChange('style', e.target.value)}
                        className="filter-select"
                    >
                        <option value="">All Styles</option>
                        {getUniqueStyles().map(style => (
                            <option key={style} value={style}>{style}</option>
                        ))}
                    </select>

                    <select
                        value={filters.technique}
                        onChange={(e) => handleFilterChange('technique', e.target.value)}
                        className="filter-select"
                    >
                        <option value="">All Techniques</option>
                        {getUniqueTechniques().map(technique => (
                            <option key={technique} value={technique}>{technique}</option>
                        ))}
                    </select>

                    <select
                        value={filters.analysis_status}
                        onChange={(e) => handleFilterChange('analysis_status', e.target.value)}
                        className="filter-select"
                    >
                        <option value="">All Status</option>
                        <option value="pending">Pending Analysis</option>
                        <option value="processing">Processing</option>
                        <option value="completed">Analyzed</option>
                        <option value="failed">Analysis Failed</option>
                    </select>

                    <select
                        value={sortBy}
                        onChange={(e) => setSortBy(e.target.value)}
                        className="sort-select"
                    >
                        <option value="newest">Newest First</option>
                        <option value="oldest">Oldest First</option>
                        <option value="title">Title A-Z</option>
                        <option value="size">File Size</option>
                        <option value="score">Analysis Score</option>
                    </select>
                </div>
            </div>

            {/* Videos Grid */}
            {filteredVideos.length === 0 ? (
                <div className="no-videos">
                    {videos.length === 0 ? (
                        <div className="empty-state">
                            <div className="empty-icon">🎥</div>
                            <h3>No videos uploaded yet</h3>
                            <p>Upload your first training video to get started with AI analysis!</p>
                        </div>
                    ) : (
                        <div className="no-results">
                            <p>No videos match your current filters.</p>
                            <Button
                                variant="secondary"
                                onClick={() => setFilters({ search: '', style: '', technique: '', analysis_status: '' })}
                            >
                                Clear Filters
                            </Button>
                        </div>
                    )}
                </div>
            ) : (
                <div className="videos-grid">
                    {filteredVideos.map(video => (
                        <VideoCard
                            key={video.id}
                            video={video}
                            onSelect={onSelectVideo}
                            onEdit={onEditVideo}
                            onDelete={() => handleDeleteVideo(video.id)}
                        />
                    ))}
                </div>
            )}
        </div>
    );
};

const VideoCard = ({ video, onSelect, onEdit, onDelete }) => {
    const navigate = useNavigate();
    const [showActions, setShowActions] = useState(false);

    const handleCardClick = () => {
        console.log('🎬 Clicking video card, navigating to:', `/video/${video.id}`);
        navigate(`/video/${video.id}`);
    };

    const handleActionClick = (e, action) => {
        e.stopPropagation(); // Prevent card click when clicking action buttons
        action();
    };

    return (
        <div
            className="video-card"
            onClick={handleCardClick}
            onMouseEnter={() => setShowActions(true)}
            onMouseLeave={() => setShowActions(false)}
            style={{ cursor: 'pointer' }}
        >
            {/* Video Thumbnail/Preview */}
            <div className="video-thumbnail">
                <div className="video-placeholder">
                    <div className="play-icon">▶</div>
                    <div className="play-overlay">
                        <div className="play-overlay-icon">▶</div>
                        <span className="play-text">Click to Play</span>
                    </div>
                </div>
                {video.duration && (
                    <div className="video-duration">
                        {trainingService.formatVideoDuration(video.duration)}
                    </div>
                )}
            </div>

            {/* Rest of your existing VideoCard JSX... */}
            <div className="video-info">
                <h4 className="video-title">{video.title}</h4>

                <div className="video-meta">
                    {video.technique_name && (
                        <span className="technique-name">{video.technique_name}</span>
                    )}
                    {video.style && (
                        <span className="style-name">{video.style}</span>
                    )}
                </div>

                <div className="video-details">
                    <span className="file-size">{video.file_size_mb}MB</span>
                    <span className="upload-date">
                        {new Date(video.created_at).toLocaleDateString()}
                    </span>
                </div>

                {/* Analysis Status */}
                <div className="analysis-status">
                    <span
                        className={`status-badge ${video.analysis_status}`}
                        style={{
                            backgroundColor: trainingService.getAnalysisStatusColor(video.analysis_status)
                        }}
                    >
                        {trainingService.getAnalysisStatusLabel(video.analysis_status)}
                    </span>
                    {video.analysis_score && (
                        <span className="analysis-score">
                            Score: {video.analysis_score}/10
                        </span>
                    )}
                </div>

                {/* Tags */}
                {video.tags && video.tags.length > 0 && (
                    <div className="video-tags">
                        {video.tags.slice(0, 3).map(tag => (
                            <span key={tag} className="tag">{tag}</span>
                        ))}
                        {video.tags.length > 3 && (
                            <span className="tag-more">+{video.tags.length - 3}</span>
                        )}
                    </div>
                )}
            </div>

            {/* Action Buttons */}
            {showActions && (
                <div className="video-actions" onClick={(e) => e.stopPropagation()}>
                    <button
                        className="action-btn edit-btn"
                        onClick={(e) => handleActionClick(e, () => onEdit && onEdit(video))}
                        title="Edit video details"
                    >
                        ✏️
                    </button>
                    <button
                        className="action-btn download-btn"
                        onClick={(e) => handleActionClick(e, () => window.open(trainingService.getVideoDownloadUrl(video.id), '_blank'))}
                        title="Download video"
                    >
                        ⬇️
                    </button>
                    <button
                        className="action-btn delete-btn"
                        onClick={(e) => handleActionClick(e, () => onDelete && onDelete())}
                        title="Delete video"
                    >
                        🗑️
                    </button>
                </div>
            )}
        </div>
    );
};

export default VideoLibrary;