// frontend/src/services/api.js - Alternative port configuration
import axios from 'axios';

// Try different ports if 5000 doesn't work
const POSSIBLE_PORTS = [5000, 8000, 5001, 3001];
const BASE_URL = `http://localhost:${POSSIBLE_PORTS[0]}/api`;

// Create axios instance with base configuration
const api = axios.create({
    baseURL: BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 5000,  // 5 second timeout
});

// Request interceptor to add auth token and log requests
api.interceptors.request.use(
    (config) => {
        console.log(`Making ${config.method?.toUpperCase()} request to: ${config.url}`);
        console.log('Full URL:', `${config.baseURL}${config.url}`);
        console.log('Request data:', config.data);

        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        console.error('Request error:', error);
        return Promise.reject(error);
    }
);

// Response interceptor to handle errors and log responses
api.interceptors.response.use(
    (response) => {
        console.log(`Response from ${response.config.url}:`, response.data);
        return response;
    },
    (error) => {
        console.error('Response error:', error);
        console.error('Error details:', {
            status: error.response?.status,
            statusText: error.response?.statusText,
            data: error.response?.data,
            url: error.config?.url,
            method: error.config?.method,
            baseURL: error.config?.baseURL
        });

        // Specific handling for connection errors
        if (error.code === 'ECONNREFUSED' || error.message === 'Network Error') {
            console.error('🚨 Backend server is not running or not accessible');
            console.error('👉 Make sure your Flask server is running on the correct port');
        }

        if (error.response?.status === 401) {
            // Token expired or invalid
            console.log('Unauthorized - clearing auth data');
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export default api;