import React, { useState, useEffect } from 'react';
import { useAuth } from '../../../context/AuthContext';
import wgerService from '../../../services/wgerService';
import workoutService from '../../../services/workoutService';
import LoadingSpinner from '../../common/LoadingSpinner';

const ExerciseBrowser = () => {
    const { isAuthenticated } = useAuth();
    const [exercises, setExercises] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [favorites, setFavorites] = useState({});
    const [workoutPlans, setWorkoutPlans] = useState([]);
    const [showWorkoutModal, setShowWorkoutModal] = useState(false);
    const [selectedExercise, setSelectedExercise] = useState(null);

    useEffect(() => {
        loadExercises();
        if (isAuthenticated) {
            loadFavorites();
            loadWorkoutPlans();
        }
    }, [isAuthenticated]);

    const loadExercises = async () => {
        try {
            setLoading(true);
            setError(null);

            console.log('🔄 Loading exercises...');
            const response = await wgerService.getMartialArtsExercises(50);
            console.log('📊 Response:', response);

            if (response.success && response.exercises) {
                // Create better exercise names based on available data
                const enhancedExercises = response.exercises.map(exercise => ({
                    ...exercise,
                    displayName: generateBetterName(exercise),
                    displayDescription: generateBetterDescription(exercise)
                }));

                setExercises(enhancedExercises);
                console.log('✅ Set exercises:', enhancedExercises.length);
            } else {
                setError('Failed to load exercises');
            }
        } catch (err) {
            console.error('❌ Error:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const loadFavorites = async () => {
        try {
            const response = await workoutService.getFavorites();
            if (response.success) {
                const favoriteMap = {};
                response.favorites.forEach(fav => {
                    favoriteMap[fav.exercise_id] = true;
                });
                setFavorites(favoriteMap);
            }
        } catch (error) {
            console.error('Error loading favorites:', error);
        }
    };

    const loadWorkoutPlans = async () => {
        try {
            const response = await workoutService.getWorkoutPlans();
            if (response.success) {
                setWorkoutPlans(response.workout_plans);
            }
        } catch (error) {
            console.error('Error loading workout plans:', error);
        }
    };

    const generateBetterName = (exercise) => {
        // Create better names based on category and equipment
        const category = exercise.category || 'Exercise';
        const equipment = exercise.equipment || [];
        const muscles = exercise.muscles || [];

        if (equipment.length > 0 && muscles.length > 0) {
            return `${category} - ${equipment[0]} (${muscles[0]})`;
        } else if (equipment.length > 0) {
            return `${category} - ${equipment[0]}`;
        } else if (muscles.length > 0) {
            return `${category} - ${muscles[0]}`;
        } else {
            return `${category} Exercise #${exercise.id}`;
        }
    };

    const generateBetterDescription = (exercise) => {
        const parts = [];

        if (exercise.category) {
            parts.push(`Category: ${exercise.category}`);
        }

        if (exercise.muscles && exercise.muscles.length > 0) {
            parts.push(`Targets: ${exercise.muscles.join(', ')}`);
        }

        if (exercise.equipment && exercise.equipment.length > 0) {
            parts.push(`Equipment: ${exercise.equipment.join(', ')}`);
        }

        return parts.length > 0 ? parts.join(' • ') : 'Exercise from WGER database';
    };

    const handleFavoriteToggle = async (exercise) => {
        if (!isAuthenticated) {
            alert('Please log in to save favorites');
            return;
        }

        const isFavorited = favorites[exercise.id];

        try {
            if (isFavorited) {
                const response = await workoutService.removeFromFavorites(exercise.id);
                if (response.success) {
                    setFavorites(prev => ({
                        ...prev,
                        [exercise.id]: false
                    }));
                } else {
                    alert('Failed to remove from favorites: ' + response.error);
                }
            } else {
                const response = await workoutService.addToFavorites(exercise);
                if (response.success) {
                    setFavorites(prev => ({
                        ...prev,
                        [exercise.id]: true
                    }));
                } else {
                    alert('Failed to add to favorites: ' + response.error);
                }
            }
        } catch (error) {
            alert('Error updating favorites: ' + error.message);
        }
    };

    const handleAddToWorkout = (exercise) => {
        if (!isAuthenticated) {
            alert('Please log in to create workouts');
            return;
        }

        setSelectedExercise(exercise);
        setShowWorkoutModal(true);
    };

    const handleWorkoutSelection = async (planId) => {
        try {
            const response = await workoutService.addExerciseToWorkout(planId, selectedExercise);
            if (response.success) {
                alert(`Added "${selectedExercise.displayName}" to workout!`);
                setShowWorkoutModal(false);
                setSelectedExercise(null);
            } else {
                alert('Failed to add to workout: ' + response.error);
            }
        } catch (error) {
            alert('Error adding to workout: ' + error.message);
        }
    };

    const handleCreateNewWorkout = async () => {
        const workoutName = prompt('Enter name for new workout:');
        if (!workoutName) return;

        try {
            const createResponse = await workoutService.createWorkoutPlan(workoutName);
            if (createResponse.success) {
                const addResponse = await workoutService.addExerciseToWorkout(
                    createResponse.workout_plan.id,
                    selectedExercise
                );
                if (addResponse.success) {
                    alert(`Created workout "${workoutName}" and added exercise!`);
                    loadWorkoutPlans(); // Refresh workout plans
                    setShowWorkoutModal(false);
                    setSelectedExercise(null);
                } else {
                    alert('Workout created but failed to add exercise: ' + addResponse.error);
                }
            } else {
                alert('Failed to create workout: ' + createResponse.error);
            }
        } catch (error) {
            alert('Error creating workout: ' + error.message);
        }
    };

    if (loading) {
        return (
            <div style={{ padding: '20px', textAlign: 'center' }}>
                <LoadingSpinner />
                <p>Loading exercises...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div style={{ padding: '20px', textAlign: 'center' }}>
                <h3>Error Loading Exercises</h3>
                <p>{error}</p>
                <button onClick={loadExercises} style={{ padding: '10px 20px', margin: '10px' }}>
                    Try Again
                </button>
            </div>
        );
    }

    return (
        <div style={{ padding: '20px' }}>
            <h1>Exercise Database</h1>
            <p>Showing {exercises.length} exercises from WGER</p>
            <p style={{ fontSize: '14px', color: '#666' }}>
                Note: Exercise names are generated from available category/muscle/equipment data
            </p>

            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
                gap: '20px',
                marginTop: '20px'
            }}>
                {exercises.map((exercise) => (
                    <div
                        key={exercise.id}
                        style={{
                            border: '1px solid #ddd',
                            borderRadius: '8px',
                            padding: '16px',
                            backgroundColor: '#fff',
                            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                        }}
                    >
                        <h3 style={{ margin: '0 0 10px 0', color: '#333', fontSize: '16px' }}>
                            {exercise.displayName}
                        </h3>

                        <p style={{ margin: '0 0 15px 0', color: '#666', fontSize: '14px' }}>
                            {exercise.displayDescription}
                        </p>

                        <div style={{ fontSize: '12px', color: '#888', marginBottom: '15px' }}>
                            Exercise ID: {exercise.id} | UUID: {exercise.uuid?.substring(0, 8)}...
                        </div>

                        <div style={{ marginTop: '15px', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                            <button
                                style={{
                                    padding: '8px 16px',
                                    backgroundColor: '#10b981',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '4px',
                                    cursor: 'pointer',
                                    fontSize: '12px'
                                }}
                                onClick={() => {
                                    // Search for the exercise on Google
                                    const searchTerm = exercise.displayName.replace(/Exercise #\d+/, '').trim();
                                    const googleUrl = `https://www.google.com/search?q=${encodeURIComponent(searchTerm + ' exercise')}`;
                                    window.open(googleUrl, '_blank');
                                }}
                            >
                                Search Exercise
                            </button>

                            {isAuthenticated && (
                                <button
                                    style={{
                                        padding: '8px 16px',
                                        backgroundColor: favorites[exercise.id] ? '#ef4444' : '#6b7280',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: '4px',
                                        cursor: 'pointer',
                                        fontSize: '12px'
                                    }}
                                    onClick={() => handleFavoriteToggle(exercise)}
                                >
                                    {favorites[exercise.id] ? '❤️ Favorited' : '🤍 Favorite'}
                                </button>
                            )}

                            {isAuthenticated && (
                                <button
                                    style={{
                                        padding: '8px 16px',
                                        backgroundColor: '#3b82f6',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: '4px',
                                        cursor: 'pointer',
                                        fontSize: '12px'
                                    }}
                                    onClick={() => handleAddToWorkout(exercise)}
                                >
                                    Add to Workout
                                </button>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            {exercises.length === 0 && (
                <div style={{ textAlign: 'center', padding: '40px' }}>
                    <h3>No exercises found</h3>
                    <button onClick={loadExercises} style={{ padding: '10px 20px' }}>
                        Reload
                    </button>
                </div>
            )}

            {/* Workout Modal */}
            {showWorkoutModal && (
                <div style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: 'rgba(0,0,0,0.5)',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    zIndex: 1000
                }}>
                    <div style={{
                        backgroundColor: 'white',
                        padding: '20px',
                        borderRadius: '8px',
                        maxWidth: '400px',
                        width: '90%',
                        maxHeight: '80vh',
                        overflowY: 'auto'
                    }}>
                        <h3>Add to Workout</h3>
                        <p>Adding: <strong>{selectedExercise?.displayName}</strong></p>

                        <div style={{ marginBottom: '20px' }}>
                            <h4>Select Workout Plan:</h4>
                            {workoutPlans.length === 0 ? (
                                <p>No workout plans found.</p>
                            ) : (
                                workoutPlans.map(plan => (
                                    <div key={plan.id} style={{ marginBottom: '10px' }}>
                                        <button
                                            style={{
                                                padding: '10px 15px',
                                                backgroundColor: '#f3f4f6',
                                                border: '1px solid #d1d5db',
                                                borderRadius: '4px',
                                                cursor: 'pointer',
                                                width: '100%',
                                                textAlign: 'left'
                                            }}
                                            onClick={() => handleWorkoutSelection(plan.id)}
                                        >
                                            <strong>{plan.name}</strong>
                                            <div style={{ fontSize: '12px', color: '#666' }}>
                                                {plan.exercise_count} exercises
                                            </div>
                                        </button>
                                    </div>
                                ))
                            )}
                        </div>

                        <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                            <button
                                style={{
                                    padding: '10px 20px',
                                    backgroundColor: '#10b981',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '4px',
                                    cursor: 'pointer'
                                }}
                                onClick={handleCreateNewWorkout}
                            >
                                Create New Workout
                            </button>
                            <button
                                style={{
                                    padding: '10px 20px',
                                    backgroundColor: '#6b7280',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '4px',
                                    cursor: 'pointer'
                                }}
                                onClick={() => {
                                    setShowWorkoutModal(false);
                                    setSelectedExercise(null);
                                }}
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ExerciseBrowser;