import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import Button from '../components/common/Button';
import LoadingSpinner from '../components/common/LoadingSpinner';
import '../styles/pages/techniques.css';

const Techniques = () => {
    const { user } = useAuth();
    const [activeTab, setActiveTab] = useState('browse');
    const [techniques, setTechniques] = useState([]);
    const [myTechniques, setMyTechniques] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedStyle, setSelectedStyle] = useState('all');
    const [isLoading, setIsLoading] = useState(false);
    const [showAddForm, setShowAddForm] = useState(false);

    // Sample technique data (replace with API calls later)
    const sampleTechniques = [
        {
            id: 1,
            name: "Front Kick (Mae Geri)",
            style: "Karate",
            category: "Kicks",
            difficulty: "Beginner",
            description: "A basic straight kick using the ball of the foot",
            video_url: "https://example.com/video1",
            steps: [
                "Start in fighting stance",
                "Lift knee to chest height",
                "Extend leg straight forward",
                "Strike with ball of foot",
                "Retract leg quickly"
            ]
        },
        {
            id: 2,
            name: "Roundhouse Kick (Mawashi Geri)",
            style: "Karate",
            category: "Kicks",
            difficulty: "Intermediate",
            description: "A circular kick striking with the instep or shin",
            video_url: "https://example.com/video2",
            steps: [
                "Start in fighting stance",
                "Pivot on supporting foot",
                "Lift knee to side",
                "Snap kick in circular motion",
                "Return to stance"
            ]
        },
        {
            id: 3,
            name: "Jab Cross Combination",
            style: "Boxing",
            category: "Punches",
            difficulty: "Beginner",
            description: "Basic two-punch combination",
            video_url: "https://example.com/video3",
            steps: [
                "Start in boxing stance",
                "Throw quick jab with lead hand",
                "Immediately follow with cross",
                "Return hands to guard position"
            ]
        }
    ];

    const [newTechnique, setNewTechnique] = useState({
        name: '',
        style: '',
        category: '',
        difficulty: 'Beginner',
        description: '',
        notes: '',
        mastery_level: 'Learning'
    });

    useEffect(() => {
        loadTechniques();
        loadMyTechniques();
    }, []);

    const loadTechniques = async () => {
        setIsLoading(true);
        try {
            // TODO: Replace with actual API call
            // const response = await techniqueService.getAllTechniques();
            setTechniques(sampleTechniques);
        } catch (error) {
            console.error('Failed to load techniques:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const loadMyTechniques = async () => {
        try {
            // TODO: Replace with actual API call
            // const response = await techniqueService.getMyTechniques();
            setMyTechniques([]);
        } catch (error) {
            console.error('Failed to load my techniques:', error);
        }
    };

    const filteredTechniques = techniques.filter(technique => {
        const matchesSearch = technique.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            technique.description.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesStyle = selectedStyle === 'all' || technique.style === selectedStyle;
        return matchesSearch && matchesStyle;
    });

    const handleAddTechnique = async (e) => {
        e.preventDefault();
        try {
            // TODO: Replace with actual API call
            // const response = await techniqueService.addMyTechnique(newTechnique);
            const newTechniqueWithId = {
                ...newTechnique,
                id: Date.now(),
                date_added: new Date().toISOString()
            };
            setMyTechniques([...myTechniques, newTechniqueWithId]);
            setNewTechnique({
                name: '',
                style: '',
                category: '',
                difficulty: 'Beginner',
                description: '',
                notes: '',
                mastery_level: 'Learning'
            });
            setShowAddForm(false);
        } catch (error) {
            console.error('Failed to add technique:', error);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setNewTechnique(prev => ({
            ...prev,
            [name]: value
        }));
    };

    if (isLoading) {
        return <LoadingSpinner />;
    }

    return (
        <div className="techniques-page">
            <div className="page-header">
                <h1>Technique Library</h1>
                <p>Discover and manage your martial arts techniques</p>
            </div>

            <div className="techniques-tabs">
                <button
                    className={`tab-button ${activeTab === 'browse' ? 'active' : ''}`}
                    onClick={() => setActiveTab('browse')}
                >
                    Browse Techniques
                </button>
                <button
                    className={`tab-button ${activeTab === 'my-techniques' ? 'active' : ''}`}
                    onClick={() => setActiveTab('my-techniques')}
                >
                    My Techniques ({myTechniques.length})
                </button>
            </div>

            {activeTab === 'browse' && (
                <div className="browse-techniques">
                    <div className="techniques-filters">
                        <div className="search-bar">
                            <input
                                type="text"
                                placeholder="Search techniques..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="form-input"
                            />
                        </div>
                        <div className="style-filter">
                            <select
                                value={selectedStyle}
                                onChange={(e) => setSelectedStyle(e.target.value)}
                                className="form-select"
                            >
                                <option value="all">All Styles</option>
                                <option value="Karate">Karate</option>
                                <option value="Taekwondo">Taekwondo</option>
                                <option value="Boxing">Boxing</option>
                                <option value="Muay Thai">Muay Thai</option>
                                <option value="BJJ">Brazilian Jiu-Jitsu</option>
                            </select>
                        </div>
                    </div>

                    <div className="techniques-grid">
                        {filteredTechniques.map(technique => (
                            <div key={technique.id} className="technique-card">
                                <div className="technique-header">
                                    <h3>{technique.name}</h3>
                                    <span className={`difficulty-badge ${technique.difficulty.toLowerCase()}`}>
                                        {technique.difficulty}
                                    </span>
                                </div>
                                <div className="technique-meta">
                                    <span className="technique-style">{technique.style}</span>
                                    <span className="technique-category">{technique.category}</span>
                                </div>
                                <p className="technique-description">{technique.description}</p>
                                <div className="technique-actions">
                                    <Button variant="outline" size="sm">
                                        View Details
                                    </Button>
                                    <Button variant="primary" size="sm">
                                        Add to My Techniques
                                    </Button>
                                </div>
                            </div>
                        ))}
                    </div>

                    {filteredTechniques.length === 0 && (
                        <div className="no-results">
                            <p>No techniques found matching your criteria.</p>
                        </div>
                    )}
                </div>
            )}

            {activeTab === 'my-techniques' && (
                <div className="my-techniques">
                    <div className="my-techniques-header">
                        <h2>Your Personal Technique Collection</h2>
                        <Button
                            variant="primary"
                            onClick={() => setShowAddForm(true)}
                        >
                            Add New Technique
                        </Button>
                    </div>

                    {showAddForm && (
                        <div className="add-technique-form">
                            <div className="form-header">
                                <h3>Add New Technique</h3>
                                <button
                                    className="close-button"
                                    onClick={() => setShowAddForm(false)}
                                >
                                    ×
                                </button>
                            </div>
                            <form onSubmit={handleAddTechnique}>
                                <div className="form-grid">
                                    <div className="form-group">
                                        <label>Technique Name *</label>
                                        <input
                                            type="text"
                                            name="name"
                                            value={newTechnique.name}
                                            onChange={handleInputChange}
                                            className="form-input"
                                            required
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>Martial Art Style *</label>
                                        <input
                                            type="text"
                                            name="style"
                                            value={newTechnique.style}
                                            onChange={handleInputChange}
                                            className="form-input"
                                            required
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>Category</label>
                                        <select
                                            name="category"
                                            value={newTechnique.category}
                                            onChange={handleInputChange}
                                            className="form-select"
                                        >
                                            <option value="">Select category</option>
                                            <option value="Kicks">Kicks</option>
                                            <option value="Punches">Punches</option>
                                            <option value="Throws">Throws</option>
                                            <option value="Grappling">Grappling</option>
                                            <option value="Blocks">Blocks</option>
                                            <option value="Kata/Forms">Kata/Forms</option>
                                        </select>
                                    </div>
                                    <div className="form-group">
                                        <label>Difficulty Level</label>
                                        <select
                                            name="difficulty"
                                            value={newTechnique.difficulty}
                                            onChange={handleInputChange}
                                            className="form-select"
                                        >
                                            <option value="Beginner">Beginner</option>
                                            <option value="Intermediate">Intermediate</option>
                                            <option value="Advanced">Advanced</option>
                                        </select>
                                    </div>
                                    <div className="form-group">
                                        <label>Mastery Level</label>
                                        <select
                                            name="mastery_level"
                                            value={newTechnique.mastery_level}
                                            onChange={handleInputChange}
                                            className="form-select"
                                        >
                                            <option value="Learning">Learning</option>
                                            <option value="Practicing">Practicing</option>
                                            <option value="Proficient">Proficient</option>
                                            <option value="Mastered">Mastered</option>
                                        </select>
                                    </div>
                                </div>
                                <div className="form-group">
                                    <label>Description</label>
                                    <textarea
                                        name="description"
                                        value={newTechnique.description}
                                        onChange={handleInputChange}
                                        className="form-textarea"
                                        rows="3"
                                        placeholder="Describe the technique..."
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Personal Notes</label>
                                    <textarea
                                        name="notes"
                                        value={newTechnique.notes}
                                        onChange={handleInputChange}
                                        className="form-textarea"
                                        rows="3"
                                        placeholder="Your notes, tips, or observations..."
                                    />
                                </div>
                                <div className="form-actions">
                                    <Button
                                        type="button"
                                        variant="outline"
                                        onClick={() => setShowAddForm(false)}
                                    >
                                        Cancel
                                    </Button>
                                    <Button type="submit" variant="primary">
                                        Add Technique
                                    </Button>
                                </div>
                            </form>
                        </div>
                    )}

                    <div className="my-techniques-grid">
                        {myTechniques.map(technique => (
                            <div key={technique.id} className="my-technique-card">
                                <div className="technique-header">
                                    <h3>{technique.name}</h3>
                                    <span className={`mastery-badge ${technique.mastery_level.toLowerCase()}`}>
                                        {technique.mastery_level}
                                    </span>
                                </div>
                                <div className="technique-meta">
                                    <span className="technique-style">{technique.style}</span>
                                    {technique.category && (
                                        <span className="technique-category">{technique.category}</span>
                                    )}
                                </div>
                                {technique.description && (
                                    <p className="technique-description">{technique.description}</p>
                                )}
                                {technique.notes && (
                                    <div className="technique-notes">
                                        <strong>Notes:</strong> {technique.notes}
                                    </div>
                                )}
                                <div className="technique-actions">
                                    <Button variant="outline" size="sm">
                                        Edit
                                    </Button>
                                    <Button variant="outline" size="sm">
                                        Update Progress
                                    </Button>
                                </div>
                            </div>
                        ))}
                    </div>

                    {myTechniques.length === 0 && (
                        <div className="no-techniques">
                            <div className="empty-state">
                                <h3>No techniques added yet</h3>
                                <p>Start building your personal technique library by adding techniques you're learning or practicing.</p>
                                <Button
                                    variant="primary"
                                    onClick={() => setShowAddForm(true)}
                                >
                                    Add Your First Technique
                                </Button>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default Techniques;