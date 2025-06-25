import React from 'react';
import { NavLink } from 'react-router-dom';

const Navigation = () => {
    const navItems = [
        { path: '/dashboard', label: 'Dashboard', icon: '📊' },
        { path: '/training', label: 'Training Sessions', icon: '🥋' },
        { path: '/techniques', label: 'Techniques', icon: '📚' },
    ];

    return (
        <nav className="main-navigation">
            <div className="container">
                <ul className="nav-list">
                    {navItems.map((item) => (
                        <li key={item.path} className="nav-item">
                            <NavLink
                                to={item.path}
                                className={({ isActive }) =>
                                    isActive ? 'nav-link active' : 'nav-link'
                                }
                            >
                                <span className="nav-icon">{item.icon}</span>
                                <span className="nav-label">{item.label}</span>
                            </NavLink>
                        </li>
                    ))}
                </ul>
            </div>
        </nav>
    );
};

export default Navigation;