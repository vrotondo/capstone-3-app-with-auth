import React, { useState, useEffect, useCallback } from 'react';
import wgerService from '../../../services/wgerService';
import LoadingSpinner from '../../common/LoadingSpinner';
import ExerciseCard from './ExerciseCard';
import ExerciseFilters from './ExerciseFilters';

const ExerciseBrowser = () => {
    const [exercises, setExercises] = useState([]);
    const [categories, setCategories] = useState([]);
    const [muscles, setMuscles] = useState([]);
    const [equipment, setEquipment] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchLoading, setSearchLoading] = useState(false);
    const [error, setError] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [filters, setFilters] = useState({
        category: '',
        muscle: '',
        equipment: '',
        difficulty: ''
    });
    const [currentPage, setCurrentPage] = useState(1);
    const [totalCount, setTotalCount] = useState(0);
    const [hasMore, setHasMore] = useState(false);

    // Load initial data
    useEffect(() => {
        loadInitialData();
    }, []);

    // Load exercises when filters change
    useEffect(() => {
        if (!loading) {
            setCurrentPage(1);
            loadExercises(true);
        }
    }, [filters, searchQuery]);

    const loadInitialData = async () => {
        try {
            setLoading(true);

            // Load filter options and initial exercises in parallel
            const [categoriesRes, musclesRes, equipmentRes] = await Promise.all([
                wgerService.getCategories(),
                wgerService.getMuscles(),
                wgerService.getEquipment()
            ]);

            if (categoriesRes.success) {
                setCategories(categoriesRes.categories);
            }
            if (musclesRes.success) {
                setMuscles(musclesRes.muscles);
            }
            if (equipmentRes.success) {
                setEquipment(equipmentRes.equipment);
            }

            // Load initial martial arts relevant exercises
            await loadMartialArtsExercises();

        } catch (err) {
            setError(`Failed to load exercise data: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };

    const loadMartialArtsExercises = async () => {
        try {
            const response = await wgerService.getMartialArtsExercises(50);
            if (response.success) {
                setExercises(response.exercises);
                setTotalCount(response.count);
                setHasMore(response.exercises.length >= 50);
            }
        } catch (err) {
            console.error('Error loading martial arts exercises:', err);
        }
    };

    const loadExercises = async (reset = false) => {
        try {
            setSearchLoading(true);

            let response;

            if (searchQuery.trim()) {
                // Search exercises
                response = await wgerService.searchExercises(searchQuery, 50);
            } else if (filters.category || filters.muscle || filters.equipment) {
                // Filtered exercises
                const params = {
                    limit: 50,
                    offset: reset ? 0 : (currentPage - 1) * 50
                };

                if (filters.category) params.category = filters.category;
                if (filters.muscle) params.muscle = filters.muscle;
                if (filters.equipment) params.equipment = filters.equipment;

                response = await wgerService.getExercises(params);
            } else {
                // Default to martial arts exercises
                await loadMartialArtsExercises();
                return;
            }

            if (response.success) {
                if (reset) {
                    setExercises(response.exercises);
                } else {
                    setExercises(prev => [...prev, ...response.exercises]);
                }
                setTotalCount(response.count || response.exercises.length);
                setHasMore(response.next != null);
            } else {
                setError('Failed to load exercises');
            }

        } catch (err) {
            setError(`Failed to load exercises: ${err.message}`);
        } finally {
            setSearchLoading(false);
        }
    };

    const handleSearch = useCallback((query) => {
        setSearchQuery(query);
    }, []);

    const handleFilterChange = useCallback((newFilters) => {
        setFilters(newFilters);
    }, []);

    const loadMore = () => {
        if (!searchLoading && hasMore) {
            setCurrentPage(prev => prev + 1);
            loadExercises(false);
        }
    };

    const clearFilters = () => {
        setFilters({
            category: '',
            muscle: '',
            equipment: '',
            difficulty: ''
        });
        setSearchQuery('');
    };

    if (loading) {
        return (
            <div className="exercise-browser-loading">
                <LoadingSpinner />
                <p>Loading exercise database...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="exercise-browser-error">
                <h3>Error Loading Exercises</h3>
                <p>{error}</p>
                <button onClick={loadInitialData} className="btn btn-primary">
                    Try Again
                </button>
            </div>
        );
    }

    return (
        <div className="exercise-browser">
            <div className="exercise-browser-header">
                <h2>Exercise Database</h2>
                <p>Explore {totalCount.toLocaleString()} exercises from the wger database</p>
            </div>

            <ExerciseFilters
                categories={categories}
                muscles={muscles}
                equipment={equipment}
                filters={filters}
                searchQuery={searchQuery}
                onFilterChange={handleFilterChange}
                onSearch={handleSearch}
                onClear={clearFilters}
                loading={searchLoading}
            />

            <div className="exercise-results">
                <div className="exercise-results-header">
                    <div className="exercise-count">
                        Showing {exercises.length} of {totalCount.toLocaleString()} exercises
                    </div>

                    {(filters.category || filters.muscle || filters.equipment || searchQuery) && (
                        <button onClick={clearFilters} className="btn btn-secondary btn-sm">
                            Clear Filters
                        </button>
                    )}
                </div>

                {exercises.length === 0 ? (
                    <div className="no-exercises">
                        <h3>No exercises found</h3>
                        <p>Try adjusting your search terms or filters</p>
                        <button onClick={clearFilters} className="btn btn-primary">
                            Show All Exercises
                        </button>
                    </div>
                ) : (
                    <>
                        <div className="exercise-grid">
                            {exercises.map((exercise) => (
                                <ExerciseCard
                                    key={exercise.id}
                                    exercise={wgerService.formatExerciseForDisplay(exercise)}
                                    difficulty={wgerService.getExerciseDifficulty(exercise)}
                                    categoryIcon={wgerService.getCategoryIcon(exercise.category_name)}
                                />
                            ))}
                        </div>

                        {hasMore && (
                            <div className="exercise-load-more">
                                <button
                                    onClick={loadMore}
                                    disabled={searchLoading}
                                    className="btn btn-primary"
                                >
                                    {searchLoading ? (
                                        <>
                                            <LoadingSpinner size="small" />
                                            Loading...
                                        </>
                                    ) : (
                                        'Load More Exercises'
                                    )}
                                </button>
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
};

export default ExerciseBrowser;