import React, { useState, useEffect, useRef } from 'react';

const ProfessionalVideoControls = ({ videoRef }) => {
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);
    const [volume, setVolume] = useState(1);
    const [isMuted, setIsMuted] = useState(false);
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [showControls, setShowControls] = useState(true);
    const [playbackRate, setPlaybackRate] = useState(1);
    const [isBuffering, setIsBuffering] = useState(false);

    const controlsTimeoutRef = useRef(null);
    const progressRef = useRef(null);

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

    // Video event listeners
    useEffect(() => {
        const video = videoRef.current;
        if (!video) return;

        const handleLoadedMetadata = () => {
            setDuration(video.duration);
            setVolume(video.volume);
            setIsMuted(video.muted);
        };

        const handleTimeUpdate = () => {
            setCurrentTime(video.currentTime);
        };

        const handlePlay = () => setIsPlaying(true);
        const handlePause = () => setIsPlaying(false);
        const handleVolumeChange = () => {
            setVolume(video.volume);
            setIsMuted(video.muted);
        };

        const handleWaiting = () => setIsBuffering(true);
        const handleCanPlay = () => setIsBuffering(false);

        const handleFullscreenChange = () => {
            setIsFullscreen(!!document.fullscreenElement);
        };

        // Add event listeners
        video.addEventListener('loadedmetadata', handleLoadedMetadata);
        video.addEventListener('timeupdate', handleTimeUpdate);
        video.addEventListener('play', handlePlay);
        video.addEventListener('pause', handlePause);
        video.addEventListener('volumechange', handleVolumeChange);
        video.addEventListener('waiting', handleWaiting);
        video.addEventListener('canplay', handleCanPlay);
        document.addEventListener('fullscreenchange', handleFullscreenChange);

        // Cleanup
        return () => {
            video.removeEventListener('loadedmetadata', handleLoadedMetadata);
            video.removeEventListener('timeupdate', handleTimeUpdate);
            video.removeEventListener('play', handlePlay);
            video.removeEventListener('pause', handlePause);
            video.removeEventListener('volumechange', handleVolumeChange);
            video.removeEventListener('waiting', handleWaiting);
            video.removeEventListener('canplay', handleCanPlay);
            document.removeEventListener('fullscreenchange', handleFullscreenChange);
        };
    }, [videoRef]);

    const togglePlayPause = () => {
        const video = videoRef.current;
        if (!video) return;

        if (isPlaying) {
            video.pause();
        } else {
            video.play();
        }
    };

    const handleSeek = (e) => {
        const video = videoRef.current;
        if (!video || !progressRef.current) return;

        const rect = progressRef.current.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const newTime = (clickX / rect.width) * duration;

        video.currentTime = newTime;
        setCurrentTime(newTime);
    };

    const handleVolumeChange = (e) => {
        const video = videoRef.current;
        if (!video) return;

        const newVolume = parseFloat(e.target.value);
        video.volume = newVolume;
        setVolume(newVolume);
        setIsMuted(newVolume === 0);
    };

    const toggleMute = () => {
        const video = videoRef.current;
        if (!video) return;

        const newMuted = !isMuted;
        video.muted = newMuted;
        setIsMuted(newMuted);
    };

    const changePlaybackRate = (rate) => {
        const video = videoRef.current;
        if (!video) return;

        video.playbackRate = rate;
        setPlaybackRate(rate);
    };

    const toggleFullscreen = () => {
        const video = videoRef.current;
        if (!video) return;

        if (!isFullscreen) {
            if (video.requestFullscreen) {
                video.requestFullscreen();
            } else if (video.webkitRequestFullscreen) {
                video.webkitRequestFullscreen();
            }
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
            }
        }
    };

    const skip = (seconds) => {
        const video = videoRef.current;
        if (!video) return;

        video.currentTime = Math.max(0, Math.min(duration, video.currentTime + seconds));
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

    return (
        <div
            className={`professional-video-controls ${showControls ? 'show' : 'hide'}`}
            onMouseMove={() => setShowControls(true)}
        >
            {/* Buffering Indicator */}
            {isBuffering && (
                <div className="buffering-indicator">
                    <div className="buffering-spinner"></div>
                </div>
            )}

            {/* Center Play/Pause Button */}
            <div
                className="center-play-button"
                onClick={togglePlayPause}
                style={{
                    display: !isPlaying && showControls ? 'flex' : 'none'
                }}
            >
                <div className="center-play-icon">▶</div>
            </div>

            {/* Skip Buttons */}
            <div className="skip-buttons">
                <button
                    className="skip-btn skip-backward"
                    onClick={() => skip(-10)}
                    title="Skip backward 10s"
                >
                    <span className="skip-icon">⏪</span>
                    <span className="skip-time">10</span>
                </button>
                <button
                    className="skip-btn skip-forward"
                    onClick={() => skip(10)}
                    title="Skip forward 10s"
                >
                    <span className="skip-icon">⏩</span>
                    <span className="skip-time">10</span>
                </button>
            </div>

            {/* Bottom Controls */}
            <div className="bottom-controls">
                {/* Progress Bar */}
                <div
                    className="progress-container"
                    ref={progressRef}
                    onClick={handleSeek}
                >
                    <div className="progress-bar">
                        <div
                            className="progress-fill"
                            style={{ width: `${(currentTime / duration) * 100}%` }}
                        />
                        <div
                            className="progress-thumb"
                            style={{ left: `${(currentTime / duration) * 100}%` }}
                        />
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
                                step="0.05"
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
                                <option value={0.25}>0.25x</option>
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
                            {isFullscreen ? '⛶' : '⛶'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ProfessionalVideoControls;