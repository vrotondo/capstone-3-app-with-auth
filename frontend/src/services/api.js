import axios from 'axios';

// Use port 8000 to avoid Windows port 5000 conflicts
const api = axios.create({
    baseURL: 'http://localhost:8000/api',
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 10000,
});

// Request interceptor
api.interceptors.request.use(
    (config) => {
        console.log(`🔄 Making ${config.method?.toUpperCase()} request to: ${config.url}`);
        console.log('📍 Full URL:', `${config.baseURL}${config.url}`);
        console.log('📦 Request data:', config.data);

        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        console.error('❌ Request error:', error);
        return Promise.reject(error);
    }
);

// Response interceptor
api.interceptors.response.use(
    (response) => {
        console.log(`✅ Response from ${response.config.url}:`, response.data);
        return response;
    },
    (error) => {
        console.error('❌ Response error:', error);

        if (error.code === 'ECONNREFUSED' || error.message === 'Network Error') {
            console.error('🚨 BACKEND NOT RUNNING!');
            console.error('💡 Start backend with: python app.py');
        }

        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = '/login';
        }

        return Promise.reject(error);
    }
);

export default api;