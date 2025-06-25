import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Button from '../components/common/Button';
import LoadingSpinner from '../components/common/LoadingSpinner';
import trainingService from '../services/trainingService';

const Dashboard = () => {
    const { user } = useAuth();
    const [stats, setStats] = useState(null);
    const [recentSessions, setRecentSessions] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        loadDashboardData();
    }, []);

    const loadDashboardData = async () => {
        try {
            setIsLoading(true);
            setError('');

            // Load training stats and recent sessions
            const [statsResponse, sessionsResponse] = await Promise.all([
                trainingService.getStats(),
                trainingService.getSessions({ limit: 5 })
            ]);

            setStats(statsResponse);
            setRecentSessions(sessionsResponse.sessions || []);
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            setError('Failed to load dashboard data. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const formatDate = (dateString) => {
        try {
            return new Date(dateString).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric'
            });
        } catch {
            return dateString;
        }
    };

    if (isLoading) {
        return <LoadingSpinner />;
    }

    return (
        <div className="dashboard-page">
            <div className="dashboard-header">
                <h1>Welcome back, {user?.first_name}!</h1>
                <p>Here's your martial arts progress overview</p>
            </div>

            {error && (
                <div className="error-message">
                    {error}
                    <button onClick={() => setError('')} className="error-close">×</button>
                </div>
            )}

            <div className="dashboard-grid">
                {/* Training Stats */}
                <div className="dashboard-card">
                    <h3>Training Overview</h3>
                    {stats ? (
                        <div className="stats-grid">
                            <div className="stat-item">
                                <span className="stat-number">{stats.total_sessions}</span>
                                <span className="stat-label">Total Sessions</span>
                            </div>
                            <div className="stat-item">
                                <span className="stat-number">{stats.total_hours}h</span>
                                <span className="stat-label">Total Hours</span>
                            </div>
                            <div className="stat-item">
                                <span className="stat-number">{stats.avg_intensity}/10</span>
                                <span className="stat-label">Avg Intensity</span>
                            </div>
                        </div>
                    ) : (
                        <p>No training data yet. Start logging your sessions!</p>
                    )}
                    <div className="card-action">
                        <Link to="/training">
                            <Button variant="outline" size="sm">View All Sessions</Button>
                        </Link>
                    </div>
                </div>

                {/* This Week's Progress */}
                <div className="dashboard-card">
                    <h3>This Week</h3>
                    {stats && stats.this_week ? (
                        <div className="week-stats">
                            <div className="week-stat">
                                <span className="week-number">{stats.this_week.sessions}</span>
                                <span className="week-label">Sessions</span>
                            </div>
                            <div className="week-stat">
                                <span className="week-number">{stats.this_week.hours}h</span>
                                <span className="week-label">Training Time</span>
                            </div>
                            {stats.this_week.sessions === 0 && (
                                <p className="motivational-text">
                                    Start your week strong! Log your first session.
                                </p>
                            )}
                        </div>
                    ) : (
                        <p>No training logged this week yet.</p>
                    )}
                    <div className="card-action">
                        <Link to="/training">
                            <Button variant="primary" size="sm">Log Session</Button>
                        </Link>
                    </div>
                </div>

                {/* Techniques Progress */}
                <div className="dashboard-card">
                    <h3>Techniques</h3>
                    {stats && stats.technique_stats ? (
                        <div className="technique-overview">
                            <div className="technique-total">
                                <span className="technique-number">{stats.technique_stats.total_techniques}</span>
                                <span className="technique-label">Total Techniques</span>
                            </div>
                            {stats.technique_stats.mastery_breakdown && Object.keys(stats.technique_stats.mastery_breakdown).length > 0 ? (
                                <div className="mastery-breakdown">
                                    {Object.entries(stats.technique_stats.mastery_breakdown).map(([status, count]) => (
                                        <div key={status} className="mastery-item">
                                            <span className={`mastery-badge ${status}`}>{count}</span>
                                            <span className="mastery-label">{trainingService.getMasteryLabel(status)}</span>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <p>Start building your technique library!</p>
                            )}
                        </div>
                    ) : (
                        <p>No techniques added yet. Build your technique library!</p>
                    )}
                    <div className="card-action">
                        <Link to="/techniques">
                            <Button variant="outline" size="sm">Manage Techniques</Button>
                        </Link>
                    </div>
                </div>

                {/* Martial Arts Styles */}
                <div className="dashboard-card">
                    <h3>Your Styles</h3>
                    {stats && stats.styles_practiced && stats.styles_practiced.length > 0 ? (
                        <div className="styles-list">
                            {stats.styles_practiced.map((style, index) => (
                                <span key={index} className="style-tag">{style}</span>
                            ))}
                        </div>
                    ) : (
                        <p>No martial arts styles recorded yet.</p>
                    )}
                    <div className="card-action">
                        <Link to="/profile">
                            <Button variant="outline" size="sm">Update Profile</Button>
                        </Link>
                    </div>
                </div>
            </div>

            {/* Recent Sessions */}
            {recentSessions.length > 0 && (
                <div className="recent-sessions-section">
                    <div className="section-header">
                        <h2>Recent Training Sessions</h2>
                        <Link to="/training">
                            <Button variant="outline" size="sm">View All</Button>
                        </Link>
                    </div>

                    <div className="recent-sessions-grid">
                        {recentSessions.map((session) => (
                            <div key={session.id} className="recent-session-card">
                                <div className="session-info">
                                    <h4>{session.style}</h4>
                                    <p className="session-date">{formatDate(session.date)}</p>
                                </div>
                                <div className="session-metrics">
                                    <span className="session-duration">
                                        {trainingService.formatDuration(session.duration)}
                                    </span>
                                    <span className="session-intensity">
                                        Intensity: {session.intensity_level}/10
                                    </span>
                                </div>
                                {session.techniques_practiced && session.techniques_practiced.length > 0 && (
                                    <div className="session-techniques">
                                        <span className="techniques-count">
                                            {session.techniques_practiced.length} technique{session.techniques_practiced.length !== 1 ? 's' : ''}
                                        </span>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Quick Actions */}
            <div className="quick-actions-section">
                <h2>Quick Actions</h2>
                <div className="quick-actions-grid">
                    <Link to="/training" className="quick-action-card">
                        <div className="action-icon">🥋</div>
                        <h3>Log Training Session</h3>
                        <p>Record your latest training session</p>
                    </Link>

                    <Link to="/techniques" className="quick-action-card">
                        <div className="action-icon">📚</div>
                        <h3>Add Technique</h3>
                        <p>Track a new technique you're learning</p>
                    </Link>

                    <Link to="/profile" className="quick-action-card">
                        <div className="action-icon">👤</div>
                        <h3>Update Profile</h3>
                        <p>Manage your account settings</p>
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;