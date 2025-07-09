import React, { useState, useRef, useEffect } from 'react';
import Button from '../../common/Button';
import trainingService from '../../../services/trainingService';

const VideoPlayer = ({ video, onClose, onEdit, onDelete }) => {
    const videoRef = useRef(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);
    const [volume, setVolume] = useState(1);
    const [isMuted, setIsMuted] = useState(false);
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [showControls, setShowControls] = useState(true);
    const [playbackRate, setPlaybackRate] = useState(1);

    // Auto-hide controls timeout
    const controlsTimeoutRef = useRef(null);

    useEffect(() => {
        const videoElement = videoRef.current;
        if (!videoElement) return;

        const handleLoadedMetadata = () => {
            setDuration(videoElement.duration);
            setLoading(false);
        };

        const handleTimeUpdate = () => {
            setCurrentTime(videoElement.currentTime);
        };

        const handlePlay = () => setIsPlaying(true);
        const handlePause = () => setIsPlaying(false);
        const handleVolumeChange = () => {
            setVolume(videoElement.volume);
            setIsMuted(videoElement.muted);
        };

        const handleError = (e) => {
            console.error('Video error:', e);
            setError('Failed to load video. Please try again.');
            setLoading(false);
        };

        // Add event listeners
        videoElement.addEventListener('loadedmetadata', handleLoadedMetadata);
        videoElement.addEventListener('timeupdate', handleTimeUpdate);
        videoElement.addEventListener('play', handlePlay);
        videoElement.addEventListener('pause', handlePause);
        videoElement.addEventListener('volumechange', handleVolumeChange);
        videoElement.addEventListener('error', handleError);

        // Cleanup
        return () => {
            videoElement.removeEventListener('loadedmetadata', handleLoadedMetadata);
            videoElement.removeEventListener('timeupdate', handleTimeUpdate);
            videoElement.removeEventListener('play', handlePlay);
            videoElement.removeEventListener('pause', handlePause);
            videoElement.removeEventListener('volumechange', handleVolumeChange);
            videoElement.removeEventListener('error', handleError);
        };
    }, [video]);

    // Auto-hide controls
    useEffect(() => {
        const resetControlsTimeout = () => {
            if (controlsTimeoutRef.current) {
                clearTimeout(controlsTimeoutRef.current);
            }
            setShowControls(true);
            if (isPlaying) {
                controlsTimeoutRef.current = setTimeout(() => {
                    setShowControls(false);
                }, 3000);
            }
        };

        resetControlsTimeout();
        return () => {
            if (controlsTimeoutRef.current) {
                clearTimeout(controlsTimeoutRef.current);
            }
        };
    }, [isPlaying]);

    const togglePlayPause = () => {
        const videoElement = videoRef.current;
        if (!videoElement) return;

        if (isPlaying) {
            videoElement.pause();
        } else {
            videoElement.play();
        }
    };

    const handleSeek = (e) => {
        const videoElement = videoRef.current;
        if (!videoElement) return;

        const rect = e.currentTarget.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const newTime = (clickX / rect.width) * duration;

        videoElement.currentTime = newTime;
        setCurrentTime(newTime);
    };

    const handleVolumeChange = (e) => {
        const videoElement = videoRef.current;
        if (!videoElement) return;

        const newVolume = parseFloat(e.target.value);
        videoElement.volume = newVolume;
        setVolume(newVolume);
        setIsMuted(newVolume === 0);
    };

    const toggleMute = () => {
        const videoElement = videoRef.current;
        if (!videoElement) return;

        const newMuted = !isMuted;
        videoElement.muted = newMuted;
        setIsMuted(newMuted);
    };

    const changePlaybackRate = (rate) => {
        const videoElement = videoRef.current;
        if (!videoElement) return;

        videoElement.playbackRate = rate;
        setPlaybackRate(rate);
    };

    const toggleFullscreen = () => {
        const videoElement = videoRef.current;
        if (!videoElement) return;

        if (!isFullscreen) {
            if (videoElement.requestFullscreen) {
                videoElement.requestFullscreen();
            } else if (videoElement.webkitRequestFullscreen) {
                videoElement.webkitRequestFullscreen();
            } else if (videoElement.mozRequestFullScreen) {
                videoElement.mozRequestFullScreen();
            }
            setIsFullscreen(true);
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
            } else if (document.mozCancelFullScreen) {
                document.mozCancelFullScreen();
            }
            setIsFullscreen(false);
        }
    };

    const formatTime = (seconds) => {
        if (isNaN(seconds) || seconds === 0) return '0:00';

        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const remainingSeconds = Math.floor(seconds % 60);

        if (hours > 0) {
            return `${hours}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
        }

        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    };

    const getVideoUrl = () => {
        const token = localStorage.getItem('token');
        const baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
        return `${baseUrl}/training/videos/${video.id}/file`;
    };

    if (error) {
        return (
            <div className="video-player-error">
                <div className="error-content">
                    <h3>Video Error</h3>
                    <p>{error}</p>
                    <Button variant="primary" onClick={onClose}>
                        Back to Library
                    </Button>
                </div>
            </div>
        );
    }

    return (
        <div className="video-player-container">
            <div
                className={`video-player ${isFullscreen ? 'fullscreen' : ''}`}
                onMouseMove={() => setShowControls(true)}
                onMouseLeave={() => isPlaying && setShowControls(false)}
            >
                {loading && (
                    <div className="video-loading">
                        <div className="loading-spinner"></div>
                        <p>Loading video...</p>
                    </div>
                )}

                <video
                    ref={videoRef}
                    className="video-element"
                    src={getVideoUrl()}
                    onClick={togglePlayPause}
                    preload="metadata"
                >
                    Your browser does not support the video tag.
                </video>

                {/* Custom Video Controls */}
                <div className={`video-controls ${showControls ? 'show' : 'hide'}`}>
                    {/* Progress Bar */}
                    <div className="progress-container">
                        <div
                            className="progress-bar"
                            onClick={handleSeek}
                        >
                            <div
                                className="progress-fill"
                                style={{ width: `${(currentTime / duration) * 100}%` }}
                            ></div>
                            <div
                                className="progress-thumb"
                                style={{ left: `${(currentTime / duration) * 100}%` }}
                            ></div>
                        </div>
                    </div>

                    {/* Control Buttons */}
                    <div className="controls-row">
                        <div className="controls-left">
                            <button
                                className="control-btn play-pause"
                                onClick={togglePlayPause}
                            >
                                {isPlaying ? '⏸️' : '▶️'}
                            </button>

                            <div className="volume-control">
                                <button
                                    className="control-btn volume-btn"
                                    onClick={toggleMute}
                                >
                                    {isMuted || volume === 0 ? '🔇' : volume < 0.5 ? '🔉' : '🔊'}
                                </button>
                                <input
                                    type="range"
                                    min="0"
                                    max="1"
                                    step="0.1"
                                    value={isMuted ? 0 : volume}
                                    onChange={handleVolumeChange}
                                    className="volume-slider"
                                />
                            </div>

                            <div className="time-display">
                                <span>{formatTime(currentTime)} / {formatTime(duration)}</span>
                            </div>
                        </div>

                        <div className="controls-right">
                            <div className="playback-rate">
                                <select
                                    value={playbackRate}
                                    onChange={(e) => changePlaybackRate(parseFloat(e.target.value))}
                                    className="rate-select"
                                >
                                    <option value={0.5}>0.5x</option>
                                    <option value={0.75}>0.75x</option>
                                    <option value={1}>1x</option>
                                    <option value={1.25}>1.25x</option>
                                    <option value={1.5}>1.5x</option>
                                    <option value={2}>2x</option>
                                </select>
                            </div>

                            <button
                                className="control-btn fullscreen-btn"
                                onClick={toggleFullscreen}
                            >
                                {isFullscreen ? '⏹️' : '⛶'}
                            </button>
                        </div>
                    </div>
                </div>

                {/* Close button for modal mode */}
                {onClose && (
                    <button
                        className="video-close-btn"
                        onClick={onClose}
                    >
                        ✕
                    </button>
                )}
            </div>

            {/* Video Actions */}
            {(onEdit || onDelete) && (
                <div className="video-actions-bar">
                    {onEdit && (
                        <Button variant="secondary" onClick={() => onEdit(video)}>
                            Edit Details
                        </Button>
                    )}
                    {onDelete && (
                        <Button variant="danger" onClick={() => onDelete(video.id)}>
                            Delete Video
                        </Button>
                    )}
                </div>
            )}
        </div>
    );
};

export default VideoPlayer;