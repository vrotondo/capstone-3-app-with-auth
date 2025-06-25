// src/components/common/Input.jsx
import React from 'react';
import '../../styles/components/forms.css';

const Input = ({
    type = 'text',
    name,
    id,
    value,
    onChange,
    onBlur,
    placeholder,
    label,
    error,
    required = false,
    disabled = false,
    className = '',
    ...props
}) => {
    const inputId = id || name;
    const hasError = !!error;

    return (
        <div className={`form-field ${className}`}>
            {label && (
                <label htmlFor={inputId} className="form-label">
                    {label}
                    {required && <span className="required">*</span>}
                </label>
            )}
            <input
                type={type}
                id={inputId}
                name={name}
                value={value}
                onChange={onChange}
                onBlur={onBlur}
                placeholder={placeholder}
                required={required}
                disabled={disabled}
                className={`form-input ${hasError ? 'form-input-error' : ''}`}
                {...props}
            />
            {error && <span className="form-error">{error}</span>}
        </div>
    );
};

export default Input;