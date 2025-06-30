import React from 'react';
import Header from './Header';
import Navigation from '../Navigation';
import Footer from './Footer';
import '../../styles/components/layout.css';

const Layout = ({ children, showNavigation = true }) => {
    return (
        <div className="layout">
            <Header />
            {showNavigation && <Navigation />}
            <main className="main-content">
                <div className="container">
                    {children}
                </div>
            </main>
            <Footer />
        </div>
    );
};

export default Layout;