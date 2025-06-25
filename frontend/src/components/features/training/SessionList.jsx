import React, { useState } from 'react';
import SessionCard from './SessionCard';
import Button from '../../common/Button';
import Input from '../../common/Input';

const SessionList = ({
    sessions,
    isLoading,
    onEdit,
    onDelete,
    onFilterChange,
    filters = {}
}) => {
    const [localFilters, setLocalFilters] = useState({
        style: filters.style || '',
        dateFrom: filters.from || '',
        dateTo: filters.to || '',
        ...filters
    });

    const handleFilterChange = (field, value) => {
        const newFilters = { ...localFilters, [field]: value };
        setLocalFilters(newFilters);

        // Convert local filter names to API format
        const apiFilters = {
            style: newFilters.style,
            from: newFilters.dateFrom,
            to: newFilters.dateTo
        };

        // Remove empty filters
        Object.keys(apiFilters).forEach(key => {
            if (!apiFilters[key]) {
                delete apiFilters[key];
            }
        });

        onFilterChange(apiFilters);
    };

    const clearFilters = () => {
        const emptyFilters = {
            style: '',
            dateFrom: '',
            dateTo: ''
        };
        setLocalFilters(emptyFilters);
        onFilterChange({});
    };

    const hasActiveFilters = localFilters.style || localFilters.dateFrom || localFilters.dateTo;

    if (isLoading) {
        return (
            <div className="sessions-loading">
                <div className="loading-container">
                    <div className="spinner spinner-md"></div>
                    <p>Loading training sessions...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="session-list">
            {/* Filters */}
            <div className="session-filters">
                <h3>Filter Sessions</h3>
                <div className="filter-row">
                    <Input
                        type="text"
                        placeholder="Filter by style"
                        value={localFilters.style}
                        onChange={(e) => handleFilterChange('style', e.target.value)}
                        className="filter-input"
                    />
                    <Input
                        type="date"
                        placeholder="From date"
                        value={localFilters.dateFrom}
                        onChange={(e) => handleFilterChange('dateFrom', e.target.value)}
                        className="filter-input"
                    />
                    <Input
                        type="date"
                        placeholder="To date"
                        value={localFilters.dateTo}
                        onChange={(e) => handleFilterChange('dateTo', e.target.value)}
                        className="filter-input"
                    />
                    {hasActiveFilters && (
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={clearFilters}
                        >
                            Clear Filters
                        </Button>
                    )}
                </div>
                {hasActiveFilters && (
                    <div className="active-filters">
                        <span className="filter-label">Active filters:</span>
                        {localFilters.style && (
                            <span className="filter-tag">
                                Style: {localFilters.style}
                                <button onClick={() => handleFilterChange('style', '')}>×</button>
                            </span>
                        )}
                        {localFilters.dateFrom && (
                            <span className="filter-tag">
                                From: {localFilters.dateFrom}
                                <button onClick={() => handleFilterChange('dateFrom', '')}>×</button>
                            </span>
                        )}
                        {localFilters.dateTo && (
                            <span className="filter-tag">
                                To: {localFilters.dateTo}
                                <button onClick={() => handleFilterChange('dateTo', '')}>×</button>
                            </span>
                        )}
                    </div>
                )}
            </div>

            {/* Sessions List */}
            <div className="sessions-container">
                {sessions.length === 0 ? (
                    <div className="no-sessions">
                        <div className="no-sessions-content">
                            <div className="no-sessions-icon">🥋</div>
                            <h3>No Training Sessions Found</h3>
                            <p>
                                {hasActiveFilters
                                    ? "No sessions match your current filters. Try adjusting your search criteria."
                                    : "You haven't logged any training sessions yet. Create your first session to get started!"
                                }
                            </p>
                            {hasActiveFilters && (
                                <Button
                                    variant="outline"
                                    onClick={clearFilters}
                                >
                                    Clear Filters
                                </Button>
                            )}
                        </div>
                    </div>
                ) : (
                    <div className="sessions-grid">
                        {sessions.map((session) => (
                            <SessionCard
                                key={session.id}
                                session={session}
                                onEdit={onEdit}
                                onDelete={onDelete}
                            />
                        ))}
                    </div>
                )}
            </div>

            {/* Sessions Summary */}
            {sessions.length > 0 && (
                <div className="sessions-summary">
                    <div className="summary-stats">
                        <div className="summary-stat">
                            <span className="stat-number">{sessions.length}</span>
                            <span className="stat-label">
                                {sessions.length === 1 ? 'Session' : 'Sessions'}
                            </span>
                        </div>
                        <div className="summary-stat">
                            <span className="stat-number">
                                {Math.round(sessions.reduce((total, session) => total + session.duration, 0) / 60 * 10) / 10}
                            </span>
                            <span className="stat-label">Hours</span>
                        </div>
                        <div className="summary-stat">
                            <span className="stat-number">
                                {Math.round(sessions.reduce((total, session) => total + session.intensity_level, 0) / sessions.length * 10) / 10}
                            </span>
                            <span className="stat-label">Avg Intensity</span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default SessionList;