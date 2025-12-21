/**
 * Message Component
 * Displays individual chat messages from user or assistant
 */

import React from 'react';
import ErrorBoundary from './ErrorBoundary';

/**
 * Message Component
 * @param {Object} props - Component properties
 * @param {Object} props.message - The message object containing all details
 * @param {'user'|'assistant'} props.sender - Who sent the message
 * @param {string} props.content - The message content
 * @param {Array<string>} [props.sources] - Sources for assistant messages
 * @param {boolean} [props.showSources] - Whether to show source information
 * @param {number} [props.confidence] - Confidence score for assistant responses
 * @param {Array<string>} [props.followupQuestions] - Suggested follow-up questions
 */
export const Message = ({
  message,
  sender,
  content,
  sources = [],
  showSources = true,
  confidence,
  followupQuestions = []
}) => {
  // Determine if the message is from user or assistant
  const isUser = sender === 'user';

  // Render sources if they exist and should be shown
  const renderSources = () => {
    if (!showSources || !sources || !Array.isArray(sources) || sources.length === 0) {
      return null;
    }

    return (
      <div className="message-sources">
        Sources: {sources.map((source, index) => {
          if (typeof source !== 'string') return null;
          return (
            <span key={`${message.id || 'temp'}-source-${index}`} className="message-source">
              {source}
            </span>
          );
        }).filter(Boolean)}
      </div>
    );
  };

  // Render confidence indicator if provided
  const renderConfidence = () => {
    if (confidence === undefined || confidence === null || sender !== 'assistant') {
      return null;
    }

    // Ensure confidence is a number
    const confidenceValue = typeof confidence === 'number' ? confidence : parseFloat(confidence);
    if (isNaN(confidenceValue)) {
      return null;
    }

    let confidenceClass = 'confidence-indicator';
    let confidenceText = '';

    if (confidenceValue >= 0.8) {
      confidenceClass += ' confidence-high';
      confidenceText = `High confidence (${Math.round(confidenceValue * 100)}%)`;
    } else if (confidenceValue >= 0.5) {
      confidenceClass += ' confidence-medium';
      confidenceText = `Medium confidence (${Math.round(confidenceValue * 100)}%)`;
    } else {
      confidenceClass += ' confidence-low';
      confidenceText = `Low confidence (${Math.round(confidenceValue * 100)}%)`;
    }

    return (
      <div className={confidenceClass}>
        {confidenceText}
      </div>
    );
  };

  // Render retrieved context if provided
  const renderRetrievedContext = () => {
    if (!message?.retrievedContext || !Array.isArray(message.retrievedContext) || message.retrievedContext.length === 0) {
      return null;
    }

    return (
      <div className="message-retrieved-context">
        <strong>Reference context:</strong>
        <ul className="retrieved-context-list">
          {message.retrievedContext.map((context, index) => {
            if (typeof context !== 'string') return null;
            return (
              <li key={`${message.id || 'temp'}-context-${index}`} className="retrieved-context-item">
                {context}
              </li>
            );
          }).filter(Boolean)}
        </ul>
      </div>
    );
  };

  // Render follow-up questions if provided
  const renderFollowupQuestions = () => {
    if (!followupQuestions || !Array.isArray(followupQuestions) || followupQuestions.length === 0) {
      return null;
    }

    return (
      <div className="followup-questions">
        <strong>Related questions:</strong>
        {followupQuestions.map((question, index) => {
          if (typeof question !== 'string') return null;
          return (
            <span
              key={`${message.id || 'temp'}-followup-${index}`}
              className="followup-question"
              onClick={() => {
                // In a real implementation, this would trigger the question
                console.log(`Clicked follow-up question: ${question}`);
              }}
            >
              {question}
            </span>
          );
        }).filter(Boolean)}
      </div>
    );
  };

  // Combine message classes
  const messageClasses = [
    'message',
    isUser ? 'message-user' : 'message-assistant',
    message?.status === 'error' ? 'message-error' : ''
  ].filter(Boolean).join(' ');

  return (
    <div
      className={messageClasses}
      role="listitem"
      aria-setsize={-1} // Will be set by parent
      aria-posinset={-1} // Will be set by parent
    >
      <p className="message-content" aria-label={`${isUser ? 'User' : 'Assistant'} message: ${content}`}>
        {content}
      </p>

      {renderSources()}
      {renderConfidence()}
      {renderRetrievedContext()}
      {renderFollowupQuestions()}
    </div>
  );
};

export default Message;