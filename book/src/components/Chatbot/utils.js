/**
 * Utility functions for the Chatbot component
 */

/**
 * Sanitize content to prevent XSS and other security issues
 * @param {string} content - Content to sanitize
 * @returns {string} Sanitized content
 */
export const sanitizeContent = (content) => {
  if (typeof content !== 'string') {
    return '';
  }

  // Remove potentially dangerous HTML tags and attributes
  let sanitized = content
    // Remove script tags and their content
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    // Remove iframe tags
    .replace(/<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi, '')
    // Remove object and embed tags
    .replace(/<object\b[^<]*(?:(?!<\/object>)<[^<]*)*<\/object>/gi, '')
    .replace(/<embed\b[^<]*(?:(?!<\/embed>)<[^<]*)*<\/embed>/gi, '')
    // Remove on* event handlers
    .replace(/\s*on\w+\s*=\s*["'][^"']*["']/gi, '')
    // Remove javascript: and data: URIs in href/src attributes
    .replace(/(href|src)\s*=\s*["']\s*javascript:/gi, '$1="#"')
    .replace(/(href|src)\s*=\s*["']\s*data:/gi, '$1="#"');

  // Additional sanitization can be added here as needed
  return sanitized;
};

/**
 * Sanitize an API response to prevent XSS
 * @param {Object} response - API response object
 * @returns {Object} Sanitized response object
 */
export const sanitizeAPIResponse = (response) => {
  if (!response || typeof response !== 'object') {
    return response;
  }

  return {
    ...response,
    answer: sanitizeContent(response.answer || ''),
    sources: Array.isArray(response.sources)
      ? response.sources.map(sanitizeContent)
      : response.sources || [],
    retrievedContext: Array.isArray(response.retrievedContext)
      ? response.retrievedContext.map(sanitizeContent)
      : response.retrievedContext || [],
    followupQuestions: Array.isArray(response.followupQuestions)
      ? response.followupQuestions.map(sanitizeContent)
      : response.followupQuestions || [],
  };
};

/**
 * Sanitize user input
 * @param {string} input - User input to sanitize
 * @returns {string} Sanitized input
 */
export const sanitizeUserInput = (input) => {
  if (typeof input !== 'string') {
    return '';
  }

  // Remove potentially dangerous characters/sequences
  return input
    .replace(/<script/gi, '&lt;script')
    .replace(/javascript:/gi, 'javascript&#58;')
    .replace(/on\w+\s*=/gi, 'on$&')
    .trim();
};