// frontend/src/components/features/techniques/TechniqueCard.jsx
import React from 'react';
import Button from '../../common/Button';

const TechniqueCard = ({
    technique,
    user,
    onToggleBookmark,
    onViewDetails,
    isBookmarked = false
}) => {
    const handleBookmarkClick = (e) => {
        e.stopPropagation();
        if (onToggleBookmark) {
            onToggleBookmark(technique.id, technique.is_bookmarked);
        }
    };

    const handleViewDetails = () => {
        if (onViewDetails) {
            onViewDetails(technique.id);
        }
    };

    return (
        <div className="technique-card">
            <div className="technique-header">
                <h3>{technique.name}</h3>
                <div className="technique-badges">
                    {technique.difficulty_level && (
                        <span className="difficulty-badge">
                            Level {technique.difficulty_level}/10
                        </span>
                    )}
                    {user && (
                        <button
                            onClick={handleBookmarkClick}
                            className={`bookmark-btn ${technique.is_bookmarked ? 'bookmarked' : ''}`}
                            title={technique.is_bookmarked ? 'Remove bookmark' : 'Add bookmark'}
                        >
                            ♥
                        </button>
                    )}
                </div>
            </div>

            <div className="technique-meta">
                <span className="technique-style">{technique.style}</span>
                {technique.category && (
                    <span className="technique-category">{technique.category}</span>
                )}
            </div>

            {technique.description && (
                <p className="technique-description">
                    {technique.description.length > 150
                        ? `${technique.description.substring(0, 150)}...`
                        : technique.description
                    }
                </p>
            )}

            <div className="technique-stats">
                <span>👁 {technique.view_count || 0}</span>
                <span>♥ {technique.bookmark_count || 0}</span>
            </div>

            <div className="technique-actions">
                <Button
                    variant="outline"
                    size="sm"
                    onClick={handleViewDetails}
                >
                    View Details
                </Button>
            </div>
        </div>
    );
};

export default TechniqueCard;