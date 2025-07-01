import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import ExerciseBrowser from '../components/features/exercises/ExerciseBrowser';
import LoadingSpinner from '../components/common/LoadingSpinner';
import wgerService from '../services/wgerService';
import workoutService from '../services/workoutService'; // <-- ADD THIS IMPORT

const Exercises = () => {
    const { isAuthenticated } = useAuth();
    const [connectionStatus, setConnectionStatus] = useState(null);
    const [apiStats, setApiStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('browse');

    useEffect(() => {
        checkConnection();
    }, []);

    const checkConnection = async () => {
        try {
            setLoading(true);
            const result = await wgerService.testConnection();
            setConnectionStatus(result);

            if (result.success && result.api_stats) {
                setApiStats(result.api_stats);
            }
        } catch (error) {
            setConnectionStatus({
                success: false,
                message: `Connection failed: ${error.message}`
            });
        } finally {
            setLoading(false);
        }
    };

    const clearCache = async () => {
        if (!isAuthenticated) return;

        try {
            const result = await wgerService.clearCache();
            if (result.success) {
                alert('Cache cleared successfully!');
                // Refresh connection status
                await checkConnection();
            } else {
                alert(`Failed to clear cache: ${result.error}`);
            }
        } catch (error) {
            alert(`Error clearing cache: ${error.message}`);
        }
    };

    if (loading) {
        return (
            <div className="exercises-page-loading">
                <LoadingSpinner />
                <p>Connecting to exercise database...</p>
            </div>
        );
    }

    if (!connectionStatus?.success) {
        return (
            <div className="exercises-page-error">
                <div className="error-content">
                    <h2>Exercise Database Unavailable</h2>
                    <p>{connectionStatus?.message || 'Failed to connect to exercise database'}</p>
                    <button onClick={checkConnection} className="btn btn-primary">
                        Try Again
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="exercises-page">
            <div className="exercises-header">
                <div className="exercises-title">
                    <h1>Exercise Database</h1>
                    <p>Powered by wger - The open source workout manager</p>
                </div>

                {apiStats && (
                    <div className="api-stats">
                        <div className="stat-item">
                            <span className="stat-number">{apiStats.total_exercises?.toLocaleString()}</span>
                            <span className="stat-label">Exercises</span>
                        </div>
                        <div className="stat-item">
                            <span className="stat-number">{apiStats.total_categories}</span>
                            <span className="stat-label">Categories</span>
                        </div>
                        <div className="stat-item">
                            <span className="stat-number">{apiStats.total_muscles}</span>
                            <span className="stat-label">Muscle Groups</span>
                        </div>
                        <div className="stat-item">
                            <span className="stat-number">{apiStats.total_equipment}</span>
                            <span className="stat-label">Equipment Types</span>
                        </div>
                    </div>
                )}
            </div>

            <div className="exercises-tabs">
                <div className="tab-buttons">
                    <button
                        onClick={() => setActiveTab('browse')}
                        className={`tab-button ${activeTab === 'browse' ? 'active' : ''}`}
                    >
                        Browse Exercises
                    </button>

                    {isAuthenticated && (
                        <>
                            <button
                                onClick={() => setActiveTab('favorites')}
                                className={`tab-button ${activeTab === 'favorites' ? 'active' : ''}`}
                            >
                                My Favorites
                            </button>
                            <button
                                onClick={() => setActiveTab('workouts')}
                                className={`tab-button ${activeTab === 'workouts' ? 'active' : ''}`}
                            >
                                My Workouts
                            </button>
                        </>
                    )}

                    <button
                        onClick={() => setActiveTab('about')}
                        className={`tab-button ${activeTab === 'about' ? 'active' : ''}`}
                    >
                        About
                    </button>
                </div>

                <div className="tab-content">
                    {activeTab === 'browse' && (
                        <div className="tab-pane">
                            <ExerciseBrowser />
                        </div>
                    )}

                    {activeTab === 'favorites' && isAuthenticated && (
                        <div className="tab-pane">
                            <FavoritesTab />
                        </div>
                    )}

                    {activeTab === 'workouts' && isAuthenticated && (
                        <div className="tab-pane">
                            <WorkoutsTab />
                        </div>
                    )}

                    {activeTab === 'about' && (
                        <div className="tab-pane">
                            <AboutTab
                                connectionStatus={connectionStatus}
                                apiStats={apiStats}
                                onClearCache={clearCache}
                                isAuthenticated={isAuthenticated}
                            />
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

// FIXED Favorites Tab Component
const FavoritesTab = () => {
    const [favorites, setFavorites] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        loadFavorites();
    }, []);

    const loadFavorites = async () => {
        try {
            setLoading(true);
            setError(null);
            // FIXED: Use correct method name from workoutService
            const result = await workoutService.getFavorites();
            if (result.success) {
                setFavorites(result.favorites || []);
            } else {
                setError(result.error || 'Failed to load favorites');
            }
        } catch (error) {
            console.error('Error loading favorites:', error);
            setError(error.message);
        } finally {
            setLoading(false);
        }
    };

    const removeFromFavorites = async (exerciseId) => {
        try {
            const result = await workoutService.removeFromFavorites(exerciseId);
            if (result.success) {
                // Remove from local state
                setFavorites(favorites.filter(fav => fav.exercise_id !== exerciseId));
            } else {
                alert('Failed to remove from favorites');
            }
        } catch (error) {
            console.error('Error removing from favorites:', error);
            alert('Error removing from favorites');
        }
    };

    if (loading) {
        return <LoadingSpinner />;
    }

    if (error) {
        return (
            <div className="error-state">
                <p>Error loading favorites: {error}</p>
                <button onClick={loadFavorites} className="btn btn-primary">
                    Try Again
                </button>
            </div>
        );
    }

    return (
        <div className="favorites-tab">
            <div className="favorites-header">
                <h2>My Favorite Exercises</h2>
                <p className="favorites-count">
                    {favorites.length} favorite{favorites.length !== 1 ? 's' : ''}
                </p>
            </div>

            {favorites.length === 0 ? (
                <div className="empty-state">
                    <p>You haven't favorited any exercises yet.</p>
                    <p>Browse exercises and click the heart icon to add them to your favorites!</p>
                </div>
            ) : (
                <div className="favorites-grid">
                    {favorites.map((favorite) => (
                        <div key={favorite.id} className="favorite-card">
                            <div className="favorite-header">
                                <h3>{favorite.exercise_name}</h3>
                                <button
                                    onClick={() => removeFromFavorites(favorite.exercise_id)}
                                    className="btn btn-danger btn-sm"
                                    title="Remove from favorites"
                                >
                                    ❤️ Remove
                                </button>
                            </div>

                            {favorite.exercise_category && (
                                <p className="exercise-category">
                                    Category: {favorite.exercise_category}
                                </p>
                            )}

                            {favorite.exercise_muscles && favorite.exercise_muscles.length > 0 && (
                                <div className="muscle-groups">
                                    <strong>Muscles:</strong>
                                    <div className="muscle-tags">
                                        {favorite.exercise_muscles.map((muscle, index) => (
                                            <span key={index} className="muscle-tag">
                                                {muscle}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {favorite.exercise_equipment && favorite.exercise_equipment.length > 0 && (
                                <div className="equipment-needed">
                                    <strong>Equipment:</strong>
                                    <div className="equipment-tags">
                                        {favorite.exercise_equipment.map((equipment, index) => (
                                            <span key={index} className="equipment-tag">
                                                {equipment}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            <p className="added-date">
                                Added: {new Date(favorite.created_at).toLocaleDateString()}
                            </p>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

// FIXED Workouts Tab Component
const WorkoutsTab = () => {
    const [workouts, setWorkouts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [newWorkoutName, setNewWorkoutName] = useState('');
    const [newWorkoutDescription, setNewWorkoutDescription] = useState('');

    useEffect(() => {
        loadWorkouts();
    }, []);

    const loadWorkouts = async () => {
        try {
            setLoading(true);
            setError(null);
            // FIXED: Use correct method name from workoutService
            const result = await workoutService.getWorkoutPlans();
            if (result.success) {
                setWorkouts(result.workout_plans || []);
            } else {
                setError(result.error || 'Failed to load workout plans');
            }
        } catch (error) {
            console.error('Error loading workouts:', error);
            setError(error.message);
        } finally {
            setLoading(false);
        }
    };

    const createWorkout = async () => {
        if (!newWorkoutName.trim()) {
            alert('Please enter a workout name');
            return;
        }

        try {
            // FIXED: Use correct method signature (name, description) instead of object
            const result = await workoutService.createWorkoutPlan(
                newWorkoutName.trim(),
                newWorkoutDescription.trim()
            );

            if (result.success) {
                setWorkouts([result.workout_plan, ...workouts]);
                setNewWorkoutName('');
                setNewWorkoutDescription('');
                setShowCreateForm(false);
            } else {
                alert('Failed to create workout plan');
            }
        } catch (error) {
            console.error('Error creating workout:', error);
            alert('Error creating workout plan');
        }
    };

    if (loading) {
        return <LoadingSpinner />;
    }

    if (error) {
        return (
            <div className="error-state">
                <p>Error loading workouts: {error}</p>
                <button onClick={loadWorkouts} className="btn btn-primary">
                    Try Again
                </button>
            </div>
        );
    }

    return (
        <div className="workouts-tab">
            <div className="workouts-header">
                <h2>My Workout Plans</h2>
                <button
                    className="btn btn-primary"
                    onClick={() => setShowCreateForm(!showCreateForm)}
                >
                    {showCreateForm ? 'Cancel' : 'Create New Workout'}
                </button>
            </div>

            {showCreateForm && (
                <div className="create-workout-form">
                    <h3>Create New Workout Plan</h3>
                    <input
                        type="text"
                        placeholder="Workout name"
                        value={newWorkoutName}
                        onChange={(e) => setNewWorkoutName(e.target.value)}
                        className="form-input"
                    />
                    <textarea
                        placeholder="Description (optional)"
                        value={newWorkoutDescription}
                        onChange={(e) => setNewWorkoutDescription(e.target.value)}
                        className="form-textarea"
                        rows="3"
                    />
                    <div className="form-buttons">
                        <button onClick={createWorkout} className="btn btn-primary">
                            Create Workout
                        </button>
                        <button
                            onClick={() => setShowCreateForm(false)}
                            className="btn btn-secondary"
                        >
                            Cancel
                        </button>
                    </div>
                </div>
            )}

            {workouts.length === 0 ? (
                <div className="empty-state">
                    <p>You don't have any workout plans yet.</p>
                    <p>Create custom workouts using exercises from our database!</p>
                </div>
            ) : (
                <div className="workouts-grid">
                    {workouts.map((workout) => (
                        <div key={workout.id} className="workout-card">
                            <div className="workout-header">
                                <h3>{workout.name}</h3>
                                <span className="exercise-count">
                                    {workout.exercise_count} exercise{workout.exercise_count !== 1 ? 's' : ''}
                                </span>
                            </div>

                            {workout.description && (
                                <p className="workout-description">{workout.description}</p>
                            )}

                            {workout.exercises && workout.exercises.length > 0 && (
                                <div className="workout-exercises">
                                    <strong>Exercises:</strong>
                                    <ul>
                                        {workout.exercises.slice(0, 3).map((exercise) => (
                                            <li key={exercise.id}>
                                                {exercise.exercise_name}
                                                {exercise.sets && exercise.reps && (
                                                    <span className="exercise-details">
                                                        ({exercise.sets} sets × {exercise.reps})
                                                    </span>
                                                )}
                                            </li>
                                        ))}
                                        {workout.exercises.length > 3 && (
                                            <li>+ {workout.exercises.length - 3} more exercises</li>
                                        )}
                                    </ul>
                                </div>
                            )}

                            <div className="workout-meta">
                                <p className="created-date">
                                    Created: {new Date(workout.created_at).toLocaleDateString()}
                                </p>
                                <p className="updated-date">
                                    Updated: {new Date(workout.updated_at).toLocaleDateString()}
                                </p>
                            </div>

                            <div className="workout-actions">
                                <button className="btn btn-primary btn-sm">
                                    View Details
                                </button>
                                <button className="btn btn-secondary btn-sm">
                                    Start Workout
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

// About Tab Component (unchanged)
const AboutTab = ({ connectionStatus, apiStats, onClearCache, isAuthenticated }) => {
    return (
        <div className="about-tab">
            <h2>About the Exercise Database</h2>

            <div className="about-section">
                <h3>wger Integration</h3>
                <p>
                    DojoTracker integrates with <a href="https://wger.de" target="_blank" rel="noopener noreferrer">wger</a>,
                    a free and open-source workout manager. This gives you access to hundreds of professionally
                    curated exercises with detailed descriptions, muscle group information, and equipment requirements.
                </p>

                <div className="integration-status">
                    <h4>Connection Status</h4>
                    <div className={`status-indicator ${connectionStatus?.success ? 'success' : 'error'}`}>
                        <span className="status-icon">
                            {connectionStatus?.success ? '✅' : '❌'}
                        </span>
                        <span className="status-text">
                            {connectionStatus?.message || 'Unknown status'}
                        </span>
                    </div>

                    {connectionStatus?.response_time && (
                        <p className="response-time">
                            Response time: {connectionStatus.response_time}s
                        </p>
                    )}
                </div>
            </div>

            {apiStats && (
                <div className="about-section">
                    <h3>Database Statistics</h3>
                    <div className="stats-grid">
                        <div className="stat-card">
                            <h4>Exercises Available</h4>
                            <p className="big-number">{apiStats.total_exercises?.toLocaleString()}</p>
                        </div>
                        <div className="stat-card">
                            <h4>Exercise Categories</h4>
                            <p className="big-number">{apiStats.total_categories}</p>
                            <div className="category-list">
                                {apiStats.categories?.slice(0, 5).map((cat, index) => (
                                    <span key={index} className="category-tag">{cat}</span>
                                ))}
                                {apiStats.categories?.length > 5 && (
                                    <span className="category-tag">+{apiStats.categories.length - 5} more</span>
                                )}
                            </div>
                        </div>
                        <div className="stat-card">
                            <h4>Muscle Groups</h4>
                            <p className="big-number">{apiStats.total_muscles}</p>
                        </div>
                        <div className="stat-card">
                            <h4>Equipment Types</h4>
                            <p className="big-number">{apiStats.total_equipment}</p>
                        </div>
                    </div>
                </div>
            )}

            <div className="about-section">
                <h3>Features</h3>
                <ul className="feature-list">
                    <li>🔍 Search through thousands of exercises</li>
                    <li>🏷️ Filter by category, muscle group, and equipment</li>
                    <li>📝 Detailed exercise descriptions and instructions</li>
                    <li>💪 Muscle group targeting information</li>
                    <li>⚡ Difficulty level indicators</li>
                    {isAuthenticated && (
                        <>
                            <li>❤️ Save favorite exercises</li>
                            <li>📋 Create custom workout plans</li>
                            <li>📊 Track exercise progress</li>
                        </>
                    )}
                </ul>
            </div>

            {isAuthenticated && (
                <div className="about-section">
                    <h3>Cache Management</h3>
                    <p>
                        Exercise data is cached to improve performance. Clear the cache if you're
                        experiencing issues or want to fetch the latest data.
                    </p>
                    <button onClick={onClearCache} className="btn btn-secondary">
                        Clear Exercise Cache
                    </button>
                </div>
            )}

            <div className="about-section">
                <h3>Attribution</h3>
                <p>
                    Exercise data is provided by the <a href="https://wger.de" target="_blank" rel="noopener noreferrer">wger</a> project,
                    licensed under AGPL 3+ and CC-BY-SA 3.0. We're grateful to the wger community for
                    making this comprehensive exercise database freely available.
                </p>
            </div>
        </div>
    );
};

export default Exercises;