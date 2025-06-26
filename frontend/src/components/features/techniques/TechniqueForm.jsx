import React, { useState, useEffect } from 'react';
import { X, Save, Plus } from 'lucide-react';
import Button from '../../common/Button';
import techniqueService from '../../../services/techniqueService';

const TechniqueForm = ({
    technique = null,
    onSave,
    onCancel,
    isEdit = false
}) => {
    const [formData, setFormData] = useState({
        name: '',
        style: '',
        category: '',
        description: '',
        instructions: '',
        tips: '',
        variations: '',
        difficulty_level: 5,
        belt_level: '',
        tags: []
    });

    const [availableStyles, setAvailableStyles] = useState([]);
    const [availableCategories, setAvailableCategories] = useState([]);
    const [tagInput, setTagInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [errors, setErrors] = useState({});

    useEffect(() => {
        loadFormOptions();

        if (technique && isEdit) {
            setFormData({
                name: technique.name || '',
                style: technique.style || '',
                category: technique.category || '',
                description: technique.description || '',
                instructions: technique.instructions || '',
                tips: technique.tips || '',
                variations: technique.variations || '',
                difficulty_level: technique.difficulty_level || 5,
                belt_level: technique.belt_level || '',
                tags: technique.tags || []
            });
        }
    }, [technique, isEdit]);

    const loadFormOptions = async () => {
        try {
            const [stylesRes, categoriesRes] = await Promise.all([
                techniqueService.getStyles(),
                techniqueService.getCategories()
            ]);

            setAvailableStyles(stylesRes.styles || []);
            setAvailableCategories(categoriesRes.categories || []);
        } catch (error) {
            console.error('Error loading form options:', error);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));

        // Clear error for this field
        if (errors[name]) {
            setErrors(prev => ({
                ...prev,
                [name]: null
            }));
        }
    };

    const handleAddTag = (e) => {
        e.preventDefault();
        const tag = tagInput.trim().toLowerCase();

        if (tag && !formData.tags.includes(tag)) {
            setFormData(prev => ({
                ...prev,
                tags: [...prev.tags, tag]
            }));
            setTagInput('');
        }
    };

    const handleRemoveTag = (tagToRemove) => {
        setFormData(prev => ({
            ...prev,
            tags: prev.tags.filter(tag => tag !== tagToRemove)
        }));
    };

    const validateForm = () => {
        const newErrors = {};

        if (!formData.name.trim()) {
            newErrors.name = 'Technique name is required';
        }

        if (!formData.style.trim()) {
            newErrors.style = 'Martial art style is required';
        }

        if (!formData.description.trim()) {
            newErrors.description = 'Description is required';
        }

        if (formData.difficulty_level < 1 || formData.difficulty_level > 10) {
            newErrors.difficulty_level = 'Difficulty must be between 1 and 10';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        setLoading(true);

        try {
            // This would typically call an API to save the technique
            // For now, we'll just pass the data to the parent component
            if (onSave) {
                await onSave(formData);
            }
        } catch (error) {
            console.error('Error saving technique:', error);
            setErrors({ submit: 'Failed to save technique. Please try again.' });
        } finally {
            setLoading(false);
        }
    };

    const getDifficultyLabel = (level) => {
        if (level <= 3) return 'Beginner';
        if (level <= 6) return 'Intermediate';
        return 'Advanced';
    };

    return (
        <div className="max-w-4xl mx-auto">
            <form onSubmit={handleSubmit} className="space-y-6">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <h2 className="text-2xl font-bold text-gray-900">
                        {isEdit ? 'Edit Technique' : 'Add New Technique'}
                    </h2>
                    <button
                        type="button"
                        onClick={onCancel}
                        className="text-gray-400 hover:text-gray-600"
                    >
                        <X className="h-6 w-6" />
                    </button>
                </div>

                {/* Error Message */}
                {errors.submit && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                        <div className="text-red-800">{errors.submit}</div>
                    </div>
                )}

                {/* Basic Information */}
                <div className="bg-white rounded-lg shadow-sm border p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h3>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* Technique Name */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Technique Name *
                            </label>
                            <input
                                type="text"
                                name="name"
                                value={formData.name}
                                onChange={handleInputChange}
                                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${errors.name ? 'border-red-300' : 'border-gray-300'
                                    }`}
                                placeholder="e.g., Front Kick, Armbar, Horse Stance"
                            />
                            {errors.name && (
                                <p className="mt-1 text-sm text-red-600">{errors.name}</p>
                            )}
                        </div>

                        {/* Martial Art Style */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Martial Art Style *
                            </label>
                            <input
                                type="text"
                                name="style"
                                value={formData.style}
                                onChange={handleInputChange}
                                list="styles"
                                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${errors.style ? 'border-red-300' : 'border-gray-300'
                                    }`}
                                placeholder="e.g., Karate, BJJ, Muay Thai"
                            />
                            <datalist id="styles">
                                {availableStyles.map(style => (
                                    <option key={style} value={style} />
                                ))}
                            </datalist>
                            {errors.style && (
                                <p className="mt-1 text-sm text-red-600">{errors.style}</p>
                            )}
                        </div>

                        {/* Category */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Category
                            </label>
                            <input
                                type="text"
                                name="category"
                                value={formData.category}
                                onChange={handleInputChange}
                                list="categories"
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                placeholder="e.g., Kicks, Throws, Submissions"
                            />
                            <datalist id="categories">
                                {availableCategories.map(category => (
                                    <option key={category} value={category} />
                                ))}
                            </datalist>
                        </div>

                        {/* Belt Level */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Belt Level
                            </label>
                            <input
                                type="text"
                                name="belt_level"
                                value={formData.belt_level}
                                onChange={handleInputChange}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                placeholder="e.g., White Belt, Blue Belt, Dan 1"
                            />
                        </div>
                    </div>

                    {/* Difficulty Level */}
                    <div className="mt-4">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Difficulty Level: {formData.difficulty_level}/10 ({getDifficultyLabel(formData.difficulty_level)})
                        </label>
                        <input
                            type="range"
                            name="difficulty_level"
                            min="1"
                            max="10"
                            value={formData.difficulty_level}
                            onChange={handleInputChange}
                            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                        />
                        <div className="flex justify-between text-xs text-gray-500 mt-1">
                            <span>1 - Very Easy</span>
                            <span>5 - Moderate</span>
                            <span>10 - Expert</span>
                        </div>
                        {errors.difficulty_level && (
                            <p className="mt-1 text-sm text-red-600">{errors.difficulty_level}</p>
                        )}
                    </div>
                </div>

                {/* Content */}
                <div className="bg-white rounded-lg shadow-sm border p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Technique Content</h3>

                    {/* Description */}
                    <div className="mb-4">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Description *
                        </label>
                        <textarea
                            name="description"
                            value={formData.description}
                            onChange={handleInputChange}
                            rows="3"
                            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${errors.description ? 'border-red-300' : 'border-gray-300'
                                }`}
                            placeholder="Brief overview of the technique..."
                        />
                        {errors.description && (
                            <p className="mt-1 text-sm text-red-600">{errors.description}</p>
                        )}
                    </div>

                    {/* Instructions */}
                    <div className="mb-4">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Step-by-Step Instructions
                        </label>
                        <textarea
                            name="instructions"
                            value={formData.instructions}
                            onChange={handleInputChange}
                            rows="5"
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            placeholder="1. Step one...&#10;2. Step two...&#10;3. Step three..."
                        />
                    </div>

                    {/* Tips */}
                    <div className="mb-4">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Tips & Common Mistakes
                        </label>
                        <textarea
                            name="tips"
                            value={formData.tips}
                            onChange={handleInputChange}
                            rows="3"
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            placeholder="Tips for better execution, common mistakes to avoid..."
                        />
                    </div>

                    {/* Variations */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Variations & Applications
                        </label>
                        <textarea
                            name="variations"
                            value={formData.variations}
                            onChange={handleInputChange}
                            rows="3"
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            placeholder="Different variations or applications of this technique..."
                        />
                    </div>
                </div>

                {/* Tags */}
                <div className="bg-white rounded-lg shadow-sm border p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Tags</h3>

                    <div className="flex gap-2 mb-3">
                        <input
                            type="text"
                            value={tagInput}
                            onChange={(e) => setTagInput(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && handleAddTag(e)}
                            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            placeholder="Add tags (e.g., defensive, grappling, counter)"
                        />
                        <Button
                            type="button"
                            onClick={handleAddTag}
                            variant="outline"
                            size="sm"
                        >
                            <Plus className="h-4 w-4" />
                        </Button>
                    </div>

                    <div className="flex flex-wrap gap-2">
                        {formData.tags.map((tag, index) => (
                            <span
                                key={index}
                                className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
                            >
                                #{tag}
                                <button
                                    type="button"
                                    onClick={() => handleRemoveTag(tag)}
                                    className="ml-2 text-blue-600 hover:text-blue-800"
                                >
                                    <X className="h-3 w-3" />
                                </button>
                            </span>
                        ))}
                    </div>
                </div>

                {/* Actions */}
                <div className="flex justify-end gap-4">
                    <Button
                        type="button"
                        variant="outline"
                        onClick={onCancel}
                    >
                        Cancel
                    </Button>
                    <Button
                        type="submit"
                        disabled={loading}
                    >
                        {loading ? (
                            <>
                                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                                Saving...
                            </>
                        ) : (
                            <>
                                <Save className="h-4 w-4 mr-2" />
                                {isEdit ? 'Update Technique' : 'Save Technique'}
                            </>
                        )}
                    </Button>
                </div>
            </form>

            {/* Custom styles for the range slider */}
            <style jsx>{`
                .slider::-webkit-slider-thumb {
                    appearance: none;
                    height: 20px;
                    width: 20px;
                    border-radius: 50%;
                    background: #3B82F6;
                    cursor: pointer;
                    box-shadow: 0 0 2px rgba(0,0,0,.2);
                }
                
                .slider::-moz-range-thumb {
                    height: 20px;
                    width: 20px;
                    border-radius: 50%;
                    background: #3B82F6;
                    cursor: pointer;
                    border: none;
                    box-shadow: 0 0 2px rgba(0,0,0,.2);
                }
            `}</style>
        </div>
    );
};

export default TechniqueForm;