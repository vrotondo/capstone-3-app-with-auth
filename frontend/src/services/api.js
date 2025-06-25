import axios from 'axios';

// Use port 8000 to match your Flask backend
const api = axios.create({
    baseURL: 'http://localhost:8000/api',
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 10000,
});

// Request interceptor with detailed logging
api.interceptors.request.use(
    (config) => {
        console.log(`🔄 Making ${config.method?.toUpperCase()} request to: ${config.url}`);
        console.log('📍 Full URL:', `${config.baseURL}${config.url}`);
        console.log('📦 Request data:', config.data);

        const token = localStorage.getItem('token');
        console.log('🔑 Token from localStorage:', token ? `${token.substring(0, 20)}...` : 'No token found');

        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
            console.log('✅ Authorization header set:', config.headers.Authorization.substring(0, 30) + '...');
        } else {
            console.log('❌ No token available - request will be unauthenticated');
        }

        console.log('📋 Final headers:', config.headers);
        return config;
    },
    (error) => {
        console.error('❌ Request interceptor error:', error);
        return Promise.reject(error);
    }
);

// Response interceptor with detailed logging
api.interceptors.response.use(
    (response) => {
        console.log(`✅ Response from ${response.config.url}:`, response.data);
        return response;
    },
    (error) => {
        console.error('❌ Response error details:');
        console.error('Status:', error.response?.status);
        console.error('Data:', error.response?.data);
        console.error('Headers:', error.response?.headers);
        console.error('Config:', error.config);

        if (error.code === 'ECONNREFUSED' || error.message === 'Network Error') {
            console.error('🚨 BACKEND NOT RUNNING!');
            console.error('💡 Start backend with: cd backend && python app.py');
            console.error('💡 Backend should be running on http://localhost:8000');
        }

        if (error.response?.status === 401) {
            console.warn('🔒 Unauthorized - Token may be invalid or expired');
            console.warn('Token in localStorage:', localStorage.getItem('token') ? 'Present' : 'Missing');

            // Check if we're already on auth pages before redirecting
            if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/register')) {
                console.warn('🔄 Redirecting to login page');
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                window.location.href = '/login';
            }
        }

        return Promise.reject(error);
    }
);

export default api;