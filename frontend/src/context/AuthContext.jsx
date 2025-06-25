import React, { createContext, useContext, useReducer, useEffect } from 'react';
import authService from '../services/authService';

const AuthContext = createContext();

const initialState = {
    user: null,
    token: null,
    isLoading: true,
    isAuthenticated: false,
};

const authReducer = (state, action) => {
    switch (action.type) {
        case 'LOGIN_SUCCESS':
            return {
                ...state,
                user: action.payload.user,
                token: action.payload.token,
                isAuthenticated: true,
                isLoading: false,
            };
        case 'LOGOUT':
            return {
                ...state,
                user: null,
                token: null,
                isAuthenticated: false,
                isLoading: false,
            };
        case 'SET_LOADING':
            return {
                ...state,
                isLoading: action.payload,
            };
        case 'AUTH_ERROR':
            return {
                ...state,
                user: null,
                token: null,
                isAuthenticated: false,
                isLoading: false,
            };
        default:
            return state;
    }
};

export const AuthProvider = ({ children }) => {
    const [state, dispatch] = useReducer(authReducer, initialState);

    useEffect(() => {
        // Check if user is already logged in
        const token = localStorage.getItem('token');
        const user = localStorage.getItem('user');

        console.log('AuthContext initialization - token:', !!token, 'user:', !!user);

        if (token && user) {
            try {
                const parsedUser = JSON.parse(user);
                console.log('Restored user from localStorage:', parsedUser);
                dispatch({
                    type: 'LOGIN_SUCCESS',
                    payload: {
                        token,
                        user: parsedUser,
                    },
                });
            } catch (error) {
                console.error('Error parsing stored user data:', error);
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                dispatch({ type: 'SET_LOADING', payload: false });
            }
        } else {
            dispatch({ type: 'SET_LOADING', payload: false });
        }
    }, []);

    const login = async (email, password) => {
        try {
            console.log('AuthContext: Starting login process for:', email);
            dispatch({ type: 'SET_LOADING', payload: true });

            const response = await authService.login(email, password);
            console.log('AuthContext: Login response received:', response);

            // Store the token and user data
            localStorage.setItem('token', response.token);
            localStorage.setItem('user', JSON.stringify(response.user));

            dispatch({
                type: 'LOGIN_SUCCESS',
                payload: {
                    token: response.token,
                    user: response.user
                },
            });

            console.log('AuthContext: Login successful, user authenticated');
            return { success: true };
        } catch (error) {
            console.error('AuthContext: Login failed:', error);
            dispatch({ type: 'AUTH_ERROR' });

            // Extract error message
            let errorMessage = 'Login failed';
            if (error.response?.data?.message) {
                errorMessage = error.response.data.message;
            } else if (error.message) {
                errorMessage = error.message;
            }

            return {
                success: false,
                error: errorMessage
            };
        }
    };

    const register = async (userData) => {
        try {
            console.log('AuthContext: Starting registration process');
            dispatch({ type: 'SET_LOADING', payload: true });

            const response = await authService.register(userData);
            console.log('AuthContext: Registration response received:', response);

            // Store the token and user data
            localStorage.setItem('token', response.token);
            localStorage.setItem('user', JSON.stringify(response.user));

            dispatch({
                type: 'LOGIN_SUCCESS',
                payload: {
                    token: response.token,
                    user: response.user
                },
            });

            console.log('AuthContext: Registration successful, user authenticated');
            return { success: true };
        } catch (error) {
            console.error('AuthContext: Registration failed:', error);
            dispatch({ type: 'AUTH_ERROR' });

            // Extract error message
            let errorMessage = 'Registration failed';
            if (error.response?.data?.message) {
                errorMessage = error.response.data.message;
            } else if (error.message) {
                errorMessage = error.message;
            }

            return {
                success: false,
                error: errorMessage
            };
        }
    };

    const logout = () => {
        console.log('AuthContext: Logging out user');
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        dispatch({ type: 'LOGOUT' });
    };

    const value = {
        ...state,
        login,
        register,
        logout,
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};