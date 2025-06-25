// src/components/common/LoadingSpinner.jsx
import React from 'react';

const LoadingSpinner = ({ size = 'md', className = '' }) => {
    const sizeClass = `spinner-${size}`;

    return (
        <div className={`loading-container ${className}`}>
            <div className={`spinner ${sizeClass}`}></div>
        </div>
    );
};

export default LoadingSpinner;