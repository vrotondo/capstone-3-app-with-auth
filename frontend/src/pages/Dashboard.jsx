// src/pages/Dashboard.jsx
import React from 'react';
import { useAuth } from '../context/AuthContext';

const Dashboard = () => {
    const { user } = useAuth();

    return (
        <div className="dashboard-page">
            <div className="dashboard-header">
                <h1>Welcome back, {user?.first_name}!</h1>
                <p>Here's your martial arts progress overview</p>
            </div>

            <div className="dashboard-grid">
                <div className="dashboard-card">
                    <h3>Recent Training</h3>
                    <p>No training sessions yet. Start logging your sessions!</p>
                </div>

                <div className="dashboard-card">
                    <h3>Techniques</h3>
                    <p>No techniques added yet. Build your technique library!</p>
                </div>

                <div className="dashboard-card">
                    <h3>This Week</h3>
                    <p>0 training sessions logged</p>
                </div>

                <div className="dashboard-card">
                    <h3>Goals</h3>
                    <p>Set your training goals to stay motivated!</p>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
