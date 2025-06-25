import React from 'react';
import '../../styles/components/buttons.css';

const Button = ({
    children,
    variant = 'primary',
    size = 'md',
    type = 'button',
    disabled = false,
    loading = false,
    className = '',
    onClick,
    ...props
}) => {
    const baseClass = 'btn';
    const variantClass = `btn-${variant}`;
    const sizeClass = `btn-${size}`;
    const disabledClass = disabled || loading ? 'btn-disabled' : '';
    const loadingClass = loading ? 'btn-loading' : '';

    const buttonClass = [
        baseClass,
        variantClass,
        sizeClass,
        disabledClass,
        loadingClass,
        className,
    ]
        .filter(Boolean)
        .join(' ');

    return (
        <button
            type={type}
            className={buttonClass}
            disabled={disabled || loading}
            onClick={onClick}
            {...props}
        >
            {loading && <span className="loading-spinner"></span>}
            {children}
        </button>
    );
};

export default Button;
