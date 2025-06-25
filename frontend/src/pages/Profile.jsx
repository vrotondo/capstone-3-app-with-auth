// src/pages/Profile.jsx
import React from 'react';
import { useAuth } from '../context/AuthContext';

const Profile = () => {
    const { user } = useAuth();

    return (
        <div className="profile-page">
            <div className="page-header">
                <h1>Profile</h1>
                <p>Manage your account settings</p>
            </div>

            <div className="profile-info">
                <h3>Personal Information</h3>
                <p><strong>Name:</strong> {user?.first_name} {user?.last_name}</p>
                <p><strong>Email:</strong> {user?.email}</p>
                <p><strong>Martial Art:</strong> {user?.martial_art}</p>
                <p><strong>Current Belt:</strong> {user?.current_belt || 'Not specified'}</p>
                <p><strong>Dojo:</strong> {user?.dojo || 'Not specified'}</p>
            </div>
        </div>
    );
};

export default Profile;