import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import Button from '../components/common/Button';

const TechniquesDebug = () => {
    const { user } = useAuth();
    const [debugInfo, setDebugInfo] = useState({});

    useEffect(() => {
        // Debug user authentication
        const token = localStorage.getItem('token');
        setDebugInfo({
            userFromContext: user,
            tokenInStorage: token,
            userTruthy: !!user,
            userType: typeof user,
            userStringified: JSON.stringify(user, null, 2)
        });
    }, [user]);

    return (
        <div style={{ padding: '2rem', fontFamily: 'monospace' }}>
            <h1>Techniques Debug Page</h1>

            {/* Debug Info */}
            <div style={{
                background: '#f0f0f0',
                padding: '1rem',
                marginBottom: '2rem',
                border: '1px solid #ccc',
                borderRadius: '4px'
            }}>
                <h3>🔧 Debug Information:</h3>
                <pre>{JSON.stringify(debugInfo, null, 2)}</pre>

                <div style={{ marginTop: '1rem' }}>
                    <strong>Auth Status:</strong> {user ? '✅ Logged In' : '❌ Not Logged In'}
                </div>

                <div>
                    <strong>Should Show Import Button:</strong> {user ? '✅ YES' : '❌ NO'}
                </div>
            </div>

            {/* Header with Import Button */}
            <div style={{
                border: '2px solid red',
                padding: '1rem',
                marginBottom: '2rem',
                background: '#fffaaa'
            }}>
                <h2>Header Section (where import button should be)</h2>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                        <h1>Technique Library</h1>
                        <p>Discover and manage your martial arts techniques</p>
                    </div>

                    {/* This is where the import button should appear */}
                    <div style={{ border: '2px dashed blue', padding: '10px' }}>
                        {user ? (
                            <Button
                                variant="primary"
                                onClick={() => alert('Import button clicked!')}
                                style={{ background: 'green', color: 'white' }}
                            >
                                🚀 IMPORT FROM BLACKBELTWIKI 🚀
                            </Button>
                        ) : (
                            <div style={{ color: 'red', fontWeight: 'bold' }}>
                                NO USER - NO BUTTON
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Test some simple API calls */}
            <div style={{ border: '1px solid #ccc', padding: '1rem' }}>
                <h3>Quick API Test</h3>
                <Button
                    onClick={async () => {
                        try {
                            const response = await fetch('http://localhost:8000/api/techniques/test');
                            const data = await response.json();
                            alert(`API Test Result: ${JSON.stringify(data)}`);
                        } catch (error) {
                            alert(`API Test Failed: ${error.message}`);
                        }
                    }}
                >
                    Test API Connection
                </Button>
            </div>
        </div>
    );
};

export default TechniquesDebug;