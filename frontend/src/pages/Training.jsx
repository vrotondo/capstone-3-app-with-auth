import React, { useState, useEffect } from 'react';
import Button from '../components/common/Button';
import SessionList from '../components/features/training/SessionList';
import SessionForm from '../components/features/training/SessionForm';
import trainingService from '../services/trainingService';

const Training = () => {
    const [sessions, setSessions] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [showForm, setShowForm] = useState(false);
    const [editingSession, setEditingSession] = useState(null);
    const [error, setError] = useState('');
    const [filters, setFilters] = useState({});

    // Load training sessions
    const loadSessions = async (filterParams = {}) => {
        try {
            setIsLoading(true);
            setError('');

            const response = await trainingService.getSessions(filterParams);
            setSessions(response.sessions || []);
        } catch (error) {
            console.error('Failed to load training sessions:', error);
            setError('Failed to load training sessions. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    // Load sessions on component mount
    useEffect(() => {
        loadSessions();
    }, []);

    // Handle filter changes
    const handleFilterChange = (newFilters) => {
        setFilters(newFilters);
        loadSessions(newFilters);
    };

    // Handle creating/updating sessions
    const handleSubmitSession = async (sessionData) => {
        try {
            setIsSubmitting(true);
            setError('');

            if (editingSession) {
                // Update existing session
                await trainingService.updateSession(editingSession.id, sessionData);

                // Update sessions list
                setSessions(prevSessions =>
                    prevSessions.map(session =>
                        session.id === editingSession.id
                            ? { ...session, ...sessionData }
                            : session
                    )
                );
            } else {
                // Create new session
                const response = await trainingService.createSession(sessionData);

                // Add new session to the beginning of the list
                setSessions(prevSessions => [response.session, ...prevSessions]);
            }

            // Close form and reset editing state
            setShowForm(false);
            setEditingSession(null);
        } catch (error) {
            console.error('Failed to save training session:', error);
            setError(
                error.response?.data?.message ||
                'Failed to save training session. Please try again.'
            );
        } finally {
            setIsSubmitting(false);
        }
    };

    // Handle editing a session
    const handleEditSession = (session) => {
        setEditingSession(session);
        setShowForm(true);
    };

    // Handle deleting a session
    const handleDeleteSession = async (sessionId) => {
        try {
            await trainingService.deleteSession(sessionId);

            // Remove session from list
            setSessions(prevSessions =>
                prevSessions.filter(session => session.id !== sessionId)
            );
        } catch (error) {
            console.error('Failed to delete training session:', error);
            setError('Failed to delete training session. Please try again.');
        }
    };

    // Handle canceling form
    const handleCancelForm = () => {
        setShowForm(false);
        setEditingSession(null);
        setError('');
    };

    // Handle starting new session
    const handleNewSession = () => {
        setEditingSession(null);
        setShowForm(true);
        setError('');
    };

    return (
        <div className="training-page">
            <div className="page-header">
                <div className="header-content">
                    <div>
                        <h1>Training Sessions</h1>
                        <p>Track and manage your martial arts training sessions</p>
                    </div>
                    {!showForm && (
                        <Button
                            variant="primary"
                            onClick={handleNewSession}
                        >
                            Log New Session
                        </Button>
                    )}
                </div>
            </div>

            {error && (
                <div className="error-message">
                    {error}
                    <button
                        onClick={() => setError('')}
                        className="error-close"
                    >
                        ×
                    </button>
                </div>
            )}

            {showForm ? (
                <div className="form-section">
                    <div className="form-header">
                        <h2>{editingSession ? 'Edit Training Session' : 'Log New Training Session'}</h2>
                        <p>
                            {editingSession
                                ? 'Update the details of your training session below.'
                                : 'Record the details of your latest training session.'
                            }
                        </p>
                    </div>

                    <div className="form-container">
                        <SessionForm
                            session={editingSession}
                            onSubmit={handleSubmitSession}
                            onCancel={handleCancelForm}
                            isLoading={isSubmitting}
                        />
                    </div>
                </div>
            ) : (
                <div className="sessions-section">
                    <SessionList
                        sessions={sessions}
                        isLoading={isLoading}
                        onEdit={handleEditSession}
                        onDelete={handleDeleteSession}
                        onFilterChange={handleFilterChange}
                        filters={filters}
                    />
                </div>
            )}
        </div>
    );
};

export default Training;