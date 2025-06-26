import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
    Menu, X, Home, Calendar, BarChart3, User, LogOut,
    BookOpen, Star, Target, Dumbbell
} from 'lucide-react';

import { useAuth } from '../context/AuthContext';

const Navigation = () => {
    const { user, logout } = useAuth();
    const [isOpen, setIsOpen] = useState(false);
    const location = useLocation();
    const navigate = useNavigate();

    const handleLogout = () => {
        onLogout();
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
            name: 'Log Training',
            href: '/log-training',
            icon: Calendar,
            description: 'Record your training sessions'
        },
        {
            name: 'Analytics',
            href: '/analytics',
            icon: BarChart3,
            description: 'View your progress and stats'
        },
        {
            name: 'Technique Library',
            href: '/techniques',
            icon: BookOpen,
            description: 'Browse martial arts techniques'
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
        <nav className="bg-white shadow-lg border-b border-gray-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">
                    {/* Logo and Brand */}
                    <div className="flex items-center">
                        <Link to="/" className="flex items-center space-x-2" onClick={closeMenu}>
                            <Dumbbell className="h-8 w-8 text-blue-600" />
                            <span className="text-xl font-bold text-gray-900">DojoTracker</span>
                        </Link>
                    </div>

                    {/* Desktop Navigation */}
                    <div className="hidden md:flex items-center space-x-8">
                        {navigationItems.map((item) => (
                            <Link
                                key={item.name}
                                to={item.href}
                                className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${isActive(item.href)
                                    ? 'text-blue-600 bg-blue-50 border-b-2 border-blue-600'
                                    : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50'
                                    }`}
                            >
                                <item.icon className="h-4 w-4" />
                                <span>{item.name}</span>
                            </Link>
                        ))}
                    </div>

                    {/* User Menu */}
                    <div className="hidden md:flex items-center space-x-4">
                        {user ? (
                            <div className="flex items-center space-x-4">
                                {/* User Menu Items */}
                                {userMenuItems.map((item) => (
                                    <Link
                                        key={item.name}
                                        to={item.href}
                                        className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${isActive(item.href)
                                            ? 'text-blue-600 bg-blue-50'
                                            : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50'
                                            }`}
                                    >
                                        <item.icon className="h-4 w-4" />
                                        <span>{item.name}</span>
                                    </Link>
                                ))}

                                {/* User Profile Dropdown */}
                                <div className="relative">
                                    <div className="flex items-center space-x-3 px-3 py-2 rounded-md bg-gray-50">
                                        <div className="flex items-center justify-center w-8 h-8 bg-blue-600 text-white rounded-full text-sm font-medium">
                                            {user.first_name?.[0]?.toUpperCase() || 'U'}
                                        </div>
                                        <div className="text-sm">
                                            <div className="font-medium text-gray-900">
                                                {user.first_name} {user.last_name}
                                            </div>
                                            <div className="text-gray-500">{user.primary_style || 'Martial Artist'}</div>
                                        </div>
                                    </div>
                                </div>

                                <button
                                    onClick={handleLogout}
                                    className="flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium text-red-700 hover:text-red-900 hover:bg-red-50 transition-colors"
                                >
                                    <LogOut className="h-4 w-4" />
                                    <span>Logout</span>
                                </button>
                            </div>
                        ) : (
                            <div className="flex items-center space-x-4">
                                <Link
                                    to="/login"
                                    className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
                                >
                                    Login
                                </Link>
                                <Link
                                    to="/register"
                                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                                >
                                    Sign Up
                                </Link>
                            </div>
                        )}
                    </div>

                    {/* Mobile menu button */}
                    <div className="md:hidden flex items-center">
                        <button
                            onClick={() => setIsOpen(!isOpen)}
                            className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
                        >
                            {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile Navigation Menu */}
            {isOpen && (
                <div className="md:hidden">
                    <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-white border-t border-gray-200">
                        {/* Main Navigation */}
                        <div className="space-y-1">
                            {navigationItems.map((item) => (
                                <Link
                                    key={item.name}
                                    to={item.href}
                                    onClick={closeMenu}
                                    className={`flex items-center space-x-3 px-3 py-3 rounded-md text-base font-medium transition-colors ${isActive(item.href)
                                        ? 'text-blue-600 bg-blue-50 border-l-4 border-blue-600'
                                        : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50'
                                        }`}
                                >
                                    <item.icon className="h-5 w-5" />
                                    <div>
                                        <div>{item.name}</div>
                                        <div className="text-xs text-gray-500">{item.description}</div>
                                    </div>
                                </Link>
                            ))}
                        </div>

                        {user && (
                            <>
                                {/* Divider */}
                                <div className="border-t border-gray-200 my-3"></div>

                                {/* User Menu Items */}
                                <div className="space-y-1">
                                    {userMenuItems.map((item) => (
                                        <Link
                                            key={item.name}
                                            to={item.href}
                                            onClick={closeMenu}
                                            className={`flex items-center space-x-3 px-3 py-3 rounded-md text-base font-medium transition-colors ${isActive(item.href)
                                                ? 'text-blue-600 bg-blue-50 border-l-4 border-blue-600'
                                                : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50'
                                                }`}
                                        >
                                            <item.icon className="h-5 w-5" />
                                            <div>
                                                <div>{item.name}</div>
                                                <div className="text-xs text-gray-500">{item.description}</div>
                                            </div>
                                        </Link>
                                    ))}
                                </div>

                                {/* User Profile */}
                                <div className="border-t border-gray-200 pt-3 mt-3">
                                    <div className="flex items-center px-3 py-3">
                                        <div className="flex items-center justify-center w-10 h-10 bg-blue-600 text-white rounded-full text-lg font-medium">
                                            {user.first_name?.[0]?.toUpperCase() || 'U'}
                                        </div>
                                        <div className="ml-3">
                                            <div className="text-base font-medium text-gray-900">
                                                {user.first_name} {user.last_name}
                                            </div>
                                            <div className="text-sm text-gray-500">{user.email}</div>
                                            <div className="text-sm text-blue-600">{user.primary_style || 'Martial Artist'}</div>
                                        </div>
                                    </div>

                                    <button
                                        onClick={handleLogout}
                                        className="w-full flex items-center space-x-3 px-3 py-3 rounded-md text-base font-medium text-red-700 hover:text-red-900 hover:bg-red-50 transition-colors"
                                    >
                                        <LogOut className="h-5 w-5" />
                                        <span>Logout</span>
                                    </button>
                                </div>
                            </>
                        )}

                        {/* Login/Register for non-authenticated users */}
                        {!user && (
                            <div className="border-t border-gray-200 pt-3 mt-3 space-y-1">
                                <Link
                                    to="/login"
                                    onClick={closeMenu}
                                    className="block px-3 py-3 rounded-md text-base font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-50"
                                >
                                    Login
                                </Link>
                                <Link
                                    to="/register"
                                    onClick={closeMenu}
                                    className="block px-3 py-3 rounded-md text-base font-medium bg-blue-600 text-white hover:bg-blue-700"
                                >
                                    Sign Up
                                </Link>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </nav>
    );
};

export default Navigation;