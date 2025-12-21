/**
 * ChatHistory Component
 * Displays the conversation history between user and assistant
 */

import React from 'react';
import { Message } from './Message';
import ErrorBoundary from './ErrorBoundary';

/**
 * ChatHistory Component
 * @param {Object} props - Component properties
 * @param {Array} props.messages - Array of chat messages to display
 * @param {boolean} [props.isLoading] - Whether the chat is currently loading
 * @param {boolean} [props.showSources] - Whether to show source information
 */
export const ChatHistory = ({ messages = [], isLoading = false, showSources = true }) => {
  return (
    <ErrorBoundary>
      <div
        className="chat-history"
        id="chat-history"
        role="log"
        aria-label="Chat history"
        aria-live="polite"
        aria-relevant="additions"
      >
        {messages.length === 0 && !isLoading && (
          <div className="message message-assistant" role="status" aria-live="polite">
            <p className="message-content">Hello! I'm your AI assistant for the AI-Driven Robotics Textbook. Ask me anything about the content you're reading!</p>
          </div>
        )}

        {messages.map((message, index) => (
          <ErrorBoundary key={`msg-boundary-${message.id || `msg-${index}`}`}>
            <Message
              key={message.id || `msg-${index}`}
              message={message}
              sender={message.sender}
              content={message.content}
              sources={message.sources}
              showSources={showSources}
              confidence={message.confidence}
              followupQuestions={message.followupQuestions}
              aria-posinset={index + 1}
              aria-setsize={messages.length}
            />
          </ErrorBoundary>
        ))}

        {isLoading && (
          <div className="message message-assistant message-loading" role="status" aria-live="polite">
            <div className="loading-dots" aria-label="Loading">
              <div className="loading-dot" aria-hidden="true"></div>
              <div className="loading-dot" aria-hidden="true"></div>
              <div className="loading-dot" aria-hidden="true"></div>
            </div>
          </div>
        )}
      </div>
    </ErrorBoundary>
  );
};

export default ChatHistory;