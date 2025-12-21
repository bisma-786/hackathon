/**
 * Main Chatbot Component
 * Provides a chat interface for users to ask questions about book content
 */

import React, { useState, useEffect, useRef } from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';
import { ChatHistory } from './ChatHistory';
import { UserInput } from './UserInput';
import { ChatbotAPIService, createChatbotAPIService } from './chatbot-api';
import { ChatMessage, ChatSession, APIRequest, ChatbotConfig } from './data-model';
import { sanitizeAPIResponse, sanitizeUserInput } from './utils';
import { addTextSelectionListener, sanitizeSelectedText, validateSelectedText, isBrowser } from './text-selection';
import ErrorBoundary from './ErrorBoundary';
import './Chatbot.css';

/**
 * Main Chatbot Component
 * @param {Object} props - Component properties
 * @param {Object} [props.pageContext] - Context about the current page
 * @param {string} [props.pageContext.url] - Current page URL
 * @param {string} [props.pageContext.title] - Current page title
 * @param {Object} [props.config] - Configuration object
 * @param {string} [props.config.apiEndpoint] - Backend API endpoint
 * @param {number} [props.config.timeoutMs] - Request timeout in milliseconds
 * @param {number} [props.config.maxQueryLength] - Maximum query length
 * @param {Object} [props.options] - Additional options
 * @param {boolean} [props.options.showSources] - Whether to show source information
 * @param {boolean} [props.options.enableSelectedText] - Whether to capture selected text
 */
export const Chatbot = ({
  pageContext = {},
  config: configProps = {},
  options = {}
}) => {
  // Default configuration
  const defaultConfig = new ChatbotConfig({
    apiEndpoint: process.env.CHATBOT_API_ENDPOINT || 'http://localhost:8000',
    timeoutMs: 30000,
    maxQueryLength: 1000,
    showSources: true,
    enableSelectedText: true
  });

  // Merge default config with provided config
  const config = { ...defaultConfig.toObject(), ...configProps };
  const mergedOptions = {
    showSources: true,
    enableSelectedText: true,
    ...options
  };

  // Initialize API service
  const apiService = useRef(null);
  const textareaRef = useRef(null);
  const [session, setSession] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isVisible, setIsVisible] = useState(false);
  const [selectedText, setSelectedText] = useState('');

  // Initialize the component
  useEffect(() => {
    // Only run in browser environment
    if (typeof window === 'undefined' || typeof localStorage === 'undefined') {
      // Create a basic session for SSR
      const basicSession = new ChatSession({
        id: `session_${Date.now()}`,
        pageUrl: pageContext.url || '',
        selectedText: '',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      });
      setSession(basicSession);
      return;
    }

    // Create API service instance
    apiService.current = createChatbotAPIService(config);

    // Start connection monitoring
    apiService.current.startConnectionMonitoring(30000); // Check every 30 seconds

    // Try to restore session from localStorage
    const savedSession = localStorage.getItem('chatbot-session');
    let restoredSession = null;

    if (savedSession) {
      try {
        const sessionData = JSON.parse(savedSession);
        // Validate that it's a proper session object
        if (sessionData && sessionData.id && sessionData.messages !== undefined) {
          restoredSession = new ChatSession(sessionData);
        }
      } catch (error) {
        console.warn('Failed to parse saved session, creating new one:', error);
      }
    }

    // Create a new chat session if no valid session was found
    const newSession = restoredSession || new ChatSession({
      id: `session_${Date.now()}`,
      pageUrl: pageContext.url || window.location.href,
      selectedText: '',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    });

    setSession(newSession);

    // Cleanup function
    return () => {
      if (apiService.current) {
        apiService.current.stopConnectionMonitoring();
      }
    };
  }, []);

  // Handle text selection if enabled
  useEffect(() => {
    if (!mergedOptions.enableSelectedText || typeof window === 'undefined' || typeof document === 'undefined') return;

    const cleanup = addTextSelectionListener((selectedText) => {
      // Sanitize and validate the selected text
      const sanitizedText = sanitizeSelectedText(selectedText);
      const validation = validateSelectedText(sanitizedText, {
        maxLength: 500, // Limit selected text to 500 characters
        maxLengthMessage: 'Selected text is too long. Please select a shorter portion.'
      });

      if (validation.isValid) {
        setSelectedText(sanitizedText);
      }
    });

    return cleanup;
  }, [mergedOptions.enableSelectedText]);

  // Handle keyboard navigation and shortcuts
  useEffect(() => {
    if (typeof document === 'undefined') return;

    const handleKeyDown = (e) => {
      // Focus chat input when pressing Ctrl/Cmd + K
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        if (isVisible && textareaRef.current) {
          textareaRef.current.focus();
        }
      }

      // Close chatbot when pressing Escape (if visible)
      if (e.key === 'Escape' && isVisible) {
        closeChatbot();
      }

      // Toggle chatbot visibility when pressing Ctrl/Cmd + Shift + K
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'K') {
        e.preventDefault();
        toggleVisibility();
      }
    };

    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isVisible]);

  /**
   * Handle sending a query to the backend
   * @param {string} query - User query
   */
  const handleSendQuery = async (query) => {
    if (!apiService.current || !session) {
      setError('Chatbot not initialized properly');
      return;
    }

    // Sanitize the user input
    const sanitizedQuery = sanitizeUserInput(query);

    if (!sanitizedQuery.trim()) {
      setError('Query cannot be empty');
      return;
    }

    if (sanitizedQuery.length > config.maxQueryLength) {
      setError(`Query exceeds maximum length of ${config.maxQueryLength} characters`);
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      // Create user message
      const userMessage = new ChatMessage({
        id: `msg_user_${Date.now()}`,
        content: sanitizedQuery,
        sender: 'user',
        timestamp: new Date().toISOString(),
        status: 'sent'
      });

      // Update session with user message
      const updatedSession = new ChatSession({
        ...session.toObject(),
        messages: [...session.messages, userMessage],
        updatedAt: new Date().toISOString()
      });
      setSession(updatedSession);

      // Persist session to localStorage (only in browser)
      if (typeof localStorage !== 'undefined') {
        try {
          localStorage.setItem('chatbot-session', JSON.stringify(updatedSession.toObject()));
        } catch (error) {
          console.warn('Failed to save session to localStorage:', error);
        }
      }

      // Validate and sanitize selected text before including in request
      let processedSelectedText = '';
      if (selectedText) {
        const sanitizedText = sanitizeSelectedText(selectedText);
        const validation = validateSelectedText(sanitizedText, {
          maxLength: 1000, // Allow up to 1000 chars in API request
          maxLengthMessage: 'Selected text is too long'
        });

        if (validation.isValid) {
          processedSelectedText = sanitizedText;
        }
      }

      // Create API request
      const apiRequest = new APIRequest({
        query: sanitizedQuery,
        selectedText: processedSelectedText,
        pageContext: {
          url: pageContext.url || window.location.href,
          title: pageContext.title || document.title
        },
        timestamp: new Date().toISOString()
      });

      // Send query to backend
      const response = await apiService.current.sendQueryWithValidation(apiRequest);

      // Sanitize the API response
      const sanitizedResponse = sanitizeAPIResponse(response);

      // Check if the response indicates no relevant content
      const noRelevantContent = sanitizedResponse.answer.toLowerCase().includes('no relevant content') ||
                               sanitizedResponse.answer.toLowerCase().includes('no information found') ||
                               sanitizedResponse.answer.toLowerCase().includes('not mentioned in the provided context') ||
                               sanitizedResponse.answer.toLowerCase().includes('no context provided');

      // Create assistant message
      const assistantMessage = new ChatMessage({
        id: `msg_assistant_${Date.now()}`,
        content: sanitizedResponse.answer,
        sender: 'assistant',
        timestamp: new Date().toISOString(),
        sources: sanitizedResponse.sources,
        retrievedContext: sanitizedResponse.retrievedContext,
        followupQuestions: sanitizedResponse.followupQuestions,
        confidence: sanitizedResponse.confidence,
        status: noRelevantContent ? 'no_content' : 'sent'
      });

      // Update session with assistant message
      const finalSession = new ChatSession({
        ...updatedSession.toObject(),
        messages: [...updatedSession.messages, assistantMessage],
        updatedAt: new Date().toISOString()
      });
      setSession(finalSession);

      // Persist session to localStorage (only in browser)
      if (typeof localStorage !== 'undefined') {
        try {
          localStorage.setItem('chatbot-session', JSON.stringify(finalSession.toObject()));
        } catch (error) {
          console.warn('Failed to save session to localStorage:', error);
        }
      }

      // Clear selected text after successful query
      if (selectedText) {
        setSelectedText('');
      }
    } catch (err) {
      setError(`Error: ${err.message}`);
      console.error('Error sending query:', err);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Toggle chatbot visibility
   */
  const toggleVisibility = () => {
    setIsVisible(!isVisible);
  };

  /**
   * Close the chatbot
   */
  const closeChatbot = () => {
    setIsVisible(false);
  };

  // If not visible, show only the toggle button
  if (!isVisible) {
    return (
      <button
        className="chatbot-toggle"
        onClick={toggleVisibility}
        aria-label="Open chatbot"
        aria-expanded={false}
        aria-controls="chatbot-container"
      >
        <svg
          className="chatbot-toggle-icon"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          aria-hidden="true"
        >
          <path d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H7L3 21V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V15Z" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>
    );
  }

  // If session is not ready, show loading
  if (!session) {
    return (
      <div className="chatbot-container">
        <div className="chatbot-header">
          <h3>AI Assistant</h3>
          <button className="chatbot-close-button" onClick={closeChatbot} aria-label="Close chatbot">
            ×
          </button>
        </div>
        <div className="chat-history">
          <div className="message message-assistant">
            <p className="message-content">Initializing chatbot...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div
        className="chatbot-container"
        id="chatbot-container"
        role="complementary"
        aria-label="AI Assistant Chatbot"
        tabIndex={-1}
      >
        <div className="chatbot-header" role="banner">
          <h3 id="chatbot-title">AI Assistant</h3>
          <button
            className="chatbot-close-button"
            onClick={closeChatbot}
            aria-label="Close chatbot"
            aria-describedby="chatbot-title"
            aria-expanded={true}
          >
            ×
          </button>
        </div>

        <ChatHistory
          messages={session.messages}
          isLoading={isLoading}
          showSources={mergedOptions.showSources}
          aria-live="polite"
          aria-relevant="additions text"
        />

        {/* Show offline message when service is unavailable */}
        {apiService.current && apiService.current.isOnline === false && (
          <div className="message message-offline" role="status" aria-live="polite">
            <p className="message-content">
              The AI service is currently unavailable. Please check your connection and try again later.
            </p>
          </div>
        )}

        <UserInput
          onSendMessage={handleSendQuery}
          isLoading={isLoading}
          selectedText={selectedText}
          maxQueryLength={config.maxQueryLength}
          aria-controls="chat-history"
          textareaRef={textareaRef}
          disabled={apiService.current?.isOnline === false}
        />

        {error && (
          <div className="message message-error" role="alert" aria-live="assertive">
            <p className="message-content">{error}</p>
          </div>
        )}

        {/* Network status indicator */}
        {apiService.current && apiService.current.isOnline !== undefined && (
          <div
            className={`network-status ${apiService.current.isOnline ? 'network-status-online' : 'network-status-offline'}`}
            aria-label={`Connection status: ${apiService.current.isOnline ? 'connected' : 'disconnected'}`}
            aria-live="polite"
          >
            <div className="network-status-indicator" aria-hidden="true"></div>
            <span>{apiService.current.isOnline ? 'Connected' : 'Offline'}</span>
          </div>
        )}
      </div>
    </ErrorBoundary>
  );
};

export default Chatbot;