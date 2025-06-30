import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
    Menu, X, Home, Calendar, BarChart3, User, LogOut,
    BookOpen, Star, Target, Dumbbell, Activity
} from 'lucide-react';

import { useAuth } from '../context/AuthContext';

const Navigation = () => {
    const { user, logout } = useAuth();
    const [isOpen, setIsOpen] = useState(false);
    const location = useLocation();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/');
        setIsOpen(false);
    };

    const closeMenu = () => setIsOpen(false);

    const isActive = (path) => {
        if (path === '/' && location.pathname === '/') return true;
        if (path !== '/' && location.pathname.startsWith(path)) return true;
        return false;
    };

    const navigationItems = [
        {
            name: 'Dashboard',
            href: '/',
            icon: Home,
            description: 'Overview and recent activity'
        },
        {
            name: 'Training Sessions',
            href: '/training',
            icon: Calendar,
            description: 'Record your training sessions'
        },
        {
            name: 'Techniques',
            href: '/techniques',
            icon: BookOpen,
            description: 'Browse martial arts techniques'
        },
        {
            name: 'Exercises',
            href: '/exercises',
            icon: Dumbbell,
            description: 'Browse workout exercises'
        }
    ];

    const userMenuItems = user ? [
        {
            name: 'My Techniques',
            href: '/my-techniques',
            icon: Star,
            description: 'Your bookmarked techniques'
        },
        {
            name: 'Training Goals',
            href: '/goals',
            icon: Target,
            description: 'Set and track your goals'
        },
        {
            name: 'Profile',
            href: '/profile',
            icon: User,
            description: 'Manage your account'
        }
    ] : [];

    return (
        <>
            {/* Desktop Navigation Only */}
            <nav className="hidden md:block bg-white shadow-lg border-b border-gray-200 sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16">
                        {/* Logo and Brand */}
                        <div className="flex items-center">
                            <Link to="/" className="flex items-center space-x-2 hover:opacity-80 transition-opacity">
                                <Dumbbell className="h-8 w-8 text-blue-600" />
                                <span className="text-xl font-bold text-gray-900">DojoTracker</span>
                            </Link>
                        </div>

                        {/* Desktop Navigation */}
                        <div className="flex items-center space-x-1">
                            {navigationItems.map((item) => (
                                <Link
                                    key={item.name}
                                    to={item.href}
                                    className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${isActive(item.href)
                                            ? 'text-blue-600 bg-blue-50 border-b-2 border-blue-600 shadow-sm'
                                            : 'text-gray-700 hover:text-blue-600 hover:bg-blue-50 hover:shadow-sm'
                                        }`}
                                >
                                    <item.icon className="h-4 w-4" />
                                    <span>{item.name}</span>
                                </Link>
                            ))}
                        </div>

                        {/* User Menu */}
                        <div className="flex items-center space-x-3">
                            {user ? (
                                <div className="flex items-center space-x-3">
                                    {/* Quick User Menu Items */}
                                    {userMenuItems.slice(0, 2).map((item) => (
                                        <Link
                                            key={item.name}
                                            to={item.href}
                                            className={`flex items-center space-x-1 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${isActive(item.href)
                                                    ? 'text-blue-600 bg-blue-50'
                                                    : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50'
                                                }`}
                                            title={item.description}
                                        >
                                            <item.icon className="h-4 w-4" />
                                        </Link>
                                    ))}

                                    {/* User Profile Display */}
                                    <Link
                                        to="/profile"
                                        className="flex items-center space-x-3 px-3 py-2 rounded-lg bg-gradient-to-r from-blue-50 to-indigo-50 hover:from-blue-100 hover:to-indigo-100 transition-all duration-200"
                                    >
                                        <div className="flex items-center justify-center w-8 h-8 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-full text-sm font-medium">
                                            {user.first_name?.[0]?.toUpperCase() || 'U'}
                                        </div>
                                        <div className="text-sm">
                                            <div className="font-medium text-gray-900">
                                                {user.first_name} {user.last_name}
                                            </div>
                                            <div className="text-gray-500 text-xs">{user.primary_style || 'Martial Artist'}</div>
                                        </div>
                                    </Link>

                                    <button
                                        onClick={handleLogout}
                                        className="flex items-center space-x-1 px-3 py-2 rounded-lg text-sm font-medium text-red-600 hover:text-red-700 hover:bg-red-50 transition-all duration-200"
                                        title="Logout"
                                    >
                                        <LogOut className="h-4 w-4" />
                                        <span>Logout</span>
                                    </button>
                                </div>
                            ) : (
                                <div className="flex items-center space-x-3">
                                    <Link
                                        to="/login"
                                        className="text-gray-700 hover:text-blue-600 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                                    >
                                        Login
                                    </Link>
                                    <Link
                                        to="/register"
                                        className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 shadow-sm hover:shadow-md"
                                    >
                                        Sign Up
                                    </Link>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </nav>

            {/* Mobile Navigation - Completely Redesigned */}
            <nav className="md:hidden bg-white shadow-lg border-b border-gray-200 sticky top-0 z-50">
                <div className="flex items-center justify-between px-4 py-3">
                    {/* Mobile Logo */}
                    <Link to="/" className="flex items-center space-x-2" onClick={closeMenu}>
                        <Dumbbell className="h-7 w-7 text-blue-600" />
                        <span className="text-lg font-bold text-gray-900">DojoTracker</span>
                    </Link>

                    {/* Mobile Menu Button */}
                    <button
                        onClick={() => setIsOpen(!isOpen)}
                        className="p-2 rounded-lg text-gray-600 hover:text-blue-600 hover:bg-blue-50 transition-all duration-200"
                        aria-label="Toggle mobile menu"
                    >
                        {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
                    </button>
                </div>

                {/* Mobile Dropdown - Centered and Streamlined */}
                {isOpen && (
                    <div className="absolute top-full left-0 right-0 bg-white shadow-xl border-t border-gray-100 z-40">
                        <div className="max-w-sm mx-auto py-6 px-6 text-center">
                            {/* Navigation Section - Centered and Clean */}
                            <div className="space-y-2 mb-6">
                                {navigationItems.map((item) => (
                                    <Link
                                        key={item.name}
                                        to={item.href}
                                        onClick={closeMenu}
                                        className={`flex flex-col items-center justify-center px-4 py-4 rounded-xl text-base font-medium transition-all duration-200 ${isActive(item.href)
                                                ? 'text-blue-600 bg-blue-50 shadow-sm border border-blue-100'
                                                : 'text-gray-700 hover:text-blue-600 hover:bg-blue-50'
                                            }`}
                                    >
                                        <div className={`p-3 rounded-xl mb-2 ${isActive(item.href)
                                                ? 'bg-blue-100 text-blue-600'
                                                : 'bg-gray-100 text-gray-600'
                                            }`}>
                                            <item.icon className="h-6 w-6" />
                                        </div>
                                        <div className="font-semibold">{item.name}</div>
                                    </Link>
                                ))}
                            </div>

                            {user && (
                                <>
                                    {/* User Section - No Avatar, Just Menu Items */}
                                    <div className="border-t border-gray-100 pt-6 mb-4">
                                        {/* User Menu Items - Centered and Clean */}
                                        <div className="space-y-2 mb-4">
                                            {userMenuItems.map((item) => (
                                                <Link
                                                    key={item.name}
                                                    to={item.href}
                                                    onClick={closeMenu}
                                                    className={`flex flex-col items-center justify-center px-4 py-4 rounded-xl text-base font-medium transition-all duration-200 ${isActive(item.href)
                                                            ? 'text-blue-600 bg-blue-50 shadow-sm border border-blue-100'
                                                            : 'text-gray-700 hover:text-blue-600 hover:bg-blue-50'
                                                        }`}
                                                >
                                                    <div className={`p-3 rounded-xl mb-2 ${isActive(item.href)
                                                            ? 'bg-blue-100 text-blue-600'
                                                            : 'bg-gray-100 text-gray-600'
                                                        }`}>
                                                        <item.icon className="h-5 w-5" />
                                                    </div>
                                                    <div className="font-semibold">{item.name}</div>
                                                </Link>
                                            ))}
                                        </div>

                                        {/* Logout Button - Centered and Clean */}
                                        <button
                                            onClick={handleLogout}
                                            className="flex flex-col items-center justify-center w-full px-4 py-4 rounded-xl text-base font-medium text-red-600 hover:text-red-700 hover:bg-red-50 transition-all duration-200"
                                        >
                                            <div className="p-3 rounded-xl bg-red-100 text-red-600 mb-2">
                                                <LogOut className="h-5 w-5" />
                                            </div>
                                            <span className="font-semibold">Logout</span>
                                        </button>
                                    </div>
                                </>
                            )}

                            {/* Login/Register for non-authenticated users */}
                            {!user && (
                                <div className="border-t border-gray-100 pt-6 space-y-3">
                                    <Link
                                        to="/login"
                                        onClick={closeMenu}
                                        className="block w-full px-6 py-4 rounded-xl text-center text-base font-semibold text-gray-700 hover:text-blue-600 hover:bg-blue-50 transition-all duration-200"
                                    >
                                        Login
                                    </Link>
                                    <Link
                                        to="/register"
                                        onClick={closeMenu}
                                        className="block w-full px-6 py-4 rounded-xl text-center text-base font-semibold bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 shadow-lg"
                                    >
                                        Sign Up
                                    </Link>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </nav>

            {/* Overlay for mobile menu */}
            {isOpen && (
                <div
                    className="md:hidden fixed inset-0 bg-black bg-opacity-25 z-30"
                    onClick={closeMenu}
                    style={{ top: '70px' }}
                />
            )}
        </>
    );
};

export default Navigation;