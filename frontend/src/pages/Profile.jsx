// Enhanced Profile Component
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Edit3, Save, X, User, Settings, Shield,
    Camera, Eye, EyeOff, AlertTriangle
} from 'lucide-react';

const Profile = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState({ type: '', text: '' });

    // Editing states
    const [editingPersonal, setEditingPersonal] = useState(false);
    const [editingMartialArts, setEditingMartialArts] = useState(false);
    const [editingPreferences, setEditingPreferences] = useState(false);
    const [editingPassword, setEditingPassword] = useState(false);

    // User data
    const [userData, setUserData] = useState({
        name: '',
        email: '',
        bio: '',
        location: '',
        dateOfBirth: '',
        primaryStyle: '',
        currentBelt: '',
        yearsTraining: 0,
        instructor: '',
        dojo: '',
        goals: '',
        sessionCount: 0,
        techniqueCount: 0,
        totalHours: 0
    });

    // Form data (for editing)
    const [formData, setFormData] = useState({});

    // Preferences
    const [preferences, setPreferences] = useState({
        emailNotifications: true,
        publicProfile: false,
        showProgress: true,
        weeklyDigest: true
    });

    // Password change
    const [passwordData, setPasswordData] = useState({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
    });
    const [showPasswords, setShowPasswords] = useState({
        current: false,
        new: false,
        confirm: false
    });

    useEffect(() => {
        loadUserProfile();
    }, []);

    const loadUserProfile = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem('token');

            const response = await fetch('/api/user/profile', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                setUserData(data.user);
                setFormData(data.user);
                setPreferences(data.preferences || preferences);
            } else {
                throw new Error('Failed to load profile');
            }
        } catch (error) {
            setMessage({ type: 'error', text: error.message });
        } finally {
            setLoading(false);
        }
    };

    const handleSaveSection = async (section) => {
        try {
            setSaving(true);
            const token = localStorage.getItem('token');

            let endpoint = '/api/user/profile';
            let data = formData;

            if (section === 'preferences') {
                endpoint = '/api/user/preferences';
                data = preferences;
            } else if (section === 'password') {
                endpoint = '/api/user/password';
                data = passwordData;
            }

            const response = await fetch(endpoint, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                const result = await response.json();

                if (section === 'password') {
                    setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
                    setEditingPassword(false);
                    setMessage({ type: 'success', text: 'Password updated successfully!' });
                } else if (section === 'preferences') {
                    setMessage({ type: 'success', text: 'Preferences updated successfully!' });
                    setEditingPreferences(false);
                } else {
                    setUserData(result.user);
                    setMessage({ type: 'success', text: 'Profile updated successfully!' });

                    // Close editing mode
                    if (section === 'personal') setEditingPersonal(false);
                    if (section === 'martialArts') setEditingMartialArts(false);
                }
            } else {
                const error = await response.json();
                throw new Error(error.message || 'Failed to update profile');
            }
        } catch (error) {
            setMessage({ type: 'error', text: error.message });
        } finally {
            setSaving(false);
        }
    };

    const handleCancel = (section) => {
        setFormData({ ...userData });
        setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });

        if (section === 'personal') setEditingPersonal(false);
        if (section === 'martialArts') setEditingMartialArts(false);
        if (section === 'preferences') setEditingPreferences(false);
        if (section === 'password') setEditingPassword(false);

        setMessage({ type: '', text: '' });
    };

    const getPasswordStrength = (password) => {
        if (password.length < 6) return 'weak';
        if (password.length < 10 || !/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(password)) return 'medium';
        return 'strong';
    };

    const getInitials = (name) => {
        return name.split(' ').map(n => n[0]).join('').toUpperCase() || 'U';
    };

    const belts = [
        { name: 'White', color: '#ffffff', border: '#e5e7eb' },
        { name: 'Yellow', color: '#fde047' },
        { name: 'Orange', color: '#fb923c' },
        { name: 'Green', color: '#22c55e' },
        { name: 'Blue', color: '#3b82f6' },
        { name: 'Purple', color: '#a855f7' },
        { name: 'Brown', color: '#a3530a' },
        { name: 'Black', color: '#1f2937' },
    ];

    if (loading) {
        return (
            <div className="profile-page">
                <div className="loading-container">
                    <div className="spinner spinner-md"></div>
                    <p>Loading your profile...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="profile-page">
            {/* Profile Header */}
            <div className="profile-header">
                <div className="profile-avatar">
                    {getInitials(userData.name)}
                    <button className="avatar-edit-btn">
                        <Camera size={16} />
                    </button>
                </div>

                <h1 className="profile-name">{userData.name || 'Your Name'}</h1>
                <p className="profile-email">{userData.email}</p>

                <div className="profile-stats">
                    <div className="profile-stat">
                        <span className="stat-number">{userData.sessionCount || 0}</span>
                        <span className="stat-label">Sessions</span>
                    </div>
                    <div className="profile-stat">
                        <span className="stat-number">{userData.techniqueCount || 0}</span>
                        <span className="stat-label">Techniques</span>
                    </div>
                    <div className="profile-stat">
                        <span className="stat-number">{userData.totalHours || 0}h</span>
                        <span className="stat-label">Training</span>
                    </div>
                    <div className="profile-stat">
                        <span className="stat-number">{userData.yearsTraining || 0}</span>
                        <span className="stat-label">Years</span>
                    </div>
                </div>
            </div>

            {/* Messages */}
            {message.text && (
                <div className={`message ${message.type}`}>
                    {message.type === 'success' && '✅'}
                    {message.type === 'error' && '❌'}
                    {message.type === 'info' && 'ℹ️'}
                    {message.text}
                </div>
            )}

            <div className="profile-content">
                {/* Personal Information */}
                <div className="profile-section">
                    {saving && <div className="loading-overlay"><div className="spinner spinner-md"></div></div>}

                    <div className="section-header">
                        <h2 className="section-title personal">Personal Information</h2>
                        <button
                            className={`edit-toggle-btn ${editingPersonal ? 'editing' : ''}`}
                            onClick={() => editingPersonal ? handleCancel('personal') : setEditingPersonal(true)}
                        >
                            {editingPersonal ? <X size={16} /> : <Edit3 size={16} />}
                            {editingPersonal ? 'Cancel' : 'Edit'}
                        </button>
                    </div>

                    <div className="form-grid">
                        <div className="form-field">
                            <label className="field-label">👤 Full Name</label>
                            {editingPersonal ? (
                                <input
                                    type="text"
                                    className="field-input"
                                    value={formData.name || ''}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    placeholder="Enter your full name"
                                />
                            ) : (
                                <div className={`field-display ${!userData.name ? 'empty' : ''}`}>
                                    {userData.name || 'Not provided'}
                                </div>
                            )}
                        </div>

                        <div className="form-field">
                            <label className="field-label">📧 Email Address</label>
                            <div className="field-display">{userData.email}</div>
                        </div>

                        <div className="form-field">
                            <label className="field-label">📍 Location</label>
                            {editingPersonal ? (
                                <input
                                    type="text"
                                    className="field-input"
                                    value={formData.location || ''}
                                    onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                                    placeholder="City, Country"
                                />
                            ) : (
                                <div className={`field-display ${!userData.location ? 'empty' : ''}`}>
                                    {userData.location || 'Not provided'}
                                </div>
                            )}
                        </div>

                        <div className="form-field">
                            <label className="field-label">🎂 Date of Birth</label>
                            {editingPersonal ? (
                                <input
                                    type="date"
                                    className="field-input"
                                    value={formData.dateOfBirth || ''}
                                    onChange={(e) => setFormData({ ...formData, dateOfBirth: e.target.value })}
                                />
                            ) : (
                                <div className={`field-display ${!userData.dateOfBirth ? 'empty' : ''}`}>
                                    {userData.dateOfBirth ? new Date(userData.dateOfBirth).toLocaleDateString() : 'Not provided'}
                                </div>
                            )}
                        </div>

                        <div className="form-field" style={{ gridColumn: '1 / -1' }}>
                            <label className="field-label">📝 Bio</label>
                            {editingPersonal ? (
                                <textarea
                                    className="field-textarea"
                                    value={formData.bio || ''}
                                    onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                                    placeholder="Tell us about yourself..."
                                />
                            ) : (
                                <div className={`field-display ${!userData.bio ? 'empty' : ''}`}>
                                    {userData.bio || 'No bio provided'}
                                </div>
                            )}
                        </div>
                    </div>

                    {editingPersonal && (
                        <div className="section-actions">
                            <button
                                className="action-btn save-btn"
                                onClick={() => handleSaveSection('personal')}
                                disabled={saving}
                            >
                                <Save size={16} />
                                {saving ? 'Saving...' : 'Save Changes'}
                            </button>
                        </div>
                    )}
                </div>

                {/* Martial Arts Information */}
                <div className="profile-section">
                    {saving && <div className="loading-overlay"><div className="spinner spinner-md"></div></div>}

                    <div className="section-header">
                        <h2 className="section-title martial-arts">Martial Arts</h2>
                        <button
                            className={`edit-toggle-btn ${editingMartialArts ? 'editing' : ''}`}
                            onClick={() => editingMartialArts ? handleCancel('martialArts') : setEditingMartialArts(true)}
                        >
                            {editingMartialArts ? <X size={16} /> : <Edit3 size={16} />}
                            {editingMartialArts ? 'Cancel' : 'Edit'}
                        </button>
                    </div>

                    <div className="form-grid">
                        <div className="form-field">
                            <label className="field-label">🥋 Primary Style</label>
                            {editingMartialArts ? (
                                <select
                                    className="field-select"
                                    value={formData.primaryStyle || ''}
                                    onChange={(e) => setFormData({ ...formData, primaryStyle: e.target.value })}
                                >
                                    <option value="">Select a martial art</option>
                                    <option value="Karate">Karate</option>
                                    <option value="Taekwondo">Taekwondo</option>
                                    <option value="Judo">Judo</option>
                                    <option value="Brazilian Jiu-Jitsu">Brazilian Jiu-Jitsu</option>
                                    <option value="Muay Thai">Muay Thai</option>
                                    <option value="Boxing">Boxing</option>
                                    <option value="Kung Fu">Kung Fu</option>
                                    <option value="Aikido">Aikido</option>
                                    <option value="Krav Maga">Krav Maga</option>
                                    <option value="MMA">Mixed Martial Arts</option>
                                    <option value="Other">Other</option>
                                </select>
                            ) : (
                                <div className={`field-display ${!userData.primaryStyle ? 'empty' : ''}`}>
                                    {userData.primaryStyle || 'Not specified'}
                                </div>
                            )}
                        </div>

                        <div className="form-field">
                            <label className="field-label">🏅 Current Belt</label>
                            {editingMartialArts ? (
                                <div className="belt-selector">
                                    {belts.map((belt) => (
                                        <div
                                            key={belt.name}
                                            className={`belt-option ${formData.currentBelt === belt.name ? 'selected' : ''}`}
                                            onClick={() => setFormData({ ...formData, currentBelt: belt.name })}
                                        >
                                            <div
                                                className="belt-color"
                                                style={{
                                                    backgroundColor: belt.color,
                                                    border: belt.border ? `2px solid ${belt.border}` : 'none'
                                                }}
                                            ></div>
                                            <div className="belt-name">{belt.name}</div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className={`field-display ${!userData.currentBelt ? 'empty' : ''}`}>
                                    {userData.currentBelt ? (
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                            <div
                                                style={{
                                                    width: '30px',
                                                    height: '6px',
                                                    backgroundColor: belts.find(b => b.name === userData.currentBelt)?.color || '#e5e7eb',
                                                    borderRadius: '3px',
                                                    border: userData.currentBelt === 'White' ? '1px solid #e5e7eb' : 'none'
                                                }}
                                            ></div>
                                            {userData.currentBelt} Belt
                                        </div>
                                    ) : 'Not specified'}
                                </div>
                            )}
                        </div>

                        <div className="form-field">
                            <label className="field-label">📅 Years Training</label>
                            {editingMartialArts ? (
                                <input
                                    type="number"
                                    className="field-input"
                                    value={formData.yearsTraining || ''}
                                    onChange={(e) => setFormData({ ...formData, yearsTraining: parseInt(e.target.value) || 0 })}
                                    placeholder="0"
                                    min="0"
                                    max="50"
                                />
                            ) : (
                                <div className="field-display">
                                    {userData.yearsTraining || 0} years
                                </div>
                            )}
                        </div>

                        <div className="form-field">
                            <label className="field-label">👨‍🏫 Instructor</label>
                            {editingMartialArts ? (
                                <input
                                    type="text"
                                    className="field-input"
                                    value={formData.instructor || ''}
                                    onChange={(e) => setFormData({ ...formData, instructor: e.target.value })}
                                    placeholder="Instructor's name"
                                />
                            ) : (
                                <div className={`field-display ${!userData.instructor ? 'empty' : ''}`}>
                                    {userData.instructor || 'Not provided'}
                                </div>
                            )}
                        </div>

                        <div className="form-field">
                            <label className="field-label">🏢 Dojo/Gym</label>
                            {editingMartialArts ? (
                                <input
                                    type="text"
                                    className="field-input"
                                    value={formData.dojo || ''}
                                    onChange={(e) => setFormData({ ...formData, dojo: e.target.value })}
                                    placeholder="Training facility name"
                                />
                            ) : (
                                <div className={`field-display ${!userData.dojo ? 'empty' : ''}`}>
                                    {userData.dojo || 'Not provided'}
                                </div>
                            )}
                        </div>

                        <div className="form-field" style={{ gridColumn: '1 / -1' }}>
                            <label className="field-label">🎯 Training Goals</label>
                            {editingMartialArts ? (
                                <textarea
                                    className="field-textarea"
                                    value={formData.goals || ''}
                                    onChange={(e) => setFormData({ ...formData, goals: e.target.value })}
                                    placeholder="What are your martial arts goals?"
                                />
                            ) : (
                                <div className={`field-display ${!userData.goals ? 'empty' : ''}`}>
                                    {userData.goals || 'No goals specified'}
                                </div>
                            )}
                        </div>
                    </div>

                    {editingMartialArts && (
                        <div className="section-actions">
                            <button
                                className="action-btn save-btn"
                                onClick={() => handleSaveSection('martialArts')}
                                disabled={saving}
                            >
                                <Save size={16} />
                                {saving ? 'Saving...' : 'Save Changes'}
                            </button>
                        </div>
                    )}
                </div>

                {/* Preferences */}
                <div className="profile-section">
                    {saving && <div className="loading-overlay"><div className="spinner spinner-md"></div></div>}

                    <div className="section-header">
                        <h2 className="section-title preferences">Preferences</h2>
                        <button
                            className={`edit-toggle-btn ${editingPreferences ? 'editing' : ''}`}
                            onClick={() => editingPreferences ? handleCancel('preferences') : setEditingPreferences(true)}
                        >
                            {editingPreferences ? <X size={16} /> : <Edit3 size={16} />}
                            {editingPreferences ? 'Cancel' : 'Edit'}
                        </button>
                    </div>

                    <div className="preferences-grid">
                        <div className="preference-item">
                            <div className="preference-info">
                                <div className="preference-title">Email Notifications</div>
                                <div className="preference-description">
                                    Receive updates about your training progress and new features
                                </div>
                            </div>
                            <button
                                className={`preference-toggle ${preferences.emailNotifications ? 'active' : ''}`}
                                onClick={() => editingPreferences && setPreferences({
                                    ...preferences,
                                    emailNotifications: !preferences.emailNotifications
                                })}
                                disabled={!editingPreferences}
                            >
                                <div className="toggle-slider"></div>
                            </button>
                        </div>

                        <div className="preference-item">
                            <div className="preference-info">
                                <div className="preference-title">Public Profile</div>
                                <div className="preference-description">
                                    Allow other users to view your training progress and achievements
                                </div>
                            </div>
                            <button
                                className={`preference-toggle ${preferences.publicProfile ? 'active' : ''}`}
                                onClick={() => editingPreferences && setPreferences({
                                    ...preferences,
                                    publicProfile: !preferences.publicProfile
                                })}
                                disabled={!editingPreferences}
                            >
                                <div className="toggle-slider"></div>
                            </button>
                        </div>

                        <div className="preference-item">
                            <div className="preference-info">
                                <div className="preference-title">Show Progress</div>
                                <div className="preference-description">
                                    Display your technique mastery levels and training statistics
                                </div>
                            </div>
                            <button
                                className={`preference-toggle ${preferences.showProgress ? 'active' : ''}`}
                                onClick={() => editingPreferences && setPreferences({
                                    ...preferences,
                                    showProgress: !preferences.showProgress
                                })}
                                disabled={!editingPreferences}
                            >
                                <div className="toggle-slider"></div>
                            </button>
                        </div>

                        <div className="preference-item">
                            <div className="preference-info">
                                <div className="preference-title">Weekly Digest</div>
                                <div className="preference-description">
                                    Get a weekly summary of your training activities and achievements
                                </div>
                            </div>
                            <button
                                className={`preference-toggle ${preferences.weeklyDigest ? 'active' : ''}`}
                                onClick={() => editingPreferences && setPreferences({
                                    ...preferences,
                                    weeklyDigest: !preferences.weeklyDigest
                                })}
                                disabled={!editingPreferences}
                            >
                                <div className="toggle-slider"></div>
                            </button>
                        </div>
                    </div>

                    {editingPreferences && (
                        <div className="section-actions">
                            <button
                                className="action-btn save-btn"
                                onClick={() => handleSaveSection('preferences')}
                                disabled={saving}
                            >
                                <Save size={16} />
                                {saving ? 'Saving...' : 'Save Preferences'}
                            </button>
                        </div>
                    )}
                </div>

                {/* Security */}
                <div className="profile-section">
                    {saving && <div className="loading-overlay"><div className="spinner spinner-md"></div></div>}

                    <div className="section-header">
                        <h2 className="section-title security">Security</h2>
                        <button
                            className={`edit-toggle-btn ${editingPassword ? 'editing' : ''}`}
                            onClick={() => editingPassword ? handleCancel('password') : setEditingPassword(true)}
                        >
                            {editingPassword ? <X size={16} /> : <Edit3 size={16} />}
                            {editingPassword ? 'Cancel' : 'Change Password'}
                        </button>
                    </div>

                    {editingPassword ? (
                        <div className="password-form">
                            <div className="form-field">
                                <label className="field-label">🔒 Current Password</label>
                                <div style={{ position: 'relative' }}>
                                    <input
                                        type={showPasswords.current ? 'text' : 'password'}
                                        className="field-input"
                                        value={passwordData.currentPassword}
                                        onChange={(e) => setPasswordData({
                                            ...passwordData,
                                            currentPassword: e.target.value
                                        })}
                                        placeholder="Enter current password"
                                        style={{ paddingRight: '3rem' }}
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowPasswords({
                                            ...showPasswords,
                                            current: !showPasswords.current
                                        })}
                                        style={{
                                            position: 'absolute',
                                            right: '1rem',
                                            top: '50%',
                                            transform: 'translateY(-50%)',
                                            background: 'none',
                                            border: 'none',
                                            cursor: 'pointer',
                                            color: 'var(--text-secondary)'
                                        }}
                                    >
                                        {showPasswords.current ? <EyeOff size={16} /> : <Eye size={16} />}
                                    </button>
                                </div>
                            </div>

                            <div className="form-field">
                                <label className="field-label">🔑 New Password</label>
                                <div style={{ position: 'relative' }}>
                                    <input
                                        type={showPasswords.new ? 'text' : 'password'}
                                        className="field-input"
                                        value={passwordData.newPassword}
                                        onChange={(e) => setPasswordData({
                                            ...passwordData,
                                            newPassword: e.target.value
                                        })}
                                        placeholder="Enter new password"
                                        style={{ paddingRight: '3rem' }}
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowPasswords({
                                            ...showPasswords,
                                            new: !showPasswords.new
                                        })}
                                        style={{
                                            position: 'absolute',
                                            right: '1rem',
                                            top: '50%',
                                            transform: 'translateY(-50%)',
                                            background: 'none',
                                            border: 'none',
                                            cursor: 'pointer',
                                            color: 'var(--text-secondary)'
                                        }}
                                    >
                                        {showPasswords.new ? <EyeOff size={16} /> : <Eye size={16} />}
                                    </button>
                                </div>
                                {passwordData.newPassword && (
                                    <div className={`password-strength ${getPasswordStrength(passwordData.newPassword)}`}>
                                        Password strength: {getPasswordStrength(passwordData.newPassword)}
                                    </div>
                                )}
                            </div>

                            <div className="form-field">
                                <label className="field-label">✅ Confirm Password</label>
                                <div style={{ position: 'relative' }}>
                                    <input
                                        type={showPasswords.confirm ? 'text' : 'password'}
                                        className="field-input"
                                        value={passwordData.confirmPassword}
                                        onChange={(e) => setPasswordData({
                                            ...passwordData,
                                            confirmPassword: e.target.value
                                        })}
                                        placeholder="Confirm new password"
                                        style={{ paddingRight: '3rem' }}
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowPasswords({
                                            ...showPasswords,
                                            confirm: !showPasswords.confirm
                                        })}
                                        style={{
                                            position: 'absolute',
                                            right: '1rem',
                                            top: '50%',
                                            transform: 'translateY(-50%)',
                                            background: 'none',
                                            border: 'none',
                                            cursor: 'pointer',
                                            color: 'var(--text-secondary)'
                                        }}
                                    >
                                        {showPasswords.confirm ? <EyeOff size={16} /> : <Eye size={16} />}
                                    </button>
                                </div>
                                {passwordData.confirmPassword && passwordData.newPassword !== passwordData.confirmPassword && (
                                    <div className="password-strength weak">
                                        Passwords do not match
                                    </div>
                                )}
                            </div>

                            <div className="section-actions">
                                <button
                                    className="action-btn save-btn"
                                    onClick={() => handleSaveSection('password')}
                                    disabled={
                                        saving ||
                                        !passwordData.currentPassword ||
                                        !passwordData.newPassword ||
                                        passwordData.newPassword !== passwordData.confirmPassword ||
                                        getPasswordStrength(passwordData.newPassword) === 'weak'
                                    }
                                >
                                    <Save size={16} />
                                    {saving ? 'Updating...' : 'Update Password'}
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="message info">
                            <Shield size={20} />
                            Your password was last updated on {new Date().toLocaleDateString()}.
                            We recommend updating your password regularly for security.
                        </div>
                    )}
                </div>

                {/* Danger Zone */}
                <div className="profile-section" style={{ borderColor: '#fecaca', background: '#fef2f2' }}>
                    <div className="section-header">
                        <h2 className="section-title" style={{ color: '#dc2626' }}>
                            <AlertTriangle size={20} />
                            Danger Zone
                        </h2>
                    </div>

                    <div className="message error">
                        <AlertTriangle size={20} />
                        Deleting your account is permanent and cannot be undone. All your data will be lost.
                    </div>

                    <div className="section-actions">
                        <button
                            className="action-btn delete-btn"
                            onClick={() => {
                                if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
                                    // Handle account deletion
                                    console.log('Delete account');
                                }
                            }}
                        >
                            <AlertTriangle size={16} />
                            Delete Account
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Profile;