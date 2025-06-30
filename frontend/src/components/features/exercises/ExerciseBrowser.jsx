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
            setError(null);
            console.log('🔄 Loading initial data...');

            // Load filter options and initial exercises in parallel
            const [categoriesRes, musclesRes, equipmentRes] = await Promise.all([
                wgerService.getCategories(),
                wgerService.getMuscles(),
                wgerService.getEquipment()
            ]);

            console.log('📂 Categories response:', categoriesRes);
            console.log('💪 Muscles response:', musclesRes);
            console.log('🏋️ Equipment response:', equipmentRes);

            if (categoriesRes.success) {
                setCategories(categoriesRes.categories || []);
                console.log('✅ Categories loaded:', categoriesRes.categories?.length || 0);
            }
            if (musclesRes.success) {
                setMuscles(musclesRes.muscles || []);
                console.log('✅ Muscles loaded:', musclesRes.muscles?.length || 0);
            }
            if (equipmentRes.success) {
                setEquipment(equipmentRes.equipment || []);
                console.log('✅ Equipment loaded:', equipmentRes.equipment?.length || 0);
            }

            // Load initial exercises with fallback strategy
            await loadInitialExercises();

        } catch (err) {
            console.error('❌ Error loading initial data:', err);
            setError(`Failed to load exercise data: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };

    const loadInitialExercises = async () => {
        try {
            console.log('🏃 Loading initial exercises with fallback strategy...');

            // Try martial arts exercises first (simplified version should be faster)
            try {
                console.log('🥋 Trying martial arts exercises...');
                const martialArtsResponse = await wgerService.getMartialArtsExercises(50);
                console.log('🥋 Martial arts response:', martialArtsResponse);

                if (martialArtsResponse.success && martialArtsResponse.exercises?.length > 0) {
                    const exerciseList = martialArtsResponse.exercises;
                    console.log('✅ Martial arts exercises loaded:', exerciseList.length);
                    await processAndSetExercises(exerciseList, martialArtsResponse.count);
                    return; // Success - exit here
                } else {
                    console.log('⚠️ Martial arts exercises failed, trying regular exercises...');
                }
            } catch (martialArtsError) {
                console.log('⚠️ Martial arts exercises errored, trying regular exercises...', martialArtsError.message);
            }

            // Fallback to regular exercises
            console.log('🔄 Loading regular exercises as fallback...');
            const regularResponse = await wgerService.getExercises({ limit: 50 });
            console.log('📊 Regular exercises response:', regularResponse);

            if (regularResponse.success && regularResponse.exercises?.length > 0) {
                const exerciseList = regularResponse.exercises;
                console.log('✅ Regular exercises loaded:', exerciseList.length);
                await processAndSetExercises(exerciseList, regularResponse.count);
            } else {
                throw new Error('No exercises available from any endpoint');
            }

        } catch (err) {
            console.error('❌ Error loading initial exercises:', err);
            throw new Error(`Failed to load exercises: ${err.message}`);
        }
    };

    const processAndSetExercises = async (exerciseList, count) => {
        console.log('🔄 Processing exercises for display...', exerciseList.length);
        console.log('📝 First exercise example:', exerciseList[0]);

        // Process exercises to ensure they have proper display format
        const processedExercises = exerciseList.map(exercise => {
            const processed = {
                id: exercise.id,
                name: exercise.name || `Exercise #${exercise.id}`,
                description: exercise.description || 'No description available',
                category: exercise.category_name || exercise.category || 'Unknown',
                muscles: Array.isArray(exercise.muscles) ? exercise.muscles : [],
                muscles_secondary: Array.isArray(exercise.muscles_secondary) ? exercise.muscles_secondary : [],
                equipment: Array.isArray(exercise.equipment) ? exercise.equipment : [],
                difficulty: getDifficulty(exercise),
                categoryIcon: getCategoryIcon(exercise.category_name || exercise.category)
            };

            console.log(`📝 Processed exercise ${processed.id}:`, processed);
            return processed;
        });

        setExercises(processedExercises);
        setTotalCount(count || processedExercises.length);
        setHasMore(false); // For now, don't implement pagination

        console.log('✅ Final processed exercises set:', processedExercises.length);
    };

    const loadExercises = async (reset = false) => {
        try {
            setSearchLoading(true);
            setError(null);
            console.log('🔍 Loading exercises with filters:', filters, 'search:', searchQuery);

            let response;

            if (searchQuery.trim()) {
                // Search exercises
                console.log('🔍 Searching for:', searchQuery);
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

                console.log('🔧 Filtering with params:', params);
                response = await wgerService.getExercises(params);
            } else {
                // Default to loading initial exercises
                await loadInitialExercises();
                return;
            }

            console.log('📊 Exercise response:', response);

            if (response.success && response.exercises?.length > 0) {
                const exerciseList = response.exercises;
                console.log('✅ Exercises loaded:', exerciseList.length);

                // Process exercises for display
                const processedExercises = exerciseList.map(exercise => ({
                    id: exercise.id,
                    name: exercise.name || `Exercise #${exercise.id}`,
                    description: exercise.description || 'No description available',
                    category: exercise.category_name || exercise.category || 'Unknown',
                    muscles: Array.isArray(exercise.muscles) ? exercise.muscles : [],
                    muscles_secondary: Array.isArray(exercise.muscles_secondary) ? exercise.muscles_secondary : [],
                    equipment: Array.isArray(exercise.equipment) ? exercise.equipment : [],
                    difficulty: getDifficulty(exercise),
                    categoryIcon: getCategoryIcon(exercise.category_name || exercise.category)
                }));

                if (reset) {
                    setExercises(processedExercises);
                } else {
                    setExercises(prev => [...prev, ...processedExercises]);
                }
                setTotalCount(response.count || exerciseList.length);
                setHasMore(response.next != null);

                console.log('✅ Final processed exercises:', processedExercises.length);
            } else {
                console.error('❌ Exercise loading failed:', response);
                setError('Failed to load exercises');
            }

        } catch (err) {
            console.error('❌ Error loading exercises:', err);
            setError(`Failed to load exercises: ${err.message}`);
        } finally {
            setSearchLoading(false);
        }
    };

    // Helper functions
    const getDifficulty = (exercise) => {
        const equipmentCount = (exercise.equipment?.length || 0);
        const muscleCount = (exercise.muscles?.length || 0) + (exercise.muscles_secondary?.length || 0);

        if (equipmentCount === 0 && muscleCount <= 1) {
            return 'Beginner';
        } else if (equipmentCount <= 1 && muscleCount <= 3) {
            return 'Intermediate';
        } else {
            return 'Advanced';
        }
    };

    const getCategoryIcon = (categoryName) => {
        const iconMap = {
            'Abs': '🏋️',
            'Arms': '💪',
            'Back': '🏃',
            'Calves': '🦵',
            'Cardio': '❤️',
            'Chest': '💯',
            'Legs': '🦵',
            'Shoulders': '🏋️',
            'Unknown': '🏋️'
        };

        return iconMap[categoryName] || '🏋️';
    };

    const handleSearch = useCallback((query) => {
        console.log('🔍 Search triggered:', query);
        setSearchQuery(query);
    }, []);

    const handleFilterChange = useCallback((newFilters) => {
        console.log('🔧 Filters changed:', newFilters);
        setFilters(newFilters);
    }, []);

    const loadMore = () => {
        if (!searchLoading && hasMore) {
            setCurrentPage(prev => prev + 1);
            loadExercises(false);
        }
    };

    const clearFilters = () => {
        console.log('🧹 Clearing filters');
        setFilters({
            category: '',
            muscle: '',
            equipment: '',
            difficulty: ''
        });
        setSearchQuery('');
    };

    const retryLoading = () => {
        console.log('🔄 Retrying to load exercises...');
        setError(null);
        loadInitialData();
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
                <div className="error-actions">
                    <button onClick={retryLoading} className="btn btn-primary">
                        Try Again
                    </button>
                    <button
                        onClick={() => {
                            setError(null);
                            loadExercises(true);
                        }}
                        className="btn btn-secondary"
                    >
                        Load Basic Exercises
                    </button>
                </div>
            </div>
        );
    }

    console.log('🎨 Rendering ExerciseBrowser with', exercises.length, 'exercises');

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
                                    exercise={exercise}
                                    difficulty={exercise.difficulty}
                                    categoryIcon={exercise.categoryIcon}
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