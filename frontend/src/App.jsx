import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Layout from './components/layout/Layout';
import LoadingSpinner from './components/common/LoadingSpinner';

// Pages
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Training from './pages/Training';
import Techniques from './pages/Techniques';
import TechniqueLibrary from './pages/TechniqueLibrary'; // Add this import
import TechniqueDetail from './pages/TechniqueDetail'; // Add this import
import MyTechniques from './pages/MyTechniques'; // Add this import
import Profile from './pages/Profile';

// Styles
import './styles/global.css';
import './App.css';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

// Public Route Component (redirect to dashboard if authenticated)
const PublicRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return !isAuthenticated ? children : <Navigate to="/dashboard" replace />;
};

// Main App Content
const AppContent = () => {
  return (
    <Router>
      <div className="app">
        <Routes>
          {/* Public Routes */}
          <Route
            path="/"
            element={
              <Layout showNavigation={false}>
                <Home />
              </Layout>
            }
          />
          <Route
            path="/login"
            element={
              <PublicRoute>
                <Layout showNavigation={false}>
                  <Login />
                </Layout>
              </PublicRoute>
            }
          />
          <Route
            path="/register"
            element={
              <PublicRoute>
                <Layout showNavigation={false}>
                  <Register />
                </Layout>
              </PublicRoute>
            }
          />

          {/* Protected Routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Layout>
                  <Dashboard />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/training"
            element={
              <ProtectedRoute>
                <Layout>
                  <Training />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Technique Routes - These can be public */}
          <Route
            path="/techniques"
            element={
              <Layout>
                <TechniqueLibrary />
              </Layout>
            }
          />
          <Route
            path="/techniques/:id"
            element={
              <Layout>
                <TechniqueDetail />
              </Layout>
            }
          />

          {/* Protected Technique Routes */}
          <Route
            path="/my-techniques"
            element={
              <ProtectedRoute>
                <Layout>
                  <MyTechniques />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Layout>
                  <Profile />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Catch all route */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
};

// Main App Component
function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;