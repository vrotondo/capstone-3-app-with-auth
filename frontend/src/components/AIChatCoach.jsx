import React, { useState, useEffect, useRef } from 'react';
import Button from './common/Button';
import LoadingSpinner from './common/LoadingSpinner';
import { useAuth } from '../context/AuthContext';
import aiService from '../services/aiService';

const AIChatCoach = ({ isOpen, onClose }) => {
    const { user } = useAuth();
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [suggestions, setSuggestions] = useState([]);
    const [showSuggestions, setShowSuggestions] = useState(true);
    const messagesEndRef = useRef(null);

    useEffect(() => {
        if (isOpen) {
            loadChatSuggestions();
            // Add welcome message if no messages
            if (messages.length === 0) {
                setMessages([{
                    role: 'coach',
                    content: `Hello ${user?.first_name || 'there'}! 👋 I'm your AI martial arts coach. I'm here to help you with training advice, technique guidance, motivation, and any questions about your martial arts journey. What would you like to work on today?`,
                    timestamp: new Date().toISOString()
                }]);
            }
        }
    }, [isOpen, user]);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const loadChatSuggestions = async () => {
        try {
            const response = await aiService.getChatSuggestions();
            if (response.success) {
                setSuggestions(response.suggestions);
            }
        } catch (error) {
            console.error('Failed to load chat suggestions:', error);
        }
    };

    const sendMessage = async (messageText = null) => {
        const message = messageText || inputMessage.trim();
        if (!message || isLoading) return;

        setIsLoading(true);
        setShowSuggestions(false);

        // Add user message
        const userMessage = {
            role: 'user',
            content: message,
            timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, userMessage]);
        setInputMessage('');

        try {
            // Send to AI coach
            const response = await aiService.sendChatMessage(message, messages);

            if (response.success) {
                // Add AI response
                const aiMessage = {
                    role: 'coach',
                    content: response.response,
                    timestamp: response.timestamp
                };
                setMessages(prev => [...prev, aiMessage]);
            } else {
                throw new Error(response.message || 'Failed to get response');
            }
        } catch (error) {
            console.error('Chat error:', error);
            // Add error message
            const errorMessage = {
                role: 'coach',
                content: "I'm sorry, I'm having trouble responding right now. Could you try asking your question again?",
                timestamp: new Date().toISOString(),
                isError: true
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    const useSuggestion = (suggestion) => {
        sendMessage(suggestion);
    };

    const clearChat = () => {
        setMessages([{
            role: 'coach',
            content: `Hello ${user?.first_name || 'there'}! 👋 I'm your AI martial arts coach. What would you like to work on today?`,
            timestamp: new Date().toISOString()
        }]);
        setShowSuggestions(true);
    };

    if (!isOpen) return null;

    return (
        <div className="ai-chat-overlay">
            <div className="ai-chat-container">
                <div className="ai-chat-header">
                    <div className="coach-info">
                        <div className="coach-avatar">🥋</div>
                        <div className="coach-details">
                            <h3>AI Martial Arts Coach</h3>
                            <p>Your personal training assistant</p>
                        </div>
                    </div>
                    <div className="chat-controls">
                        <button className="chat-clear-btn" onClick={clearChat} title="Clear Chat">
                            🗑️
                        </button>
                        <button className="chat-close-btn" onClick={onClose} title="Close Chat">
                            ✕
                        </button>
                    </div>
                </div>

                <div className="ai-chat-messages">
                    {messages.map((message, index) => (
                        <div key={index} className={`message ${message.role}-message`}>
                            <div className="message-avatar">
                                {message.role === 'coach' ? '🤖' : '👤'}
                            </div>
                            <div className="message-content">
                                <div className={`message-bubble ${message.isError ? 'error' : ''}`}>
                                    {message.content}
                                </div>
                                <div className="message-time">
                                    {new Date(message.timestamp).toLocaleTimeString([], {
                                        hour: '2-digit',
                                        minute: '2-digit'
                                    })}
                                </div>
                            </div>
                        </div>
                    ))}

                    {isLoading && (
                        <div className="message coach-message">
                            <div className="message-avatar">🤖</div>
                            <div className="message-content">
                                <div className="message-bubble loading">
                                    <div className="typing-indicator">
                                        <span></span>
                                        <span></span>
                                        <span></span>
                                    </div>
                                    <span>Coach is thinking...</span>
                                </div>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                {showSuggestions && suggestions.length > 0 && (
                    <div className="chat-suggestions">
                        <p>💡 Try asking about:</p>
                        <div className="suggestions-grid">
                            {suggestions.slice(0, 4).map((suggestion, index) => (
                                <button
                                    key={index}
                                    className="suggestion-btn"
                                    onClick={() => useSuggestion(suggestion)}
                                >
                                    {suggestion}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                <div className="ai-chat-input">
                    <div className="input-container">
                        <textarea
                            value={inputMessage}
                            onChange={(e) => setInputMessage(e.target.value)}
                            onKeyPress={handleKeyPress}
                            placeholder="Ask me about training, techniques, motivation, or anything martial arts related..."
                            disabled={isLoading}
                            rows="2"
                        />
                        <button
                            className="send-btn"
                            onClick={() => sendMessage()}
                            disabled={isLoading || !inputMessage.trim()}
                        >
                            {isLoading ? <LoadingSpinner size="small" /> : '📤'}
                        </button>
                    </div>
                    <div className="input-hint">
                        Press Enter to send • Shift+Enter for new line
                    </div>
                </div>
            </div>
        </div>
    );
};

// Chat Toggle Button Component
export const AIChatToggle = ({ onClick }) => {
    return (
        <button className="ai-chat-toggle" onClick={onClick} title="Chat with AI Coach">
            <span className="chat-icon">💬</span>
            <span className="chat-label">AI Coach</span>
        </button>
    );
};

export default AIChatCoach;