/**
 * UserInput Component
 * Handles user input for the chatbot with text area and send button
 */

import React, { useState, useRef, useEffect } from 'react';

/**
 * UserInput Component
 * @param {Object} props - Component properties
 * @param {Function} props.onSendMessage - Callback function to send message
 * @param {boolean} [props.isLoading] - Whether the chat is currently loading
 * @param {string} [props.selectedText] - Currently selected text from the page
 * @param {number} [props.maxQueryLength] - Maximum allowed query length
 */
export const UserInput = ({
  onSendMessage,
  isLoading = false,
  selectedText = '',
  maxQueryLength = 1000,
  textareaRef,
  disabled = false
}) => {
  const [inputValue, setInputValue] = useState('');
  const [isComposing, setIsComposing] = useState(false);

  // If no textareaRef is provided, create a local one
  const localTextareaRef = useRef(null);
  const effectiveTextareaRef = textareaRef || localTextareaRef;

  // Initialize with selected text if available
  useEffect(() => {
    if (selectedText && !inputValue) {
      setInputValue(selectedText);
    }
  }, [selectedText, inputValue]);

  // Handle text input changes
  const handleInputChange = (e) => {
    const value = e.target.value;
    if (value.length <= maxQueryLength) {
      setInputValue(value);
    }
  };

  // Handle sending the message
  const handleSend = () => {
    if (inputValue.trim() && !isLoading) {
      onSendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  // Handle key down events for sending with Enter
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!isComposing) {
        handleSend();
      }
    }
  };

  // Handle composition events for IME input
  const handleCompositionStart = () => {
    setIsComposing(true);
  };

  const handleCompositionEnd = () => {
    setIsComposing(false);
  };

  // Handle input focus
  const handleFocus = () => {
    if (effectiveTextareaRef.current) {
      // Move cursor to end of text
      const length = effectiveTextareaRef.current.value.length;
      effectiveTextareaRef.current.setSelectionRange(length, length);
    }
  };

  // Calculate remaining characters
  const remainingChars = maxQueryLength - inputValue.length;

  return (
    <div className="chat-input-area" role="form" aria-label="Chat input area">
      <div className="input-container">
        {selectedText && (
          <div className="selected-text-preview" role="region" aria-label="Selected text preview">
            <small className="selected-text-label">Selected text:</small>
            <div className="selected-text-content" aria-label={`Selected text: ${selectedText}`}>
              "{selectedText.length > 100 ? selectedText.substring(0, 100) + '...' : selectedText}"
            </div>
          </div>
        )}

        <textarea
          ref={effectiveTextareaRef}
          className="chat-input"
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onCompositionStart={handleCompositionStart}
          onCompositionEnd={handleCompositionEnd}
          onFocus={handleFocus}
          placeholder={selectedText
            ? "Ask about the selected text..."
            : "Ask a question about the book content..."}
          disabled={isLoading || disabled}
          rows={2}
          maxLength={maxQueryLength}
          aria-label="Type your message"
          aria-describedby="input-footer"
          id="chat-input"
        />

        <div className="input-footer" id="input-footer">
          <span
            className={`char-count ${remainingChars < 50 ? 'char-count-warning' : ''}`}
            aria-label={`Characters remaining: ${remainingChars} of ${maxQueryLength}`}
          >
            {remainingChars}/{maxQueryLength}
          </span>
        </div>
      </div>

      <button
        className="chat-send-button"
        onClick={handleSend}
        disabled={isLoading || !inputValue.trim() || disabled}
        aria-label="Send message"
        aria-describedby="chat-input"
      >
        <svg
          className="chat-send-icon"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          aria-hidden="true"
        >
          <path d="M22 2L11 13M22 2L15 22L11 13M11 13L2 9L22 2" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>
    </div>
  );
};

export default UserInput;