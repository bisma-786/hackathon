/**
 * Unit tests for the text selection utilities
 */

import {
  getSelectedText,
  hasSelectedText,
  getSelectionInfo,
  addTextSelectionListener,
  sanitizeSelectedText,
  validateSelectedText,
  getSelectionContext,
  createTextSelectionObserver
} from '../../book/src/components/Chatbot/text-selection';

// Mock the window and document objects for testing
const mockSelection = {
  toString: jest.fn(),
  rangeCount: 1,
  getRangeAt: jest.fn(() => ({
    getBoundingClientRect: jest.fn(() => ({
      x: 0, y: 0, width: 100, height: 20, top: 0, right: 100, bottom: 20, left: 0
    })),
    startContainer: { nodeType: Node.TEXT_NODE, textContent: 'This is sample text for testing.' },
    endContainer: { nodeType: Node.TEXT_NODE },
    startOffset: 5,
    endOffset: 10
  }))
};

describe('Text Selection Utilities', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getSelectedText', () => {
    test('returns selected text when selection exists', () => {
      Object.defineProperty(window, 'getSelection', {
        value: () => ({
          toString: () => 'Selected text'
        }),
        writable: true
      });

      expect(getSelectedText()).toBe('Selected text');
    });

    test('returns empty string when no selection exists', () => {
      Object.defineProperty(window, 'getSelection', {
        value: () => ({
          toString: () => ''
        }),
        writable: true
      });

      expect(getSelectedText()).toBe('');
    });

    test('returns empty string when window is not defined', () => {
      // Temporarily remove window.getSelection
      const originalGetSelection = window.getSelection;
      delete window.getSelection;

      expect(getSelectedText()).toBe('');

      // Restore original function
      window.getSelection = originalGetSelection;
    });
  });

  describe('hasSelectedText', () => {
    test('returns true when text is selected', () => {
      Object.defineProperty(window, 'getSelection', {
        value: () => ({
          toString: () => 'Selected text'
        }),
        writable: true
      });

      expect(hasSelectedText()).toBe(true);
    });

    test('returns false when no text is selected', () => {
      Object.defineProperty(window, 'getSelection', {
        value: () => ({
          toString: () => ''
        }),
        writable: true
      });

      expect(hasSelectedText()).toBe(false);
    });
  });

  describe('getSelectionInfo', () => {
    test('returns selection information when selection exists', () => {
      Object.defineProperty(window, 'getSelection', {
        value: () => mockSelection,
        writable: true
      });

      const selectionInfo = getSelectionInfo();

      expect(selectionInfo.text).toBeDefined();
      expect(selectionInfo.range).toBeDefined();
      expect(selectionInfo.rect).toBeDefined();
      expect(typeof selectionInfo.rect.x).toBe('number');
      expect(typeof selectionInfo.rect.y).toBe('number');
    });

    test('returns empty selection info when no selection exists', () => {
      Object.defineProperty(window, 'getSelection', {
        value: () => null,
        writable: true
      });

      const selectionInfo = getSelectionInfo();

      expect(selectionInfo.text).toBe('');
      expect(selectionInfo.range).toBeNull();
      expect(selectionInfo.rect).toBeNull();
    });

    test('returns empty selection info when window is not defined', () => {
      // Temporarily remove window object
      const originalWindow = global.window;
      delete global.window;

      const selectionInfo = getSelectionInfo();

      expect(selectionInfo.text).toBe('');
      expect(selectionInfo.range).toBeNull();
      expect(selectionInfo.rect).toBeNull();

      // Restore window
      global.window = originalWindow;
    });
  });

  describe('sanitizeSelectedText', () => {
    test('removes script tags', () => {
      const input = 'Text with <script>alert("xss")</script> content';
      const sanitized = sanitizeSelectedText(input);

      expect(sanitized).toBe('Text with &lt;script>alert("xss")&lt;/script> content');
    });

    test('removes javascript: URIs', () => {
      const input = 'Link with javascript:alert(1)';
      const sanitized = sanitizeSelectedText(input);

      expect(sanitized).toBe('Link with javascript&#58;alert(1)');
    });

    test('handles non-string input', () => {
      expect(sanitizeSelectedText(null)).toBe('');
      expect(sanitizeSelectedText(undefined)).toBe('');
      expect(sanitizeSelectedText(123)).toBe('');
    });

    test('trims whitespace', () => {
      const input = '  spaced text  ';
      const sanitized = sanitizeSelectedText(input);

      expect(sanitized).toBe('spaced text');
    });
  });

  describe('validateSelectedText', () => {
    test('returns valid for text within length limits', () => {
      const result = validateSelectedText('Valid text', { minLength: 1, maxLength: 100 });

      expect(result.isValid).toBe(true);
      expect(result.message).toBe('');
    });

    test('returns invalid for text shorter than minimum', () => {
      const result = validateSelectedText('A', { minLength: 5, maxLength: 100 });

      expect(result.isValid).toBe(false);
      expect(result.message).toBe('Selected text is too short');
    });

    test('returns invalid for text longer than maximum', () => {
      const longText = 'A'.repeat(101);
      const result = validateSelectedText(longText, { minLength: 1, maxLength: 100 });

      expect(result.isValid).toBe(false);
      expect(result.message).toBe('Selected text is too long');
    });

    test('uses custom validation messages', () => {
      const result = validateSelectedText('A', {
        minLength: 5,
        minLengthMessage: 'Text must be at least 5 characters'
      });

      expect(result.message).toBe('Text must be at least 5 characters');
    });

    test('uses default options when not provided', () => {
      const result = validateSelectedText('');

      expect(result.isValid).toBe(false);
      expect(result.message).toBe('Selected text is too short');
    });
  });

  describe('getSelectionContext', () => {
    test('returns context around selection', () => {
      // Mock window.getSelection to return our mock selection
      Object.defineProperty(window, 'getSelection', {
        value: () => mockSelection,
        writable: true
      });

      const context = getSelectionContext(10);

      expect(context.before).toBeDefined();
      expect(context.selection).toBeDefined();
      expect(context.after).toBeDefined();
      expect(context.fullContext).toBeDefined();
    });

    test('returns empty context when no selection exists', () => {
      Object.defineProperty(window, 'getSelection', {
        value: () => null,
        writable: true
      });

      const context = getSelectionContext();

      expect(context.before).toBe('');
      expect(context.selection).toBe('');
      expect(context.after).toBe('');
      expect(context.fullContext).toBe('');
    });
  });

  describe('createTextSelectionObserver', () => {
    test('creates an observer with start and stop methods', () => {
      const callback = jest.fn();
      const observer = createTextSelectionObserver(callback);

      expect(typeof observer.start).toBe('function');
      expect(typeof observer.stop).toBe('function');
      expect(typeof observer.isObserving).toBe('function');
      expect(observer.isObserving()).toBe(false);
    });

    test('can start and stop observing', () => {
      const callback = jest.fn();
      const observer = createTextSelectionObserver(callback);

      // Initially not observing
      expect(observer.isObserving()).toBe(false);

      // Start observing
      observer.start();
      expect(observer.isObserving()).toBe(true);

      // Stop observing
      observer.stop();
      expect(observer.isObserving()).toBe(false);
    });
  });

  describe('addTextSelectionListener', () => {
    test('adds event listeners and returns cleanup function', () => {
      const callback = jest.fn();
      const cleanup = addTextSelectionListener(callback);

      expect(typeof cleanup).toBe('function');
    });

    test('calls callback when text is selected', () => {
      const callback = jest.fn();
      Object.defineProperty(window, 'getSelection', {
        value: () => ({
          toString: () => 'Selected text'
        }),
        writable: true
      });

      const cleanup = addTextSelectionListener(callback);

      // Simulate a mouseup event
      document.dispatchEvent(new Event('mouseup'));

      expect(callback).toHaveBeenCalledWith('Selected text');

      cleanup();
    });
  });

  describe('integration tests', () => {
    test('full text selection flow works correctly', () => {
      const originalGetSelection = window.getSelection;

      // Set up a mock selection
      Object.defineProperty(window, 'getSelection', {
        value: () => ({
          toString: () => 'This is selected text',
          rangeCount: 0 // No ranges for simplicity in this test
        }),
        writable: true
      });

      // Test getting selected text
      const selectedText = getSelectedText();
      expect(selectedText).toBe('This is selected text');

      // Test that text exists
      expect(hasSelectedText()).toBe(true);

      // Test sanitization
      const sanitized = sanitizeSelectedText(selectedText);
      expect(sanitized).toBe('This is selected text'); // Should be unchanged in this case

      // Test validation
      const validation = validateSelectedText(selectedText, { minLength: 1, maxLength: 100 });
      expect(validation.isValid).toBe(true);

      // Restore original function
      window.getSelection = originalGetSelection;
    });

    test('handles edge cases gracefully', () => {
      // Test with empty string
      const emptyValidation = validateSelectedText('');
      expect(emptyValidation.isValid).toBe(false);

      // Test with very long string
      const longString = 'A'.repeat(2000);
      const longValidation = validateSelectedText(longString, { maxLength: 1000 });
      expect(longValidation.isValid).toBe(false);

      // Test sanitization of malicious content
      const maliciousInput = '<script>alert("xss")</script>';
      const sanitized = sanitizeSelectedText(maliciousInput);
      expect(sanitized).toContain('&lt;script&gt;');
    });
  });
});