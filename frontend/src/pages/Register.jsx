import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import '../styles/pages/auth.css';

const Register = () => {
    const navigate = useNavigate();
    const { register } = useAuth();

    const [formData, setFormData] = useState({
        firstName: '',
        lastName: '',
        email: '',
        password: '',
        confirmPassword: '',
        martialArt: '',
        currentBelt: '',
        dojo: '',
    });

    const [errors, setErrors] = useState({});
    const [loading, setLoading] = useState(false);
    const [successMessage, setSuccessMessage] = useState('');

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value,
        }));

        // Clear error when user starts typing
        if (errors[name]) {
            setErrors(prev => ({
                ...prev,
                [name]: '',
            }));
        }

        // Clear general errors
        if (errors.general) {
            setErrors(prev => ({
                ...prev,
                general: '',
            }));
        }
    };

    const validateForm = () => {
        const newErrors = {};

        if (!formData.firstName.trim()) {
            newErrors.firstName = 'First name is required';
        }

        if (!formData.lastName.trim()) {
            newErrors.lastName = 'Last name is required';
        }

        if (!formData.email) {
            newErrors.email = 'Email is required';
        } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
            newErrors.email = 'Email is invalid';
        }

        if (!formData.password) {
            newErrors.password = 'Password is required';
        } else if (formData.password.length < 6) {
            newErrors.password = 'Password must be at least 6 characters';
        }

        if (!formData.confirmPassword) {
            newErrors.confirmPassword = 'Please confirm your password';
        } else if (formData.password !== formData.confirmPassword) {
            newErrors.confirmPassword = 'Passwords do not match';
        }

        if (!formData.martialArt.trim()) {
            newErrors.martialArt = 'Martial art is required';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        setLoading(true);
        setErrors({});
        setSuccessMessage('');

        try {
            // Prepare data for API (convert to backend format)
            const userData = {
                first_name: formData.firstName.trim(),
                last_name: formData.lastName.trim(),
                email: formData.email.trim().toLowerCase(),
                password: formData.password,
                martial_art: formData.martialArt.trim(),
                current_belt: formData.currentBelt.trim() || null,
                dojo: formData.dojo.trim() || null,
            };

            console.log('Attempting to register with:', { ...userData, password: '[HIDDEN]' });

            const result = await register(userData);

            if (result.success) {
                setSuccessMessage('Account created successfully! Redirecting to dashboard...');
                setTimeout(() => {
                    navigate('/dashboard');
                }, 1500);
            } else {
                console.error('Registration failed:', result.error);
                setErrors({ general: result.error });
            }
        } catch (error) {
            console.error('Registration error:', error);
            setErrors({
                general: error.response?.data?.message || 'An unexpected error occurred. Please try again.'
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-page">
            <div className="auth-container">
                <div className="auth-card">
                    <div className="auth-header">
                        <h1>Join DojoTracker</h1>
                        <p>Create your account to start tracking your martial arts journey</p>
                    </div>

                    <form onSubmit={handleSubmit} className="auth-form">
                        {errors.general && (
                            <div className="error-message">
                                {errors.general}
                            </div>
                        )}

                        {successMessage && (
                            <div className="success-message">
                                {successMessage}
                            </div>
                        )}

                        <div className="form-row">
                            <Input
                                type="text"
                                name="firstName"
                                label="First Name"
                                value={formData.firstName}
                                onChange={handleChange}
                                error={errors.firstName}
                                required
                                placeholder="Enter your first name"
                            />

                            <Input
                                type="text"
                                name="lastName"
                                label="Last Name"
                                value={formData.lastName}
                                onChange={handleChange}
                                error={errors.lastName}
                                required
                                placeholder="Enter your last name"
                            />
                        </div>

                        <Input
                            type="email"
                            name="email"
                            label="Email Address"
                            value={formData.email}
                            onChange={handleChange}
                            error={errors.email}
                            required
                            placeholder="Enter your email"
                        />

                        <div className="form-row">
                            <Input
                                type="password"
                                name="password"
                                label="Password"
                                value={formData.password}
                                onChange={handleChange}
                                error={errors.password}
                                required
                                placeholder="Create a password"
                            />

                            <Input
                                type="password"
                                name="confirmPassword"
                                label="Confirm Password"
                                value={formData.confirmPassword}
                                onChange={handleChange}
                                error={errors.confirmPassword}
                                required
                                placeholder="Confirm your password"
                            />
                        </div>

                        <Input
                            type="text"
                            name="martialArt"
                            label="Martial Art"
                            value={formData.martialArt}
                            onChange={handleChange}
                            error={errors.martialArt}
                            required
                            placeholder="e.g., Karate, BJJ, Taekwondo"
                        />

                        <div className="form-row">
                            <Input
                                type="text"
                                name="currentBelt"
                                label="Current Belt/Rank"
                                value={formData.currentBelt}
                                onChange={handleChange}
                                error={errors.currentBelt}
                                placeholder="e.g., White Belt, Blue Belt"
                            />

                            <Input
                                type="text"
                                name="dojo"
                                label="Dojo/School"
                                value={formData.dojo}
                                onChange={handleChange}
                                error={errors.dojo}
                                placeholder="Name of your dojo/school"
                            />
                        </div>

                        <Button
                            type="submit"
                            variant="primary"
                            size="lg"
                            loading={loading}
                            className="auth-submit-btn"
                        >
                            {loading ? 'Creating Account...' : 'Create Account'}
                        </Button>
                    </form>

                    <div className="auth-footer">
                        <p>
                            Already have an account?{' '}
                            <Link to="/login" className="auth-link">
                                Sign in here
                            </Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Register;