import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import ExerciseBrowser from '../components/features/exercises/ExerciseBrowser';
import LoadingSpinner from '../components/common/LoadingSpinner';
import wgerService from '../services/wgerService';

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

// Favorites Tab Component
const FavoritesTab = () => {
    const [favorites, setFavorites] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadFavorites();
    }, []);

    const loadFavorites = async () => {
        try {
            const result = await wgerService.getUserFavorites();
            if (result.success) {
                setFavorites(result.favorites);
            }
        } catch (error) {
            console.error('Error loading favorites:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <LoadingSpinner />;
    }

    return (
        <div className="favorites-tab">
            <h2>My Favorite Exercises</h2>
            {favorites.length === 0 ? (
                <div className="empty-state">
                    <p>You haven't favorited any exercises yet.</p>
                    <p>Browse exercises and click the heart icon to add them to your favorites!</p>
                </div>
            ) : (
                <div className="favorites-grid">
                    {/* Exercise cards would go here */}
                </div>
            )}
        </div>
    );
};

// Workouts Tab Component
const WorkoutsTab = () => {
    const [workouts, setWorkouts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadWorkouts();
    }, []);

    const loadWorkouts = async () => {
        try {
            const result = await wgerService.getUserWorkoutPlans();
            if (result.success) {
                setWorkouts(result.workout_plans);
            }
        } catch (error) {
            console.error('Error loading workouts:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <LoadingSpinner />;
    }

    return (
        <div className="workouts-tab">
            <div className="workouts-header">
                <h2>My Workout Plans</h2>
                <button className="btn btn-primary">
                    Create New Workout
                </button>
            </div>

            {workouts.length === 0 ? (
                <div className="empty-state">
                    <p>You don't have any workout plans yet.</p>
                    <p>Create custom workouts using exercises from our database!</p>
                </div>
            ) : (
                <div className="workouts-grid">
                    {/* Workout plan cards would go here */}
                </div>
            )}
        </div>
    );
};

// About Tab Component
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