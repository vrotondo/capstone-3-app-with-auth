import React, { useState, useEffect } from 'react';
import Button from '../../common/Button';
import Input from '../../common/Input';
import trainingService from '../../../services/trainingService';

const SessionForm = ({ session = null, onSubmit, onCancel, isLoading = false }) => {
    const [formData, setFormData] = useState({
        date: '',
        duration: '',
        style: '',
        techniques_practiced: [],
        notes: '',
        intensity_level: 5,
        energy_before: '',
        energy_after: '',
        mood: '',
        calories_burned: '',
        avg_heart_rate: '',
        max_heart_rate: ''
    });

    const [errors, setErrors] = useState({});
    const [techniqueInput, setTechniqueInput] = useState('');

    // Initialize form data when editing
    useEffect(() => {
        if (session) {
            setFormData({
                date: session.date || '',
                duration: session.duration || '',
                style: session.style || '',
                techniques_practiced: session.techniques_practiced || [],
                notes: session.notes || '',
                intensity_level: session.intensity_level || 5,
                energy_before: session.energy_before || '',
                energy_after: session.energy_after || '',
                mood: session.mood || '',
                calories_burned: session.calories_burned || '',
                avg_heart_rate: session.avg_heart_rate || '',
                max_heart_rate: session.max_heart_rate || ''
            });
        } else {
            // Set today's date for new sessions
            const today = new Date().toISOString().split('T')[0];
            setFormData(prev => ({ ...prev, date: today }));
        }
    }, [session]);

    const handleChange = (e) => {
        const { name, value, type } = e.target;

        setFormData(prev => ({
            ...prev,
            [name]: type === 'number' ? (value === '' ? '' : Number(value)) : value
        }));

        // Clear error when user starts typing
        if (errors[name]) {
            setErrors(prev => ({
                ...prev,
                [name]: ''
            }));
        }
    };

    const addTechnique = () => {
        const technique = techniqueInput.trim();
        if (technique && !formData.techniques_practiced.includes(technique)) {
            setFormData(prev => ({
                ...prev,
                techniques_practiced: [...prev.techniques_practiced, technique]
            }));
            setTechniqueInput('');
        }
    };

    const removeTechnique = (index) => {
        setFormData(prev => ({
            ...prev,
            techniques_practiced: prev.techniques_practiced.filter((_, i) => i !== index)
        }));
    };

    const handleTechniqueKeyPress = (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            addTechnique();
        }
    };

    const validateForm = () => {
        const validation = trainingService.validateSessionData(formData);
        setErrors(validation.errors);
        return validation.isValid;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        // Prepare data for submission
        const submissionData = {
            ...formData,
            duration: Number(formData.duration),
            intensity_level: Number(formData.intensity_level),
            energy_before: formData.energy_before ? Number(formData.energy_before) : null,
            energy_after: formData.energy_after ? Number(formData.energy_after) : null,
            calories_burned: formData.calories_burned ? Number(formData.calories_burned) : null,
            avg_heart_rate: formData.avg_heart_rate ? Number(formData.avg_heart_rate) : null,
            max_heart_rate: formData.max_heart_rate ? Number(formData.max_heart_rate) : null,
        };

        await onSubmit(submissionData);
    };

    return (
        <form onSubmit={handleSubmit} className="session-form">
            <div className="form-grid">
                <div className="form-row">
                    <Input
                        type="date"
                        name="date"
                        label="Date"
                        value={formData.date}
                        onChange={handleChange}
                        error={errors.date}
                        required
                    />

                    <Input
                        type="number"
                        name="duration"
                        label="Duration (minutes)"
                        value={formData.duration}
                        onChange={handleChange}
                        error={errors.duration}
                        required
                        min="1"
                        placeholder="60"
                    />
                </div>

                <Input
                    type="text"
                    name="style"
                    label="Martial Art Style"
                    value={formData.style}
                    onChange={handleChange}
                    error={errors.style}
                    required
                    placeholder="e.g., Karate, BJJ, Taekwondo"
                />

                <div className="form-field">
                    <label className="form-label">Techniques Practiced</label>
                    <div className="technique-input-group">
                        <input
                            type="text"
                            value={techniqueInput}
                            onChange={(e) => setTechniqueInput(e.target.value)}
                            onKeyPress={handleTechniqueKeyPress}
                            placeholder="Enter technique name"
                            className="form-input"
                        />
                        <Button
                            type="button"
                            onClick={addTechnique}
                            variant="outline"
                            size="sm"
                            disabled={!techniqueInput.trim()}
                        >
                            Add
                        </Button>
                    </div>

                    {formData.techniques_practiced.length > 0 && (
                        <div className="technique-tags">
                            {formData.techniques_practiced.map((technique, index) => (
                                <span key={index} className="technique-tag">
                                    {technique}
                                    <button
                                        type="button"
                                        onClick={() => removeTechnique(index)}
                                        className="technique-remove"
                                    >
                                        ×
                                    </button>
                                </span>
                            ))}
                        </div>
                    )}
                </div>

                <div className="form-row">
                    <div className="form-field">
                        <label htmlFor="intensity_level" className="form-label">
                            Intensity Level: {formData.intensity_level}/10
                        </label>
                        <input
                            type="range"
                            id="intensity_level"
                            name="intensity_level"
                            min="1"
                            max="10"
                            value={formData.intensity_level}
                            onChange={handleChange}
                            className="form-range"
                        />
                        <div className="range-labels">
                            <span>Light</span>
                            <span>Moderate</span>
                            <span>Intense</span>
                        </div>
                    </div>
                </div>

                <div className="form-row">
                    <Input
                        type="number"
                        name="energy_before"
                        label="Energy Before (1-10)"
                        value={formData.energy_before}
                        onChange={handleChange}
                        error={errors.energy_before}
                        min="1"
                        max="10"
                        placeholder="5"
                    />

                    <Input
                        type="number"
                        name="energy_after"
                        label="Energy After (1-10)"
                        value={formData.energy_after}
                        onChange={handleChange}
                        error={errors.energy_after}
                        min="1"
                        max="10"
                        placeholder="7"
                    />
                </div>

                <Input
                    type="text"
                    name="mood"
                    label="Mood"
                    value={formData.mood}
                    onChange={handleChange}
                    error={errors.mood}
                    placeholder="e.g., Motivated, Tired, Focused"
                />

                <div className="form-row">
                    <Input
                        type="number"
                        name="calories_burned"
                        label="Calories Burned"
                        value={formData.calories_burned}
                        onChange={handleChange}
                        error={errors.calories_burned}
                        min="0"
                        placeholder="300"
                    />

                    <Input
                        type="number"
                        name="avg_heart_rate"
                        label="Avg Heart Rate (BPM)"
                        value={formData.avg_heart_rate}
                        onChange={handleChange}
                        error={errors.avg_heart_rate}
                        min="0"
                        placeholder="140"
                    />

                    <Input
                        type="number"
                        name="max_heart_rate"
                        label="Max Heart Rate (BPM)"
                        value={formData.max_heart_rate}
                        onChange={handleChange}
                        error={errors.max_heart_rate}
                        min="0"
                        placeholder="180"
                    />
                </div>

                <div className="form-field">
                    <label htmlFor="notes" className="form-label">Notes</label>
                    <textarea
                        id="notes"
                        name="notes"
                        value={formData.notes}
                        onChange={handleChange}
                        className="form-textarea"
                        rows="4"
                        placeholder="How did the training go? What did you work on?"
                    />
                    {errors.notes && <span className="form-error">{errors.notes}</span>}
                </div>
            </div>

            <div className="form-actions">
                <Button
                    type="button"
                    variant="outline"
                    onClick={onCancel}
                    disabled={isLoading}
                >
                    Cancel
                </Button>
                <Button
                    type="submit"
                    variant="primary"
                    loading={isLoading}
                >
                    {session ? 'Update Session' : 'Create Session'}
                </Button>
            </div>
        </form>
    );
};

export default SessionForm;