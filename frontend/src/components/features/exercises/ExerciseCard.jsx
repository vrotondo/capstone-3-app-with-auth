import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import wgerService from '../../services/wgerService';

const ExerciseCard = ({ exercise, difficulty, categoryIcon }) => {
    const { isAuthenticated } = useAuth();
    const [isFavorited, setIsFavorited] = useState(false);
    const [isExpanded, setIsExpanded] = useState(false);
    const [loading, setLoading] = useState(false);

    const handleFavoriteToggle = async () => {
        if (!isAuthenticated) return;

        try {
            setLoading(true);

            if (isFavorited) {
                const result = await wgerService.removeFromFavorites(exercise.id);
                if (result.success) {
                    setIsFavorited(false);
                }
            } else {
                const result = await wgerService.addToFavorites(exercise.id);
                if (result.success) {
                    setIsFavorited(true);
                }
            }
        } catch (error) {
            console.error('Error toggling favorite:', error);
        } finally {
            setLoading(false);
        }
    };

    const getDifficultyColor = (diff) => {
        switch (diff) {
            case 'Beginner': return '#22c55e';
            case 'Intermediate': return '#f59e0b';
            case 'Advanced': return '#ef4444';
            default: return '#6b7280';
        }
    };

    return (
        <div className="exercise-card">
            <div className="exercise-card-header">
                <div className="exercise-category">
                    <span className="category-icon">{categoryIcon}</span>
                    <span className="category-name">{exercise.category}</span>
                </div>

                {isAuthenticated && (
                    <button
                        onClick={handleFavoriteToggle}
                        disabled={loading}
                        className={`favorite-btn ${isFavorited ? 'favorited' : ''}`}
                        title={isFavorited ? 'Remove from favorites' : 'Add to favorites'}
                    >
                        {loading ? '⏳' : isFavorited ? '❤️' : '🤍'}
                    </button>
                )}
            </div>

            <div className="exercise-card-body">
                <h3 className="exercise-name">{exercise.name}</h3>

                <div className="exercise-difficulty">
                    <span
                        className="difficulty-badge"
                        style={{ backgroundColor: getDifficultyColor(difficulty) }}
                    >
                        {difficulty}
                    </span>
                </div>

                <div className="exercise-description">
                    {exercise.description ? (
                        isExpanded ? (
                            exercise.description
                        ) : (
                            `${exercise.description.slice(0, 100)}${exercise.description.length > 100 ? '...' : ''}`
                        )
                    ) : (
                        'No description available'
                    )}

                    {exercise.description && exercise.description.length > 100 && (
                        <button
                            onClick={() => setIsExpanded(!isExpanded)}
                            className="expand-btn"
                        >
                            {isExpanded ? 'Show less' : 'Show more'}
                        </button>
                    )}
                </div>

                {exercise.muscles.length > 0 && (
                    <div className="exercise-muscles">
                        <h4>Primary Muscles:</h4>
                        <div className="muscle-tags">
                            {exercise.muscles.map((muscle, index) => (
                                <span key={index} className="muscle-tag">
                                    {muscle}
                                </span>
                            ))}
                        </div>
                    </div>
                )}

                {exercise.equipment.length > 0 && (
                    <div className="exercise-equipment">
                        <h4>Equipment:</h4>
                        <div className="equipment-tags">
                            {exercise.equipment.map((eq, index) => (
                                <span key={index} className="equipment-tag">
                                    {eq}
                                </span>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            <div className="exercise-card-footer">
                <button
                    onClick={() => window.open(`https://wger.de/en/exercise/${exercise.id}`, '_blank')}
                    className="btn btn-secondary btn-sm"
                >
                    View Details
                </button>

                {isAuthenticated && (
                    <button className="btn btn-primary btn-sm">
                        Add to Workout
                    </button>
                )}
            </div>
        </div>
    );
};