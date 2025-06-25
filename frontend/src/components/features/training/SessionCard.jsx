import React, { useState } from 'react';
import { format } from 'date-fns';
import Button from '../../common/Button';
import trainingService from '../../../services/trainingService';

const SessionCard = ({ session, onEdit, onDelete }) => {
    const [isDeleting, setIsDeleting] = useState(false);
    const [showDetails, setShowDetails] = useState(false);

    const handleDelete = async () => {
        if (window.confirm('Are you sure you want to delete this training session?')) {
            setIsDeleting(true);
            try {
                await onDelete(session.id);
            } finally {
                setIsDeleting(false);
            }
        }
    };

    const formatDate = (dateString) => {
        try {
            return format(new Date(dateString), 'MMM dd, yyyy');
        } catch {
            return dateString;
        }
    };

    const getIntensityColor = (level) => {
        if (level <= 3) return '#10b981'; // green
        if (level <= 6) return '#f59e0b'; // yellow
        if (level <= 8) return '#f97316'; // orange
        return '#ef4444'; // red
    };

    return (
        <div className="session-card card">
            <div className="card-header">
                <div className="session-header-info">
                    <h3 className="card-title">{session.style}</h3>
                    <p className="card-subtitle">{formatDate(session.date)}</p>
                </div>
                <div className="session-duration">
                    <span className="duration-text">
                        {trainingService.formatDuration(session.duration)}
                    </span>
                </div>
            </div>

            <div className="card-content">
                <div className="session-stats">
                    <div className="stat-item">
                        <span className="stat-label">Intensity</span>
                        <div className="intensity-indicator">
                            <div
                                className="intensity-bar"
                                style={{
                                    width: `${session.intensity_level * 10}%`,
                                    backgroundColor: getIntensityColor(session.intensity_level)
                                }}
                            />
                            <span className="intensity-text">{session.intensity_level}/10</span>
                        </div>
                    </div>

                    {(session.energy_before || session.energy_after) && (
                        <div className="stat-item">
                            <span className="stat-label">Energy</span>
                            <div className="energy-levels">
                                {session.energy_before && (
                                    <span className="energy-item">
                                        Before: {session.energy_before}/10
                                    </span>
                                )}
                                {session.energy_after && (
                                    <span className="energy-item">
                                        After: {session.energy_after}/10
                                    </span>
                                )}
                            </div>
                        </div>
                    )}

                    {session.mood && (
                        <div className="stat-item">
                            <span className="stat-label">Mood</span>
                            <span className="stat-value">{session.mood}</span>
                        </div>
                    )}
                </div>

                {session.techniques_practiced && session.techniques_practiced.length > 0 && (
                    <div className="techniques-section">
                        <span className="techniques-label">Techniques:</span>
                        <div className="technique-tags">
                            {session.techniques_practiced.slice(0, 3).map((technique, index) => (
                                <span key={index} className="technique-tag small">
                                    {technique}
                                </span>
                            ))}
                            {session.techniques_practiced.length > 3 && (
                                <span className="technique-more">
                                    +{session.techniques_practiced.length - 3} more
                                </span>
                            )}
                        </div>
                    </div>
                )}

                {showDetails && (
                    <div className="session-details">
                        {session.notes && (
                            <div className="detail-item">
                                <strong>Notes:</strong>
                                <p>{session.notes}</p>
                            </div>
                        )}

                        {session.techniques_practiced && session.techniques_practiced.length > 3 && (
                            <div className="detail-item">
                                <strong>All Techniques:</strong>
                                <div className="technique-tags">
                                    {session.techniques_practiced.map((technique, index) => (
                                        <span key={index} className="technique-tag small">
                                            {technique}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}

                        {(session.calories_burned || session.avg_heart_rate || session.max_heart_rate) && (
                            <div className="detail-item">
                                <strong>Fitness Data:</strong>
                                <div className="fitness-stats">
                                    {session.calories_burned && (
                                        <span className="fitness-stat">
                                            🔥 {session.calories_burned} cal
                                        </span>
                                    )}
                                    {session.avg_heart_rate && (
                                        <span className="fitness-stat">
                                            💓 Avg: {session.avg_heart_rate} BPM
                                        </span>
                                    )}
                                    {session.max_heart_rate && (
                                        <span className="fitness-stat">
                                            📈 Max: {session.max_heart_rate} BPM
                                        </span>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>

            <div className="card-footer">
                <div className="card-actions">
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setShowDetails(!showDetails)}
                    >
                        {showDetails ? 'Show Less' : 'Show More'}
                    </Button>
                    <div className="action-buttons">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => onEdit(session)}
                        >
                            Edit
                        </Button>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={handleDelete}
                            loading={isDeleting}
                            className="delete-btn"
                        >
                            Delete
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SessionCard;