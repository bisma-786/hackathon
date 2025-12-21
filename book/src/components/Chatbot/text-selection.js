/**
 * Text Selection Utilities for the Chatbot component
 * Handles detection and capture of user-selected text
 */

/**
 * Check if running in browser environment
 * @returns {boolean} True if in browser, false otherwise
 */
export const isBrowser = () => {
  return typeof window !== 'undefined' && typeof document !== 'undefined';
};

/**
 * Get the currently selected text from the page
 * @returns {string} The selected text, or empty string if none
 */
export const getSelectedText = () => {
  if (isBrowser()) {
    return window.getSelection ? window.getSelection().toString().trim() : '';
  }
  return '';
};

/**
 * Check if there is currently selected text on the page
 * @returns {boolean} True if text is selected, false otherwise
 */
export const hasSelectedText = () => {
  if (!isBrowser()) return false;
  return getSelectedText().length > 0;
};

/**
 * Get detailed information about the current text selection
 * @returns {Object} Selection information including text, range, and position
 */
export const getSelectionInfo = () => {
  if (!isBrowser()) {
    return {
      text: '',
      range: null,
      rect: null,
      startContainer: null,
      endContainer: null
    };
  }

  const selection = window.getSelection();
  if (!selection || selection.rangeCount === 0) {
    return {
      text: '',
      range: null,
      rect: null,
      startContainer: null,
      endContainer: null
    };
  }

  const range = selection.getRangeAt(0);
  const rect = range.getBoundingClientRect();

  return {
    text: selection.toString().trim(),
    range: range,
    rect: {
      x: rect.x,
      y: rect.y,
      width: rect.width,
      height: rect.height,
      top: rect.top,
      right: rect.right,
      bottom: rect.bottom,
      left: rect.left
    },
    startContainer: range.startContainer,
    endContainer: range.endContainer
  };
};

/**
 * Add event listeners for text selection
 * @param {Function} callback - Function to call when text is selected
 * @returns {Function} Function to remove event listeners
 */
export const addTextSelectionListener = (callback) => {
  if (!isBrowser()) {
    return () => {};
  }

  const handleSelection = () => {
    const selectedText = getSelectedText();
    if (selectedText) {
      callback(selectedText);
    }
  };

  // Add event listeners
  document.addEventListener('mouseup', handleSelection);
  document.addEventListener('touchend', handleSelection);

  // Return cleanup function
  return () => {
    document.removeEventListener('mouseup', handleSelection);
    document.removeEventListener('touchend', handleSelection);
  };
};

/**
 * Remove text selection event listeners
 * @param {Function} callback - The same callback function that was used to add the listener
 */
export const removeTextSelectionListener = (callback) => {
  if (typeof document === 'undefined') {
    return;
  }

  // This function assumes the same callback function is used
  // In practice, you'd want to store the listener function reference
  // For this implementation, we'll just return the cleanup function from addTextSelectionListener
};

/**
 * Sanitize selected text to remove potentially harmful content
 * @param {string} text - The selected text to sanitize
 * @returns {string} Sanitized text
 */
export const sanitizeSelectedText = (text) => {
  if (typeof text !== 'string') {
    return '';
  }

  // Remove potentially harmful content
  return text
    .replace(/<script/gi, '&lt;script')
    .replace(/javascript:/gi, 'javascript&#58;')
    .replace(/on\w+\s*=/gi, '')
    .trim();
};

/**
 * Validate selected text to ensure it meets requirements
 * @param {string} text - The selected text to validate
 * @param {Object} options - Validation options
 * @param {number} [options.minLength] - Minimum length of selected text
 * @param {number} [options.maxLength] - Maximum length of selected text
 * @param {string} [options.minLengthMessage] - Message for minimum length violation
 * @param {string} [options.maxLengthMessage] - Message for maximum length violation
 * @returns {Object} Validation result with isValid and message properties
 */
export const validateSelectedText = (text, options = {}) => {
  const {
    minLength = 1,
    maxLength = 1000,
    minLengthMessage = 'Selected text is too short',
    maxLengthMessage = 'Selected text is too long'
  } = options;

  if (text.length < minLength) {
    return {
      isValid: false,
      message: minLengthMessage
    };
  }

  if (text.length > maxLength) {
    return {
      isValid: false,
      message: maxLengthMessage
    };
  }

  return {
    isValid: true,
    message: ''
  };
};

/**
 * Get the context around the selected text (surrounding text)
 * @param {number} contextLength - Number of characters before and after selection
 * @returns {Object} Context information including before, selection, and after text
 */
export const getSelectionContext = (contextLength = 50) => {
  if (!isBrowser()) {
    return {
      before: '',
      selection: '',
      after: '',
      fullContext: ''
    };
  }

  const selectionInfo = getSelectionInfo();
  if (!selectionInfo.range) {
    return {
      before: '',
      selection: '',
      after: '',
      fullContext: ''
    };
  }

  const range = selectionInfo.range;
  const startContainer = range.startContainer;
  const selectedText = selectionInfo.text;

  if (startContainer.nodeType !== Node.TEXT_NODE) {
    // If not a text node, we can't get precise context
    return {
      before: '',
      selection: selectedText,
      after: '',
      fullContext: selectedText
    };
  }

  const textContent = startContainer.textContent || '';
  const selectionStart = range.startOffset;
  const selectionEnd = range.endOffset;

  const before = textContent.substring(
    Math.max(0, selectionStart - contextLength),
    selectionStart
  );
  const after = textContent.substring(
    selectionEnd,
    Math.min(textContent.length, selectionEnd + contextLength)
  );

  return {
    before,
    selection: selectedText,
    after,
    fullContext: before + selectedText + after
  };
};

/**
 * Create a text selection observer that calls a callback when text is selected
 * @param {Function} callback - Function to call when text is selected
 * @returns {Object} Observer object with start and stop methods
 */
export const createTextSelectionObserver = (callback) => {
  if (!isBrowser()) {
    // Return a no-op observer for SSR
    return {
      start: () => {},
      stop: () => {},
      isObserving: () => false
    };
  }

  let isObserving = false;
  let cleanupFn = null;

  return {
    start: () => {
      if (isObserving) return;

      cleanupFn = addTextSelectionListener(callback);
      isObserving = true;
    },

    stop: () => {
      if (!isObserving || !cleanupFn) return;

      cleanupFn();
      isObserving = false;
    },

    isObserving: () => isObserving
  };
};