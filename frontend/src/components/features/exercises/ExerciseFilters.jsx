// src/components/features/exercises/ExerciseFilters.jsx
import React, { useState } from 'react';

const ExerciseFilters = ({
    categories,
    muscles,
    equipment,
    filters,
    searchQuery,
    onFilterChange,
    onSearch,
    onClear,
    loading
}) => {
    const [localSearchQuery, setLocalSearchQuery] = useState(searchQuery);

    const handleSearchSubmit = (e) => {
        e.preventDefault();
        onSearch(localSearchQuery);
    };

    const handleFilterChange = (key, value) => {
        onFilterChange({
            ...filters,
            [key]: value
        });
    };

    const hasActiveFilters = filters.category || filters.muscle || filters.equipment || searchQuery;

    return (
        <div className="exercise-filters">
            {/* Search section */}
            <div className="search-section">
                <form onSubmit={handleSearchSubmit} className="search-form">
                    <div className="search-input-group">
                        <input
                            type="text"
                            value={localSearchQuery}
                            onChange={(e) => setLocalSearchQuery(e.target.value)}
                            placeholder="Search exercises..."
                            className="form-input search-input"
                        />
                        <button
                            type="submit"
                            disabled={loading}
                            className="btn btn-primary search-btn"
                        >
                            {loading ? '⏳' : '🔍'}
                        </button>
                    </div>
                </form>
            </div>

            {/* Filter section */}
            <div className="filter-section">
                <div className="filter-row">
                    <div className="filter-group">
                        <label htmlFor="category-filter">Category:</label>
                        <select
                            id="category-filter"
                            value={filters.category}
                            onChange={(e) => handleFilterChange('category', e.target.value)}
                            className="form-select"
                        >
                            <option value="">All Categories</option>
                            {categories.map((category) => (
                                <option key={category.id} value={category.id}>
                                    {category.name} ({category.exercise_count || 0})
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="filter-group">
                        <label htmlFor="muscle-filter">Primary Muscle:</label>
                        <select
                            id="muscle-filter"
                            value={filters.muscle}
                            onChange={(e) => handleFilterChange('muscle', e.target.value)}
                            className="form-select"
                        >
                            <option value="">All Muscles</option>
                            {muscles.map((muscle) => (
                                <option key={muscle.id} value={muscle.id}>
                                    {muscle.name}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="filter-group">
                        <label htmlFor="equipment-filter">Equipment:</label>
                        <select
                            id="equipment-filter"
                            value={filters.equipment}
                            onChange={(e) => handleFilterChange('equipment', e.target.value)}
                            className="form-select"
                        >
                            <option value="">Any Equipment</option>
                            {equipment.map((eq) => (
                                <option key={eq.id} value={eq.id}>
                                    {eq.name}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="filter-group">
                        <label htmlFor="difficulty-filter">Difficulty:</label>
                        <select
                            id="difficulty-filter"
                            value={filters.difficulty}
                            onChange={(e) => handleFilterChange('difficulty', e.target.value)}
                            className="form-select"
                        >
                            <option value="">Any Level</option>
                            <option value="Beginner">Beginner</option>
                            <option value="Intermediate">Intermediate</option>
                            <option value="Advanced">Advanced</option>
                        </select>
                    </div>
                </div>

                {hasActiveFilters && (
                    <div className="filter-actions">
                        <button
                            onClick={onClear}
                            className="btn btn-secondary btn-sm clear-filters-btn"
                        >
                            Clear All Filters
                        </button>
                        <div className="active-filters">
                            {searchQuery && (
                                <span className="active-filter">
                                    Search: "{searchQuery}"
                                </span>
                            )}
                            {filters.category && (
                                <span className="active-filter">
                                    Category: {categories.find(c => c.id == filters.category)?.name}
                                </span>
                            )}
                            {filters.muscle && (
                                <span className="active-filter">
                                    Muscle: {muscles.find(m => m.id == filters.muscle)?.name}
                                </span>
                            )}
                            {filters.equipment && (
                                <span className="active-filter">
                                    Equipment: {equipment.find(e => e.id == filters.equipment)?.name}
                                </span>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ExerciseFilters;