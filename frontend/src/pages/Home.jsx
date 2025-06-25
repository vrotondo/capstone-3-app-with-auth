// src/pages/Home.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import Button from '../components/common/Button';
import '../styles/pages/home.css';

const Home = () => {
    return (
        <div className="home-page">
            <section className="hero-section">
                <h1>Track Your Martial Arts Journey</h1>
                <p>
                    DojoTracker helps martial artists log training sessions, track techniques,
                    and monitor their progress over time.
                </p>
                <div className="hero-actions">
                    <Link to="/register">
                        <Button variant="primary" size="lg">
                            Get Started Free
                        </Button>
                    </Link>
                    <Link to="/login">
                        <Button variant="outline" size="lg">
                            Sign In
                        </Button>
                    </Link>
                </div>
            </section>

            <section className="features-section">
                <div className="features-grid">
                    <div className="feature-card">
                        <div className="feature-icon">🥋</div>
                        <h3>Training Sessions</h3>
                        <p>Log your training sessions with detailed notes, duration, and intensity.</p>
                    </div>
                    <div className="feature-card">
                        <div className="feature-icon">📚</div>
                        <h3>Technique Library</h3>
                        <p>Build your personal technique library and track your mastery level.</p>
                    </div>
                    <div className="feature-card">
                        <div className="feature-icon">📊</div>
                        <h3>Progress Tracking</h3>
                        <p>Visualize your progress and see how you're improving over time.</p>
                    </div>
                </div>
            </section>
        </div>
    );
};

export default Home;