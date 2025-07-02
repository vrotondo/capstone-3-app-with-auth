import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Button from '../components/common/Button';
import LoadingSpinner from '../components/common/LoadingSpinner';
import AIInsights from '../components/AIInsights';
import AIChatCoach, { AIChatToggle } from '../components/AIChatCoach'; // NEW
import trainingService from '../services/trainingService';
import "../styles/pages/dashboard.css";

const Dashboard = () => {
    const { user } = useAuth();
    const [stats, setStats] = useState(null);
    const [recentSessions, setRecentSessions] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');
    const [showAIChat, setShowAIChat] = useState(false); // NEW

    useEffect(() => {
        loadDashboardData();
    }, []);

    const loadDashboardData = async () => {
        try {
            setIsLoading(true);
            setError('');

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
                <p>Here's your martial arts progress overview with AI-powered insights</p>
            </div>

            {error && (
                <div className="error-message">
                    {error}
                    <button onClick={() => setError('')} className="error-close">×</button>
                </div>
            )}

            <div className="dashboard-grid">
                {/* Your existing dashboard cards */}
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

                {/* AI Insights Card */}
                <AIInsights />

                {/* Your other existing cards... */}
            </div>

            {/* Recent Sessions section... */}

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

                    {/* NEW: AI Coach Quick Action */}
                    <div
                        className="quick-action-card ai-action"
                        onClick={() => setShowAIChat(true)}
                        style={{ cursor: 'pointer' }}
                    >
                        <div className="action-icon">🤖</div>
                        <h3>AI Coach Chat</h3>
                        <p>Get personalized training advice</p>
                        <small>Ask questions, get tips, stay motivated</small>
                    </div>
                </div>
            </div>

            {/* AI Chat Component */}
            <AIChatCoach
                isOpen={showAIChat}
                onClose={() => setShowAIChat(false)}
            />

            {/* Floating Chat Toggle */}
            <AIChatToggle onClick={() => setShowAIChat(true)} />
        </div>
    );
};

export default Dashboard;