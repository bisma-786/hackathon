/**
 * API service for the RAG Chatbot component
 * Handles communication with the backend RAG system
 */

import { APIRequest, APIResponse } from './data-model';

/**
 * Chatbot API Service Class
 * Provides methods for communicating with the backend API
 */
export class ChatbotAPIService {
  /**
   * Create a ChatbotAPIService instance
   * @param {Object} config - API configuration
   * @param {string} config.apiEndpoint - Base URL for the backend API
   * @param {number} [config.timeoutMs] - Request timeout in milliseconds (default: 30000)
   * @param {string} [config.apiKey] - Optional API key for authentication
   */
  constructor(config) {
    this.apiEndpoint = config.apiEndpoint;
    this.timeoutMs = config.timeoutMs || 30000;
    this.apiKey = config.apiKey || null;
    this.isOnline = true; // Track online status
    this.lastCheckTime = null;
    this.checkInterval = null;
  }

  /**
   * Create headers for API requests
   * @returns {Object} Request headers
   */
  _getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    // Add authorization header if API key is provided
    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }

    return headers;
  }

  /**
   * Perform a fetch request with timeout
   * @param {string} url - Request URL
   * @param {Object} options - Request options
   * @returns {Promise<Response>} Response promise
   */
  async _fetchWithTimeout(url, options) {
    // Check if running in browser environment
    if (typeof fetch === 'undefined') {
      throw new Error('Network requests are not available in server environment');
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeoutMs);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);

      if (error.name === 'AbortError') {
        throw new Error(`Request timed out after ${this.timeoutMs}ms`);
      }

      throw error;
    }
  }

  /**
   * Validate and format API request
   * @param {APIRequest} apiRequest - Request object to validate
   * @returns {Object} Formatted request payload
   */
  _formatRequest(apiRequest) {
    if (!(apiRequest instanceof APIRequest)) {
      throw new Error('apiRequest must be an instance of APIRequest');
    }

    return {
      query: apiRequest.query,
      context: {
        selected_text: apiRequest.selectedText || '',
        page_url: apiRequest.pageContext?.url || '',
        page_title: apiRequest.pageContext?.title || ''
      },
      parameters: {
        temperature: 0.7,
        max_tokens: 500
      }
    };
  }

  /**
   * Validate and format API response
   * @param {Object} responseObj - Raw response object from API
   * @returns {APIResponse} Formatted API response
   */
  _formatResponse(responseObj) {
    // Validate response structure
    if (!responseObj || typeof responseObj !== 'object') {
      throw new Error('Invalid response format from API');
    }

    // If response has an error structure, handle it appropriately
    if (responseObj.status === 'error' && responseObj.errors) {
      throw new Error(`API Error: ${responseObj.errors.map(err => err.message).join(', ')}`);
    }

    // Extract the response data (might be nested in 'data' field)
    const responseData = responseObj.data || responseObj;

    return new APIResponse({
      answer: responseData.answer || responseData.data?.answer || 'No answer provided',
      sources: responseData.sources || responseData.data?.sources || [],
      confidence: responseData.confidence || responseData.data?.confidence || 0.5,
      retrievedContext: responseData.retrieved_context || responseData.retrievedContext || responseData.data?.retrieved_context || responseData.data?.retrievedContext || [],
      followupQuestions: responseData.followup_questions || responseData.followupQuestions || responseData.data?.followup_questions || responseData.data?.followupQuestions || [],
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Send a query to the backend API
   * Implements POST /api/agent/query API call
   * @param {APIRequest} apiRequest - Request object containing query and context
   * @returns {Promise<APIResponse>} Promise resolving to API response
   */
  async sendQuery(apiRequest) {
    try {
      // Format the request
      const payload = this._formatRequest(apiRequest);

      // Construct the API endpoint URL
      const url = `${this.apiEndpoint}/api/agent/query`;

      // Make the API request
      const response = await this._fetchWithTimeout(url, {
        method: 'POST',
        headers: this._getHeaders(),
        body: JSON.stringify(payload),
      });

      // Check if the response is OK
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: `HTTP ${response.status}: ${response.statusText}` }));
        throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
      }

      // Update online status on successful request
      this.isOnline = true;
      this.lastCheckTime = new Date().toISOString();

      // Parse the response
      const responseData = await response.json();

      // Format and return the response
      return this._formatResponse(responseData);
    } catch (error) {
      // Update online status on error
      if (error.name === 'AbortError') {
        this.isOnline = false;
        throw new Error(`Query request timed out after ${this.timeoutMs}ms. Please try again.`);
      } else if (error.message.includes('NetworkError') || error.message.includes('Failed to fetch')) {
        this.isOnline = false;
        throw new Error('Unable to connect to the backend service. Please check your connection and try again.');
      } else if (error.message.includes('HTTP 429')) {
        // Handle rate limiting
        this.isOnline = true; // Service is still online, just rate limited
        throw new Error('Rate limit exceeded. Please wait before sending another query.');
      } else if (error.message.includes('HTTP 503')) {
        // Handle service unavailable
        this.isOnline = false;
        throw new Error('The AI service is temporarily unavailable. Please try again later.');
      } else {
        throw new Error(`Error sending query to backend: ${error.message}`);
      }
    }
  }

  /**
   * Check the health of the backend API
   * Implements GET /health API call
   * @returns {Promise<boolean>} Promise resolving to health status
   */
  async checkHealth() {
    try {
      const url = `${this.apiEndpoint}/health`;

      const response = await this._fetchWithTimeout(url, {
        method: 'GET',
        headers: this._getHeaders(),
      });

      // Check if the response is OK
      if (!response.ok) {
        this.isOnline = false;
        this.lastCheckTime = new Date().toISOString();
        return false;
      }

      // Parse the response
      const responseData = await response.json();

      // Check if the service reports as healthy
      const isHealthy = responseData.status === 'healthy' ||
             responseData.status === 'ok' ||
             responseData.message?.includes('running');

      // Update online status
      this.isOnline = isHealthy;
      this.lastCheckTime = new Date().toISOString();

      return isHealthy;
    } catch (error) {
      console.warn('Health check failed:', error.message);
      this.isOnline = false;
      this.lastCheckTime = new Date().toISOString();
      return false;
    }
  }

  /**
   * Send a query with request/response validation
   * @param {APIRequest} apiRequest - Request object containing query and context
   * @returns {Promise<APIResponse>} Promise resolving to validated API response
   */
  async sendQueryWithValidation(apiRequest) {
    // Validate the request before sending
    if (!(apiRequest instanceof APIRequest)) {
      throw new Error('Request must be an instance of APIRequest');
    }

    // Send the query
    const response = await this.sendQuery(apiRequest);

    // Validate the response
    if (!(response instanceof APIResponse)) {
      throw new Error('Response is not in expected format');
    }

    return response;
  }

  /**
   * Get API configuration information
   * @returns {Object} Current API configuration
   */
  getConfig() {
    return {
      apiEndpoint: this.apiEndpoint,
      timeoutMs: this.timeoutMs,
      hasApiKey: !!this.apiKey
    };
  }

  /**
   * Starts monitoring the API connection status
   * @param {number} intervalMs - Interval in milliseconds to check status (default: 30000)
   */
  startConnectionMonitoring(intervalMs = 30000) {
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
    }

    this.checkInterval = setInterval(async () => {
      try {
        const isHealthy = await this.checkHealth();
        this.isOnline = isHealthy;
        this.lastCheckTime = new Date().toISOString();
      } catch (error) {
        this.isOnline = false;
        this.lastCheckTime = new Date().toISOString();
      }
    }, intervalMs);

    // Initial check
    this.checkHealth().then(isHealthy => {
      this.isOnline = isHealthy;
      this.lastCheckTime = new Date().toISOString();
    }).catch(() => {
      this.isOnline = false;
      this.lastCheckTime = new Date().toISOString();
    });
  }

  /**
   * Stops monitoring the API connection status
   */
  stopConnectionMonitoring() {
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
      this.checkInterval = null;
    }
  }

  /**
   * Update API configuration
   * @param {Object} newConfig - New configuration options
   * @param {string} [newConfig.apiEndpoint] - New API endpoint
   * @param {number} [newConfig.timeoutMs] - New timeout value
   * @param {string} [newConfig.apiKey] - New API key
   */
  updateConfig(newConfig) {
    if (newConfig.apiEndpoint !== undefined) {
      this.apiEndpoint = newConfig.apiEndpoint;
    }
    if (newConfig.timeoutMs !== undefined) {
      this.timeoutMs = newConfig.timeoutMs;
    }
    if (newConfig.apiKey !== undefined) {
      this.apiKey = newConfig.apiKey;
    }
  }
}

/**
 * Utility function to create an API service instance with default configuration
 * @param {Object} overrides - Configuration overrides
 * @returns {ChatbotAPIService} Configured API service instance
 */
export const createChatbotAPIService = (overrides = {}) => {
  // Get default configuration from environment or use defaults
  const defaultConfig = {
    apiEndpoint: process.env.CHATBOT_API_ENDPOINT || 'http://localhost:8000',
    timeoutMs: parseInt(process.env.CHATBOT_TIMEOUT_MS) || 30000,
    apiKey: process.env.CHATBOT_API_KEY || null
  };

  // Merge with overrides
  const config = { ...defaultConfig, ...overrides };

  return new ChatbotAPIService(config);
};

// Export a default instance for convenience
export const defaultAPIService = createChatbotAPIService();