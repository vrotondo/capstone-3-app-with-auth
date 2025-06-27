import React from 'react';

const LoadingSpinner = ({ size = 'medium', message }) => {
    const sizeClasses = {
        small: 'loading-spinner-small',
        medium: 'loading-spinner-medium',
        large: 'loading-spinner-large'
    };

    return (
        <div className="loading-container">
            <div className={`loading-spinner ${sizeClasses[size]}`}>
                <div className="spinner"></div>
            </div>
            {message && <p className="loading-message">{message}</p>}
        </div>
    );
};

export default LoadingSpinner;