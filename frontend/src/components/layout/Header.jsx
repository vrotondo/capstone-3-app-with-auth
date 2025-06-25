import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import Button from '../common/Button';

const Header = () => {
    const { isAuthenticated, user, logout } = useAuth();

    const handleLogout = () => {
        logout();
    };

    return (
        <header className="header">
            <div className="container">
                <div className="header-content">
                    <Link to="/" className="logo">
                        <h2>DojoTracker</h2>
                    </Link>

                    <nav className="header-nav">
                        {isAuthenticated ? (
                            <div className="user-menu">
                                <span className="welcome-text">
                                    Welcome, {user?.first_name || user?.email}
                                </span>
                                <Link to="/profile" className="profile-link">
                                    Profile
                                </Link>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={handleLogout}
                                >
                                    Logout
                                </Button>
                            </div>
                        ) : (
                            <div className="auth-links">
                                <Link to="/login" className="auth-link">
                                    Login
                                </Link>
                                <Link to="/register">
                                    <Button variant="primary" size="sm">
                                        Sign Up
                                    </Button>
                                </Link>
                            </div>
                        )}
                    </nav>
                </div>
            </div>
        </header>
    );
};

export default Header;