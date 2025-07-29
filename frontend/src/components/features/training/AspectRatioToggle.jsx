import React from 'react';

const AspectRatioToggle = ({
    naturalAspectRatio,
    currentDisplayMode,
    onDisplayModeChange,
    videoDimensions = { width: 0, height: 0 },
    isForced = false,
    className = ''
}) => {
    // Available display modes
    const displayModes = [
        {
            key: 'auto',
            label: 'Auto',
            icon: '🎬',
            description: 'Original ratio',
            shortDesc: 'Native'
        },
        {
            key: 'landscape',
            label: 'Landscape',
            icon: '🖥️',
            description: 'YouTube style',
            shortDesc: '16:9'
        },
        {
            key: 'portrait',
            label: 'Portrait',
            icon: '📱',
            description: 'TikTok style',
            shortDesc: '9:16'
        },
        {
            key: 'square',
            label: 'Square',
            icon: '📷',
            description: 'Instagram style',
            shortDesc: '1:1'
        }
    ];

    // Get effective aspect ratio info
    const getEffectiveAspectRatio = () => {
        if (currentDisplayMode === 'auto') {
            return naturalAspectRatio;
        }
        return currentDisplayMode;
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

    const aspectInfo = getAspectRatioInfo();

    return (
        <div className={`aspect-ratio-controls ${className}`}>
            <div className="controls-header">
                <h3>📐 Display Mode</h3>
                <p>Choose how to display this video</p>
            </div>

            <div className="display-mode-buttons">
                {displayModes.map(mode => (
                    <button
                        key={mode.key}
                        className={`display-mode-btn ${currentDisplayMode === mode.key ? 'active' : ''}`}
                        onClick={() => onDisplayModeChange(mode.key)}
                        title={`Switch to ${mode.description}`}
                        aria-label={`Display video in ${mode.label} mode (${mode.description})`}
                    >
                        <span className="mode-icon" role="img" aria-hidden="true">
                            {mode.icon}
                        </span>
                        <span className="mode-label">{mode.label}</span>
                        <span className="mode-description">{mode.shortDesc}</span>
                    </button>
                ))}
            </div>

            {/* Current Mode Indicator */}
            <div className="current-mode-info">
                <div className="mode-indicator">
                    <span className="indicator-icon" role="img" aria-hidden="true">
                        {aspectInfo.icon}
                    </span>
                    <div className="indicator-text">
                        <strong>Current: {aspectInfo.label}</strong>
                        <span>{aspectInfo.description}</span>
                    </div>
                </div>

                {isForced && (
                    <div className="mode-warning" role="alert">
                        ⚠️ Forced aspect ratio - video may be cropped or letterboxed
                    </div>
                )}
            </div>

            {/* Additional Technical Info */}
            {videoDimensions.width > 0 && (
                <div className="technical-info">
                    <div className="tech-info-item">
                        <strong>Original:</strong> {videoDimensions.width}×{videoDimensions.height}
                        ({(videoDimensions.width / videoDimensions.height).toFixed(2)})
                    </div>
                    {isForced && (
                        <div className="tech-info-item">
                            <strong>Display:</strong> {aspectInfo.description} ({aspectInfo.ratio})
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

// Quick Toggle Bar Component (for minimal UI)
export const AspectRatioQuickToggle = ({
    currentDisplayMode,
    onDisplayModeChange,
    showLabels = false,
    size = 'normal' // 'small', 'normal', 'large'
}) => {
    const displayModes = [
        { key: 'auto', icon: '🎬', label: 'Auto' },
        { key: 'landscape', icon: '🖥️', label: 'Landscape' },
        { key: 'portrait', icon: '📱', label: 'Portrait' },
        { key: 'square', icon: '📷', label: 'Square' }
    ];

    const sizeClasses = {
        small: 'quick-toggle-small',
        normal: 'quick-toggle-normal',
        large: 'quick-toggle-large'
    };

    return (
        <div className={`aspect-ratio-quick-toggle ${sizeClasses[size]}`}>
            {displayModes.map(mode => (
                <button
                    key={mode.key}
                    className={`quick-toggle-btn ${currentDisplayMode === mode.key ? 'active' : ''}`}
                    onClick={() => onDisplayModeChange(mode.key)}
                    title={`Switch to ${mode.label} mode`}
                    aria-label={`${mode.label} display mode`}
                >
                    <span className="quick-icon" role="img" aria-hidden="true">
                        {mode.icon}
                    </span>
                    {showLabels && (
                        <span className="quick-label">{mode.label}</span>
                    )}
                </button>
            ))}
        </div>
    );
};

// Hook for managing aspect ratio state (for advanced usage)
export const useAspectRatioToggle = (initialMode = 'auto') => {
    const [displayMode, setDisplayMode] = React.useState(initialMode);
    const [naturalAspectRatio, setNaturalAspectRatio] = React.useState('auto');
    const [videoDimensions, setVideoDimensions] = React.useState({ width: 0, height: 0 });

    // Handle video metadata loaded
    const handleVideoMetadata = (videoElement) => {
        const { videoWidth, videoHeight } = videoElement;
        setVideoDimensions({ width: videoWidth, height: videoHeight });

        // Calculate aspect ratio
        const aspectRatio = videoWidth / videoHeight;

        let detectedRatio;
        if (Math.abs(aspectRatio - 1) < 0.1) {
            detectedRatio = 'square';
        } else if (aspectRatio < 0.8) {
            detectedRatio = 'portrait';
        } else if (aspectRatio > 1.5) {
            detectedRatio = 'landscape';
        } else {
            detectedRatio = 'auto';
        }

        setNaturalAspectRatio(detectedRatio);
        console.log(`🎭 Video aspect ratio detected: ${detectedRatio} (${aspectRatio.toFixed(2)})`);
    };

    // Get effective display mode
    const getEffectiveDisplayMode = () => {
        return displayMode === 'auto' ? naturalAspectRatio : displayMode;
    };

    // Check if mode is forced
    const isForced = displayMode !== 'auto' && naturalAspectRatio !== displayMode;

    return {
        displayMode,
        setDisplayMode,
        naturalAspectRatio,
        videoDimensions,
        handleVideoMetadata,
        getEffectiveDisplayMode,
        isForced
    };
};

export default AspectRatioToggle;