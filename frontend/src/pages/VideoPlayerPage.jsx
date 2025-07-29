import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Button from '../components/common/Button';
import LoadingSpinner from '../components/common/LoadingSpinner';
import AspectRatioToggle from '../components/features/training/AspectRatioToggle';
import trainingService from '../services/trainingService';

const VideoPlayerPage = () => {
    const { videoId } = useParams();
    const navigate = useNavigate();

    const [video, setVideo] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');
    const [videoError, setVideoError] = useState(false);

    // Enhanced aspect ratio state management
    const [naturalAspectRatio, setNaturalAspectRatio] = useState('auto'); // Video's natural ratio
    const [displayMode, setDisplayMode] = useState('auto'); // Current display mode
    const [videoDimensions, setVideoDimensions] = useState({ width: 0, height: 0 });
    const [isVideoLoading, setIsVideoLoading] = useState(true);

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

    // Enhanced video URL with debugging
    const getVideoUrl = () => {
        if (!video) return '';
        const url = trainingService.getVideoFileUrl(video.id);
        console.log('🎬 Video URL being used:', url);
        return url;
    };

    // Smart aspect ratio detection
    const handleVideoLoadedMetadata = (e) => {
        const videoElement = e.target;
        const { videoWidth, videoHeight } = videoElement;

        console.log(`📐 Video dimensions: ${videoWidth}x${videoHeight}`);

        setVideoDimensions({ width: videoWidth, height: videoHeight });

        // Calculate aspect ratio
        const aspectRatio = videoWidth / videoHeight;

        let detectedRatio;
        let ratioType;

        if (Math.abs(aspectRatio - 1) < 0.1) {
            // Square-ish (Instagram style)
            detectedRatio = 'square';
            ratioType = 'Square (1:1)';
        } else if (aspectRatio < 0.8) {
            // Portrait (TikTok style)
            detectedRatio = 'portrait';
            ratioType = 'Portrait (9:16)';
        } else if (aspectRatio > 1.5) {
            // Landscape (YouTube style)
            detectedRatio = 'landscape';
            ratioType = 'Landscape (16:9)';
        } else {
            // Other ratios
            detectedRatio = 'auto';
            ratioType = 'Custom';
        }

        setNaturalAspectRatio(detectedRatio);
        console.log(`🎭 Video aspect ratio detected: ${ratioType} (${aspectRatio.toFixed(2)})`);
        setIsVideoLoading(false);
    };

    const handleVideoLoadStart = () => {
        console.log('📼 Video loading started');
        setIsVideoLoading(true);
    };

    const handleVideoCanPlay = () => {
        console.log('✅ Video can play');
        setIsVideoLoading(false);
    };

    const handleVideoError = (e) => {
        console.error('❌ Video loading error:', e);
        setVideoError(true);
        setIsVideoLoading(false);
    };

    // Toggle display mode
    const handleDisplayModeChange = (newMode) => {
        console.log(`🔄 Switching display mode from ${displayMode} to ${newMode}`);
        setDisplayMode(newMode);
    };

    // Get current effective aspect ratio
    const getEffectiveAspectRatio = () => {
        if (displayMode === 'auto') {
            return naturalAspectRatio;
        }
        return displayMode;
    };

    // Check if current display mode differs from natural ratio
    const isForced = displayMode !== 'auto' && naturalAspectRatio !== displayMode;

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const getAspectRatioInfo = () => {
        const { width, height } = videoDimensions;
        const ratio = width && height ? (width / height).toFixed(2) : 'Unknown';
        const effectiveMode = getEffectiveAspectRatio();

        const modeInfo = {
            portrait: {
                icon: '📱',
                label: 'Portrait',
                description: 'TikTok Style',
                ratio: '0.56',
                class: 'portrait'
            },
            landscape: {
                icon: '🖥️',
                label: 'Landscape',
                description: 'YouTube Style',
                ratio: '1.78',
                class: 'landscape'
            },
            square: {
                icon: '📷',
                label: 'Square',
                description: 'Instagram Style',
                ratio: '1.00',
                class: 'square'
            },
            auto: {
                icon: '🎬',
                label: 'Auto',
                description: 'Original Ratio',
                ratio: ratio,
                class: naturalAspectRatio
            }
        };

        return modeInfo[effectiveMode] || modeInfo.auto;
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

    const aspectInfo = getAspectRatioInfo();
    const effectiveAspectRatio = getEffectiveAspectRatio();

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
                <h1>🎬 Video Player</h1>
            </div>

            {/* Main Content */}
            <div className="video-content">
                {/* Enhanced Video Player Section */}
                <div className="video-section">
                    {/* Video Player Container - FIRST */}
                    <div className={`video-player-container ${effectiveAspectRatio} ${isVideoLoading ? 'loading' : ''}`}>
                        {videoError ? (
                            <div className="video-error">
                                <h3>⚠️ Video Loading Error</h3>
                                <p>Unable to load video file. This might be a temporary issue.</p>
                                <Button variant="primary" onClick={() => {
                                    setVideoError(false);
                                    setIsVideoLoading(true);
                                    window.location.reload();
                                }}>
                                    Try Again
                                </Button>
                            </div>
                        ) : (
                            <>
                                {/* Crop Indicator (when video is being cropped) */}
                                {isForced && (
                                    <div className="crop-indicator">
                                        ✂️ Video cropped to fit {displayMode} format
                                    </div>
                                )}

                                <video
                                    controls
                                    preload="metadata"
                                    src={getVideoUrl()}
                                    onError={handleVideoError}
                                    onLoadStart={handleVideoLoadStart}
                                    onCanPlay={handleVideoCanPlay}
                                    onLoadedData={() => console.log('✅ Video loaded successfully')}
                                    onLoadedMetadata={handleVideoLoadedMetadata}
                                    className={`video-element ${effectiveAspectRatio}-video ${isForced ? 'video-forced-fit' : 'video-natural-fit'}`}
                                    style={{
                                        width: '100%',
                                        height: '100%',
                                        backgroundColor: '#000',
                                        borderRadius: '16px'
                                    }}
                                >
                                    Your browser does not support the video tag.
                                </video>
                            </>
                        )}
                    </div>

                    {/* Professional Video Info Pills - SECOND */}
                    <div className="video-info-pills">
                        <div className={`video-pill aspect-ratio ${aspectInfo.class}`}>
                            {aspectInfo.icon} {aspectInfo.label} • {aspectInfo.description}
                            {videoDimensions.width && (
                                <span style={{ opacity: 0.8, marginLeft: '0.5rem' }}>
                                    ({videoDimensions.width}×{videoDimensions.height})
                                </span>
                            )}
                        </div>

                        {video.file_size_mb && (
                            <div className="video-pill file-size">
                                📁 {video.file_size_mb}MB
                            </div>
                        )}

                        <div className="video-pill ai-ready">
                            🤖 Ready for AI Analysis
                        </div>

                        {video.analysis_status === 'completed' && video.analysis_score && (
                            <div className="video-pill" style={{
                                background: 'linear-gradient(135deg, #00b894 0%, #00a085 100%)',
                                color: 'white'
                            }}>
                                🎯 Score: {video.analysis_score}/10
                            </div>
                        )}
                    </div>

                    {/* Aspect Ratio Toggle Controls - THIRD (BELOW VIDEO) */}
                    <AspectRatioToggle
                        naturalAspectRatio={naturalAspectRatio}
                        currentDisplayMode={displayMode}
                        onDisplayModeChange={handleDisplayModeChange}
                        videoDimensions={videoDimensions}
                        isForced={isForced}
                    />
                </div>

                {/* Enhanced Video Details Section */}
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

                        {/* Enhanced Analysis Status */}
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

                        {/* Technical Info */}
                        <div className="metadata-item">
                            <strong>Video Details:</strong>
                            <div style={{
                                background: 'var(--background-secondary, #f8f9fa)',
                                padding: '1rem',
                                borderRadius: '8px',
                                marginTop: '0.5rem',
                                fontSize: '0.9rem'
                            }}>
                                <div style={{ marginBottom: '0.5rem' }}>
                                    <strong>Original Resolution:</strong> {videoDimensions.width}×{videoDimensions.height}
                                </div>
                                <div style={{ marginBottom: '0.5rem' }}>
                                    <strong>Original Aspect Ratio:</strong> {aspectInfo.ratio}
                                </div>
                                <div style={{ marginBottom: '0.5rem' }}>
                                    <strong>Display Mode:</strong> {aspectInfo.description}
                                </div>
                                <div>
                                    <strong>File Size:</strong> {video.file_size_mb}MB
                                </div>
                                {isForced && (
                                    <div style={{ marginTop: '0.5rem', color: '#856404' }}>
                                        ⚠️ Video aspect ratio has been forced. Content may be cropped or letterboxed.
                                    </div>
                                )}
                            </div>
                        </div>

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

                    {/* Enhanced AI Analysis Section */}
                    {video.analysis_status === 'pending' && (
                        <div className="ai-analysis-section">
                            <h3>🤖 AI Technique Analysis</h3>
                            <p>Get detailed feedback on your martial arts technique with our advanced AI system!</p>
                            <div style={{ marginBottom: '1rem', fontSize: '0.9rem', opacity: 0.9 }}>
                                <strong>What AI Analysis Provides:</strong>
                                <ul style={{ margin: '0.5rem 0', paddingLeft: '1.5rem', textAlign: 'left' }}>
                                    <li>Technique form assessment</li>
                                    <li>Movement quality scoring</li>
                                    <li>Improvement suggestions</li>
                                    <li>Progress tracking over time</li>
                                </ul>
                            </div>
                            <Button
                                variant="primary"
                                className="ai-analyze-btn"
                                disabled
                                style={{
                                    background: 'rgba(255, 255, 255, 0.2)',
                                    border: '1px solid rgba(255, 255, 255, 0.3)',
                                    color: 'white',
                                    opacity: 0.7,
                                    cursor: 'not-allowed'
                                }}
                            >
                                🚀 Analyze Technique (Coming Soon!)
                            </Button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default VideoPlayerPage;