import React, { useState, useEffect } from 'react';
import Button from './common/Button';
import LoadingSpinner from './common/LoadingSpinner';

const AIInsights = () => {
    const [status, setStatus] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        checkAIStatus();
    }, []);

    const checkAIStatus = async () => {
        try {
            setLoading(true);
            setError(null);

            // Simple fetch to our AI status endpoint
            const response = await fetch('http://localhost:8000/api/ai-status');

            if (response.ok) {
                const data = await response.json();
                setStatus(data);
            } else {
                setError('AI service endpoint not available');
            }
        } catch (err) {
            console.error('Error checking AI status:', err);
            setError('Could not connect to AI service');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="dashboard-card ai-insights-card">
                <h3>🤖 AI Training Insights</h3>
                <div className="loading-container">
                    <LoadingSpinner />
                    <p>Checking AI service status...</p>
                </div>
            </div>
        );
    }

    if (error || !status) {
        return (
            <div className="dashboard-card ai-insights-card error">
                <h3>🤖 AI Training Insights</h3>
                <div className="error-state">
                    <p>❌ {error || 'AI service unavailable'}</p>
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={checkAIStatus}
                    >
                        Try Again
                    </Button>
                </div>
            </div>
        );
    }

    if (!status.ai_enabled) {
        return (
            <div className="dashboard-card ai-insights-card disabled">
                <h3>🤖 AI Training Insights</h3>
                <div className="ai-disabled">
                    <div className="disabled-icon">🔧</div>
                    <p>{status.message}</p>
                    <small>Status: {status.status}</small>
                    {status.status === 'library_missing' && (
                        <div style={{ marginTop: '1rem', fontSize: '0.8rem', textAlign: 'left' }}>
                            <strong>To enable AI insights:</strong>
                            <ol style={{ paddingLeft: '1rem', margin: '0.5rem 0' }}>
                                <li>cd backend</li>
                                <li>pip install google-generativeai</li>
                                <li>Add GEMINI_API_KEY to .env</li>
                                <li>Restart server</li>
                            </ol>
                        </div>
                    )}
                </div>
            </div>
        );
    }

    // AI is enabled - show a placeholder for now
    return (
        <div className="dashboard-card ai-insights-card">
            <h3>🤖 AI Training Insights</h3>
            <div className="ai-ready">
                <div style={{ textAlign: 'center', padding: '2rem 1rem' }}>
                    <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>✅</div>
                    <p><strong>AI Service Ready!</strong></p>
                    <p style={{ fontSize: '0.9rem', opacity: 0.8 }}>
                        {status.message}
                    </p>
                    <small style={{ fontSize: '0.7rem', opacity: 0.7 }}>
                        Status: {status.status}
                    </small>
                </div>

                {status.endpoints && (
                    <div style={{
                        marginTop: '1rem',
                        padding: '1rem',
                        background: 'rgba(255,255,255,0.1)',
                        borderRadius: '8px',
                        fontSize: '0.8rem'
                    }}>
                        <strong>Available endpoints:</strong>
                        <ul style={{ margin: '0.5rem 0', paddingLeft: '1rem' }}>
                            {status.endpoints.map((endpoint, index) => (
                                <li key={index}>{endpoint}</li>
                            ))}
                        </ul>
                    </div>
                )}

                <div className="card-action" style={{ marginTop: '1rem', textAlign: 'center' }}>
                    <p style={{ fontSize: '0.8rem', opacity: 0.8 }}>
                        🚧 Full AI insights coming soon!
                    </p>
                </div>
            </div>
        </div>
    );
};

export default AIInsights;