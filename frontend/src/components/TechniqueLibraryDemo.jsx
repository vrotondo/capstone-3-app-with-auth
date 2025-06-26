import React, { useState } from 'react';
import {
    Search, Star, BookOpen, Eye, ArrowLeft, Target, Lightbulb,
    List, Award, Plus, Clock, BarChart3, Calendar, Trash2, Dumbbell
} from 'lucide-react';

// Mock data
const mockTechniques = [
    {
        id: 1,
        name: 'Front Kick',
        style: 'Karate',
        category: 'Kicks',
        difficulty_level: 3,
        description: 'A basic straight kick delivered with the ball of the foot.',
        instructions: '1. Stand in fighting stance\n2. Lift knee to chamber position\n3. Extend leg straight forward\n4. Strike with ball of foot',
        tips: 'Keep your balance on the standing leg.',
        tags: ['basic', 'linear', 'striking'],
        view_count: 245,
        bookmark_count: 18
    },
    {
        id: 2,
        name: 'Roundhouse Kick',
        style: 'Taekwondo',
        category: 'Kicks',
        difficulty_level: 5,
        description: 'A circular kick delivered with the top of the foot or shin.',
        instructions: '1. Stand in fighting stance\n2. Pivot on supporting foot\n3. Lift knee to side\n4. Snap leg in circular motion',
        tips: 'Pivot fully on the supporting foot.',
        tags: ['intermediate', 'circular', 'striking'],
        view_count: 189,
        bookmark_count: 25
    },
    {
        id: 3,
        name: 'Basic Jab',
        style: 'Boxing',
        category: 'Punches',
        difficulty_level: 2,
        description: 'A quick, straight punch thrown with the lead hand.',
        instructions: '1. Stand in boxing stance\n2. Extend lead hand straight forward\n3. Rotate fist so palm faces down',
        tips: 'Keep it quick and snappy.',
        tags: ['basic', 'boxing', 'hand-technique'],
        view_count: 156,
        bookmark_count: 12
    }
];

const mockBookmarks = [
    {
        id: 1,
        technique_id: 1,
        technique: mockTechniques[0],
        mastery_level: 6,
        practice_count: 8,
        personal_notes: 'Working on keeping better balance.',
        last_practiced: '2025-06-20'
    },
    {
        id: 2,
        technique_id: 2,
        technique: mockTechniques[1],
        mastery_level: 4,
        practice_count: 5,
        personal_notes: 'Still working on the pivot.',
        last_practiced: '2025-06-18'
    }
];

// Utility functions
const getDifficultyColor = (level) => {
    if (level <= 3) return 'bg-green-500';
    if (level <= 6) return 'bg-yellow-500';
    return 'bg-red-500';
};

const getDifficultyText = (level) => {
    if (level <= 3) return 'Beginner';
    if (level <= 6) return 'Intermediate';
    return 'Advanced';
};

const getMasteryColor = (level) => {
    if (level <= 2) return 'text-red-600 bg-red-50';
    if (level <= 4) return 'text-yellow-600 bg-yellow-50';
    if (level <= 7) return 'text-blue-600 bg-blue-50';
    return 'text-green-600 bg-green-50';
};

const getMasteryText = (level) => {
    if (level <= 2) return 'Learning';
    if (level <= 4) return 'Practicing';
    if (level <= 7) return 'Improving';
    return 'Mastered';
};

// Navigation Component
const DemoNavigation = ({ currentView, setCurrentView }) => (
    <nav className="bg-white shadow-lg border-b border-gray-200 mb-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
                <div className="flex items-center">
                    <div className="flex items-center space-x-2">
                        <Dumbbell className="h-8 w-8 text-blue-600" />
                        <span className="text-xl font-bold text-gray-900">DojoTracker</span>
                    </div>
                </div>

                <div className="flex items-center space-x-8">
                    <button
                        onClick={() => setCurrentView('library')}
                        className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${currentView === 'library'
                                ? 'text-blue-600 bg-blue-50'
                                : 'text-gray-700 hover:text-blue-600'
                            }`}
                    >
                        <BookOpen className="h-4 w-4" />
                        <span>Library</span>
                    </button>

                    <button
                        onClick={() => setCurrentView('bookmarks')}
                        className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${currentView === 'bookmarks'
                                ? 'text-blue-600 bg-blue-50'
                                : 'text-gray-700 hover:text-blue-600'
                            }`}
                    >
                        <Star className="h-4 w-4" />
                        <span>My Techniques</span>
                    </button>

                    <div className="flex items-center space-x-3 px-3 py-2 rounded-md bg-gray-50">
                        <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                            J
                        </div>
                        <div className="text-sm">
                            <div className="font-medium text-gray-900">John Doe</div>
                            <div className="text-gray-500">Karate</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </nav>
);

// Search and Filter Component
const SearchFilters = ({ searchQuery, setSearchQuery, selectedStyle, setSelectedStyle }) => (
    <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
        <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex-1">
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                    <input
                        type="text"
                        placeholder="Search techniques..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                </div>
            </div>

            <select
                value={selectedStyle}
                onChange={(e) => setSelectedStyle(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
                <option value="">All Styles</option>
                <option value="Karate">Karate</option>
                <option value="Taekwondo">Taekwondo</option>
                <option value="Boxing">Boxing</option>
            </select>
        </div>
    </div>
);

// Technique Card Component
const TechniqueCard = ({ technique, onSelect, isBookmarked = false }) => (
    <div
        className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow cursor-pointer"
        onClick={() => onSelect(technique)}
    >
        <div className="p-6">
            <div className="flex items-start justify-between">
                <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900 hover:text-blue-600">
                            {technique.name}
                        </h3>
                        <span className={`px-2 py-1 text-xs font-medium text-white rounded-full ${getDifficultyColor(technique.difficulty_level)}`}>
                            {getDifficultyText(technique.difficulty_level)}
                        </span>
                    </div>

                    <div className="text-sm text-gray-600 mb-3">
                        <span className="font-medium text-blue-600">{technique.style}</span>
                        {technique.category && <span className="text-gray-500"> • {technique.category}</span>}
                    </div>

                    <p className="text-sm text-gray-600 line-clamp-2 mb-3">
                        {technique.description}
                    </p>

                    <div className="flex items-center justify-between text-sm text-gray-500">
                        <div className="flex items-center gap-1">
                            <Eye className="h-4 w-4" />
                            <span>{technique.view_count} views</span>
                        </div>

                        <div className="flex gap-1">
                            {technique.tags?.slice(0, 2).map((tag, index) => (
                                <span key={index} className="px-2 py-1 text-xs bg-gray-100 rounded">
                                    {tag}
                                </span>
                            ))}
                        </div>
                    </div>
                </div>

                <Star className={`h-5 w-5 ml-2 ${isBookmarked ? 'text-yellow-500 fill-current' : 'text-gray-400'}`} />
            </div>
        </div>
    </div>
);

// Technique Detail Component
const TechniqueDetail = ({ technique, onBack, isBookmarked, setIsBookmarked }) => (
    <div>
        {/* Header */}
        <div className="bg-white shadow-sm border-b rounded-lg mb-8">
            <div className="px-6 py-6">
                <div className="flex items-center justify-between">
                    <button
                        onClick={onBack}
                        className="flex items-center text-gray-600 hover:text-gray-900"
                    >
                        <ArrowLeft className="h-5 w-5 mr-2" />
                        Back to Library
                    </button>

                    <button
                        onClick={() => setIsBookmarked(!isBookmarked)}
                        className={`flex items-center px-4 py-2 rounded-lg transition-colors ${isBookmarked
                                ? 'bg-yellow-100 text-yellow-700'
                                : 'bg-gray-100 text-gray-700'
                            }`}
                    >
                        <Star className={`h-5 w-5 mr-2 ${isBookmarked ? 'fill-current' : ''}`} />
                        {isBookmarked ? 'Bookmarked' : 'Bookmark'}
                    </button>
                </div>
            </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Main Content */}
            <div className="lg:col-span-2 space-y-6">
                {/* Technique Header */}
                <div className="bg-white rounded-lg shadow-sm p-6">
                    <h1 className="text-3xl font-bold text-gray-900 mb-4">{technique.name}</h1>

                    <div className="flex flex-wrap items-center gap-4 mb-4">
                        <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                            {technique.style}
                        </span>
                        <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
                            {technique.category}
                        </span>
                        <span className={`px-3 py-1 text-white rounded-full text-sm font-medium ${getDifficultyColor(technique.difficulty_level)}`}>
                            {getDifficultyText(technique.difficulty_level)} ({technique.difficulty_level}/10)
                        </span>
                    </div>

                    <div className="flex items-center gap-6 text-sm text-gray-600">
                        <div className="flex items-center gap-1">
                            <Eye className="h-4 w-4" />
                            <span>{technique.view_count} views</span>
                        </div>
                        <div className="flex items-center gap-1">
                            <Star className="h-4 w-4" />
                            <span>{technique.bookmark_count} bookmarks</span>
                        </div>
                    </div>

                    {technique.tags && (
                        <div className="mt-4 flex flex-wrap gap-2">
                            {technique.tags.map((tag, index) => (
                                <span key={index} className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-sm">
                                    #{tag}
                                </span>
                            ))}
                        </div>
                    )}
                </div>

                {/* Content Sections */}
                <ContentSection
                    title="Description"
                    icon={<BookOpen className="h-5 w-5 text-blue-600" />}
                    content={technique.description}
                />

                <ContentSection
                    title="Instructions"
                    icon={<List className="h-5 w-5 text-green-600" />}
                    content={technique.instructions}
                    isMultiline
                />

                <ContentSection
                    title="Tips"
                    icon={<Lightbulb className="h-5 w-5 text-yellow-600" />}
                    content={technique.tips}
                />
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
                <QuickInfo technique={technique} />
                {isBookmarked && <ProgressTracker />}
            </div>
        </div>
    </div>
);

// Content Section Component
const ContentSection = ({ title, icon, content, isMultiline = false }) => (
    <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            {icon}
            <span className="ml-2">{title}</span>
        </h2>
        <div className="text-gray-700">
            {isMultiline ? (
                content.split('\n').map((line, index) => (
                    <p key={index} className="mb-2">{line}</p>
                ))
            ) : (
                <p>{content}</p>
            )}
        </div>
    </div>
);

// Quick Info Sidebar Component
const QuickInfo = ({ technique }) => (
    <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Info</h3>
        <div className="space-y-3">
            <InfoItem label="Martial Art" value={technique.style} />
            <InfoItem label="Category" value={technique.category} />
            <InfoItem label="Difficulty" value={`${getDifficultyText(technique.difficulty_level)} (${technique.difficulty_level}/10)`} />
        </div>
    </div>
);

// Info Item Component
const InfoItem = ({ label, value }) => (
    <div>
        <span className="text-sm font-medium text-gray-500">{label}:</span>
        <div className="text-sm text-gray-900">{value}</div>
    </div>
);

// Progress Tracker Component
const ProgressTracker = () => {
    const [masteryLevel, setMasteryLevel] = useState(5);

    return (
        <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Award className="h-5 w-5 mr-2 text-blue-600" />
                Your Progress
            </h3>

            <div className="space-y-4">
                <div>
                    <label className="text-sm font-medium text-gray-500 block mb-2">
                        Mastery Level: {masteryLevel}/10
                    </label>
                    <input
                        type="range"
                        min="1"
                        max="10"
                        value={masteryLevel}
                        onChange={(e) => setMasteryLevel(parseInt(e.target.value))}
                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                        <span>Learning</span>
                        <span>Mastered</span>
                    </div>
                </div>

                <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center">
                    <Plus className="h-4 w-4 mr-2" />
                    Mark as Practiced
                </button>
            </div>
        </div>
    );
};

// Bookmarks View Component
const BookmarksView = ({ onSelectTechnique }) => {
    const stats = {
        total: mockBookmarks.length,
        learning: mockBookmarks.filter(b => b.mastery_level <= 2).length,
        practicing: mockBookmarks.filter(b => b.mastery_level > 2 && b.mastery_level <= 4).length,
        improving: mockBookmarks.filter(b => b.mastery_level > 4 && b.mastery_level <= 7).length,
        mastered: mockBookmarks.filter(b => b.mastery_level > 7).length
    };

    return (
        <div>
            {/* Header */}
            <div className="bg-white shadow-sm border-b rounded-lg mb-8">
                <div className="px-6 py-6">
                    <h1 className="text-3xl font-bold text-gray-900 flex items-center">
                        <Star className="mr-3 h-8 w-8 text-yellow-500 fill-current" />
                        My Techniques
                    </h1>
                    <p className="mt-2 text-gray-600">Track your progress and practice</p>
                </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                <StatCard title="Total" value={stats.total} color="blue" icon={<BookOpen className="h-6 w-6" />} />
                <StatCard title="Learning" value={stats.learning} color="red" icon={<Target className="h-6 w-6" />} />
                <StatCard title="Practicing" value={stats.practicing} color="yellow" icon={<Clock className="h-6 w-6" />} />
                <StatCard title="Mastered" value={stats.mastered} color="green" icon={<Award className="h-6 w-6" />} />
            </div>

            {/* Bookmarked Techniques */}
            <div className="space-y-4">
                {mockBookmarks.map((bookmark) => (
                    <BookmarkCard
                        key={bookmark.id}
                        bookmark={bookmark}
                        onSelect={onSelectTechnique}
                    />
                ))}
            </div>
        </div>
    );
};

// Stat Card Component
const StatCard = ({ title, value, color, icon }) => {
    const colorClasses = {
        blue: 'border-blue-500 text-blue-500',
        red: 'border-red-500 text-red-500',
        yellow: 'border-yellow-500 text-yellow-500',
        green: 'border-green-500 text-green-500'
    };

    return (
        <div className={`bg-white rounded-lg shadow-sm p-4 border-l-4 ${colorClasses[color]}`}>
            <div className="flex items-center">
                <div className={colorClasses[color]}>{icon}</div>
                <div className="ml-3">
                    <div className="text-xl font-bold text-gray-900">{value}</div>
                    <div className="text-sm text-gray-500">{title}</div>
                </div>
            </div>
        </div>
    );
};

// Bookmark Card Component
const BookmarkCard = ({ bookmark, onSelect }) => (
    <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-start justify-between">
            <div className="flex-1">
                <div className="flex items-center gap-3 mb-3">
                    <h3
                        className="text-lg font-semibold text-gray-900 hover:text-blue-600 cursor-pointer"
                        onClick={() => onSelect(bookmark.technique)}
                    >
                        {bookmark.technique.name}
                    </h3>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getMasteryColor(bookmark.mastery_level)}`}>
                        {getMasteryText(bookmark.mastery_level)} ({bookmark.mastery_level}/10)
                    </span>
                </div>

                <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                    <span className="font-medium text-blue-600">{bookmark.technique.style}</span>
                    <div className="flex items-center gap-1">
                        <BarChart3 className="h-4 w-4" />
                        <span>{bookmark.practice_count} sessions</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        <span>Last: {new Date(bookmark.last_practiced).toLocaleDateString()}</span>
                    </div>
                </div>

                {bookmark.personal_notes && (
                    <div className="bg-gray-50 rounded p-3 mb-3">
                        <div className="text-sm font-medium text-gray-700 mb-1">Notes:</div>
                        <div className="text-sm text-gray-600">{bookmark.personal_notes}</div>
                    </div>
                )}

                <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${(bookmark.mastery_level / 10) * 100}%` }}
                    ></div>
                </div>
            </div>

            <button className="ml-4 p-2 text-red-600 hover:bg-red-50 rounded-lg">
                <Trash2 className="h-5 w-5" />
            </button>
        </div>
    </div>
);

// Main Demo Component
const TechniqueLibraryDemo = () => {
    const [currentView, setCurrentView] = useState('library');
    const [selectedTechnique, setSelectedTechnique] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedStyle, setSelectedStyle] = useState('');
    const [bookmarkedTechniques, setBookmarkedTechniques] = useState(new Set([1, 2]));

    // Filter techniques based on search
    const filteredTechniques = mockTechniques.filter(technique => {
        const matchesSearch = !searchQuery ||
            technique.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
            technique.style.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesStyle = !selectedStyle || technique.style === selectedStyle;
        return matchesSearch && matchesStyle;
    });

    const handleSelectTechnique = (technique) => {
        setSelectedTechnique(technique);
        setCurrentView('detail');
    };

    const isBookmarked = (techniqueId) => bookmarkedTechniques.has(techniqueId);

    const toggleBookmark = (techniqueId) => {
        const newBookmarks = new Set(bookmarkedTechniques);
        if (newBookmarks.has(techniqueId)) {
            newBookmarks.delete(techniqueId);
        } else {
            newBookmarks.add(techniqueId);
        }
        setBookmarkedTechniques(newBookmarks);
    };

    return (
        <div className="min-h-screen bg-gray-50">
            <DemoNavigation currentView={currentView} setCurrentView={setCurrentView} />

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Library View */}
                {currentView === 'library' && (
                    <div>
                        <div className="bg-white shadow-sm border-b rounded-lg mb-8">
                            <div className="px-6 py-6">
                                <h1 className="text-3xl font-bold text-gray-900 flex items-center">
                                    <BookOpen className="mr-3 h-8 w-8 text-blue-600" />
                                    Technique Library
                                </h1>
                                <p className="mt-2 text-gray-600">Discover martial arts techniques</p>
                            </div>
                        </div>

                        <SearchFilters
                            searchQuery={searchQuery}
                            setSearchQuery={setSearchQuery}
                            selectedStyle={selectedStyle}
                            setSelectedStyle={setSelectedStyle}
                        />

                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {filteredTechniques.map((technique) => (
                                <TechniqueCard
                                    key={technique.id}
                                    technique={technique}
                                    onSelect={handleSelectTechnique}
                                    isBookmarked={isBookmarked(technique.id)}
                                />
                            ))}
                        </div>
                    </div>
                )}

                {/* Detail View */}
                {currentView === 'detail' && selectedTechnique && (
                    <TechniqueDetail
                        technique={selectedTechnique}
                        onBack={() => setCurrentView('library')}
                        isBookmarked={isBookmarked(selectedTechnique.id)}
                        setIsBookmarked={() => toggleBookmark(selectedTechnique.id)}
                    />
                )}

                {/* Bookmarks View */}
                {currentView === 'bookmarks' && (
                    <BookmarksView onSelectTechnique={handleSelectTechnique} />
                )}
            </div>

            {/* Demo Info */}
            <div className="fixed bottom-4 right-4 bg-blue-600 text-white p-4 rounded-lg shadow-lg max-w-sm">
                <h4 className="font-semibold mb-2">🥋 Technique Library Demo</h4>
                <p className="text-sm opacity-90">
                    Browse techniques, view details, and track progress.
                    Current view: <strong>{currentView}</strong>
                </p>
            </div>
        </div>
    );
};

export default TechniqueLibraryDemo;