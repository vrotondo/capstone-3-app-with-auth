// Replace your VideoPlayerPage.jsx with this functional version

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Button from '../components/common/Button';
import LoadingSpinner from '../components/common/LoadingSpinner';
import trainingService from '../services/trainingService';

const VideoPlayerPage = () => {
    const { videoId } = useParams();
    const navigate = useNavigate();

    const [video, setVideo] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');
    const [videoError, setVideoError] = useState(false);
    const [videoAspectRatio, setVideoAspectRatio] = useState('landscape');

    // Load video data
    useEffect(() => {
        const loadVideo = async () => {
            try {
                setIsLoading(true);
                setError('');

                console.log('🎥 Loading video with ID:', videoId);
                const response = await trainingService.getVideo(videoId);
                console.log('✅ Video loaded:', response.video);
                setVideo(response.video);
            } catch (error) {
                console.error('❌ Failed to load video:', error);
                setError('Failed to load video. The video may not exist or you may not have permission to view it.');
            } finally {
                setIsLoading(false);
            }
        };

        if (videoId) {
            loadVideo();
        }
    }, [videoId]);

    const handleBackToLibrary = () => {
        navigate('/training');
    };

    const handleDeleteVideo = async () => {
        if (!window.confirm('Are you sure you want to delete this video? This action cannot be undone.')) {
            return;
        }

        try {
            await trainingService.deleteVideo(videoId);
            console.log('✅ Video deleted successfully');
            navigate('/training');
        } catch (error) {
            console.error('❌ Failed to delete video:', error);
            setError('Failed to delete video. Please try again.');
        }
    };

    // Get video URL for player
    const getVideoUrl = () => {
        if (!video) return '';
        const url = trainingService.getVideoFileUrl(video.id);
        console.log('🎬 Video URL being used:', url);
        return url;
    };

    // Handle video metadata loading to detect aspect ratio
    const handleVideoLoadedMetadata = (e) => {
        const videoElement = e.target;
        const { videoWidth, videoHeight } = videoElement;

        console.log(`📐 Video dimensions: ${videoWidth}x${videoHeight}`);

        // Determine if video is portrait or landscape
        const aspectRatio = videoWidth / videoHeight;
        const isPortrait = aspectRatio < 1; // Height > Width

        setVideoAspectRatio(isPortrait ? 'portrait' : 'landscape');
        console.log(`🎭 Video aspect ratio detected: ${isPortrait ? 'Portrait (TikTok-style)' : 'Landscape (YouTube-style)'}`);
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    // Loading state
    if (isLoading) {
        return (
            <div className="video-player-page loading">
                <LoadingSpinner />
                <p>Loading video...</p>
            </div>
        );
    }

    // Error state
    if (error) {
        return (
            <div className="video-player-page error">
                <div className="error-content">
                    <h2>Video Not Found</h2>
                    <p>{error}</p>
                    <Button variant="primary" onClick={handleBackToLibrary}>
                        Back to Video Library
                    </Button>
                </div>
            </div>
        );
    }

    // No video found
    if (!video) {
        return (
            <div className="video-player-page error">
                <div className="error-content">
                    <h2>Video Not Found</h2>
                    <p>The requested video could not be found.</p>
                    <Button variant="primary" onClick={handleBackToLibrary}>
                        Back to Video Library
                    </Button>
                </div>
            </div>
        );
    }

    return (
        <div className="video-player-page">
            {/* Navigation Bar */}
            <div className="video-nav">
                <Button
                    variant="secondary"
                    onClick={handleBackToLibrary}
                    className="back-btn"
                >
                    ← Back to Library
                </Button>
                <h1>Video Player</h1>
            </div>

            {/* Enhanced Debug info */}
            <div style={{
                background: '#f0f9ff',
                padding: '1rem',
                borderRadius: '8px',
                marginBottom: '1rem',
                fontSize: '0.9rem'
            }}>
                <strong>Debug Info:</strong> Video ID: {videoId} | Title: {video?.title} |
                File Size: {video?.file_size_mb}MB | Aspect: {videoAspectRatio} | Status: {video?.analysis_status}
            </div>

            {/* Main Content */}
            <div className="video-content">
                {/* Enhanced Video Player Section */}
                <div className="video-section">
                    <div className={`video-player-container ${videoAspectRatio}`}>
                        {videoError ? (
                            <div className="video-error">
                                <h3>⚠️ Video Loading Error</h3>
                                <p>Unable to load video file. This might be a temporary issue.</p>
                                <Button variant="primary" onClick={() => {
                                    setVideoError(false);
                                    window.location.reload();
                                }}>
                                    Try Again
                                </Button>
                            </div>
                        ) : (
                            <video
                                controls
                                preload="metadata"
                                src={getVideoUrl()}
                                onError={(e) => {
                                    console.error('❌ Video loading error:', e);
                                    setVideoError(true);
                                }}
                                onLoadStart={() => console.log('📼 Video loading started')}
                                onCanPlay={() => console.log('✅ Video can play')}
                                onLoadedData={() => console.log('✅ Video loaded successfully')}
                                onLoadedMetadata={handleVideoLoadedMetadata}
                                style={{
                                    width: '100%',
                                    height: 'auto',
                                    backgroundColor: '#000',
                                    borderRadius: '12px'
                                }}
                            >
                                Your browser does not support the video tag.
                            </video>
                        )}
                    </div>

                    {/* Video Info Pills */}
                    <div style={{
                        display: 'flex',
                        gap: '1rem',
                        marginTop: '1rem',
                        justifyContent: 'center',
                        flexWrap: 'wrap'
                    }}>
                        <span style={{
                            background: videoAspectRatio === 'portrait' ? '#ff6b6b' : '#4ecdc4',
                            color: 'white',
                            padding: '0.25rem 0.75rem',
                            borderRadius: '16px',
                            fontSize: '0.8rem',
                            fontWeight: '500'
                        }}>
                            {videoAspectRatio === 'portrait' ? '📱 Portrait (TikTok-style)' : '🖥️ Landscape (YouTube-style)'}
                        </span>

                        {video?.file_size_mb && (
                            <span style={{
                                background: '#6c5ce7',
                                color: 'white',
                                padding: '0.25rem 0.75rem',
                                borderRadius: '16px',
                                fontSize: '0.8rem',
                                fontWeight: '500'
                            }}>
                                📁 {video.file_size_mb}MB
                            </span>
                        )}

                        <span style={{
                            background: '#a8e6cf',
                            color: '#2d3436',
                            padding: '0.25rem 0.75rem',
                            borderRadius: '16px',
                            fontSize: '0.8rem',
                            fontWeight: '500'
                        }}>
                            🎬 Ready for AI Analysis
                        </span>
                    </div>
                </div>

                {/* Video Details Section */}
                <div className="video-details">
                    {/* Video Header */}
                    <div className="video-header">
                        <h2>{video.title}</h2>
                        <div className="video-stats">
                            <span className="stat-item">📁 {video.file_size_mb}MB</span>
                            {video.duration && (
                                <span className="stat-item">⏱️ {trainingService.formatVideoDuration(video.duration)}</span>
                            )}
                            <span className="stat-item">📅 {formatDate(video.created_at)}</span>
                        </div>
                    </div>

                    {/* Video Metadata */}
                    <div className="video-metadata">
                        {video.technique_name && (
                            <div className="metadata-item">
                                <strong>Technique:</strong>
                                <span className="technique-badge">{video.technique_name}</span>
                            </div>
                        )}

                        {video.style && (
                            <div className="metadata-item">
                                <strong>Martial Art:</strong>
                                <span className="style-badge">{video.style}</span>
                            </div>
                        )}

                        {video.description && (
                            <div className="metadata-item description">
                                <strong>Description:</strong>
                                <p>{video.description}</p>
                            </div>
                        )}

                        {video.tags && video.tags.length > 0 && (
                            <div className="metadata-item">
                                <strong>Tags:</strong>
                                <div className="tags-container">
                                    {video.tags.map((tag, index) => (
                                        <span key={index} className="tag">{tag}</span>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Analysis Status */}
                        <div className="metadata-item">
                            <strong>Analysis Status:</strong>
                            <span
                                className={`status-badge ${video.analysis_status}`}
                                style={{
                                    backgroundColor: trainingService.getAnalysisStatusColor(video.analysis_status),
                                    color: 'white',
                                    padding: '0.25rem 0.75rem',
                                    borderRadius: '12px',
                                    fontSize: '0.8rem',
                                    marginLeft: '0.5rem'
                                }}
                            >
                                {trainingService.getAnalysisStatusLabel(video.analysis_status)}
                            </span>
                        </div>

                        {/* Analysis Results (if available) */}
                        {video.analysis_results && (
                            <div className="metadata-item analysis-results">
                                <strong>AI Analysis:</strong>
                                <div className="analysis-content">
                                    {video.analysis_score && (
                                        <div className="analysis-score">
                                            <span className="score-label">Overall Score:</span>
                                            <span className="score-value">{video.analysis_score}/10</span>
                                        </div>
                                    )}
                                    <div className="analysis-feedback">
                                        <p>{video.analysis_results.feedback || 'Analysis complete - detailed feedback coming soon!'}</p>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Privacy Status */}
                        <div className="metadata-item">
                            <strong>Privacy:</strong>
                            <span className={`privacy-badge ${video.is_private ? 'private' : 'public'}`}>
                                {video.is_private ? '🔒 Private' : '🌐 Public'}
                            </span>
                        </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="video-actions">
                        <Button
                            variant="secondary"
                            onClick={() => window.open(trainingService.getVideoDownloadUrl(video.id), '_blank')}
                        >
                            ⬇️ Download
                        </Button>

                        <Button
                            variant="danger"
                            onClick={handleDeleteVideo}
                        >
                            🗑️ Delete
                        </Button>
                    </div>

                    {/* Future AI Analysis Section */}
                    {video.analysis_status === 'pending' && (
                        <div className="ai-analysis-section">
                            <h3>🤖 AI Analysis</h3>
                            <p>Get detailed feedback on your technique with AI analysis!</p>
                            <Button
                                variant="primary"
                                className="ai-analyze-btn"
                                disabled
                            >
                                Analyze with AI (Coming Soon!)
                            </Button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default VideoPlayerPage;