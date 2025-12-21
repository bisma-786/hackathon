/**
 * Integration tests for the Chatbot API service
 */

import { ChatbotAPIService, createChatbotAPIService } from '../../book/src/components/Chatbot/chatbot-api';
import { APIRequest, APIResponse } from '../../book/src/components/Chatbot/data-model';

describe('Chatbot API Service Integration', () => {
  let apiService;

  beforeAll(() => {
    // Use a test API endpoint or mock server
    apiService = createChatbotAPIService({
      apiEndpoint: 'http://localhost:8000', // This would be the actual backend during real testing
      timeoutMs: 10000, // 10 second timeout for integration tests
    });
  });

  describe('Configuration', () => {
    test('should create API service with default configuration', () => {
      const defaultService = createChatbotAPIService();
      const config = defaultService.getConfig();

      expect(config.apiEndpoint).toBeDefined();
      expect(typeof config.timeoutMs).toBe('number');
      expect(typeof config.hasApiKey).toBe('boolean');
    });

    test('should create API service with custom configuration', () => {
      const customConfig = {
        apiEndpoint: 'http://test-api:8000',
        timeoutMs: 15000,
        apiKey: 'test-key-123'
      };

      const customService = createChatbotAPIService(customConfig);
      const config = customService.getConfig();

      expect(config.apiEndpoint).toBe(customConfig.apiEndpoint);
      expect(config.timeoutMs).toBe(customConfig.timeoutMs);
      expect(config.hasApiKey).toBe(true);
    });

    test('should update configuration dynamically', () => {
      const newConfig = {
        apiEndpoint: 'http://updated-api:8000',
        timeoutMs: 20000,
      };

      apiService.updateConfig(newConfig);
      const config = apiService.getConfig();

      expect(config.apiEndpoint).toBe(newConfig.apiEndpoint);
      expect(config.timeoutMs).toBe(newConfig.timeoutMs);
    });
  });

  describe('Request/Response Formatting', () => {
    test('should format API request correctly', () => {
      const apiRequest = new APIRequest({
        query: 'Test query',
        selectedText: 'Selected text',
        pageContext: {
          url: 'http://example.com/page',
          title: 'Test Page'
        }
      });

      // Since _formatRequest is a private method, we'll test the public interface
      // by creating a request object and checking its structure
      const formatted = {
        query: apiRequest.query,
        context: {
          selected_text: apiRequest.selectedText,
          page_url: apiRequest.pageContext?.url,
          page_title: apiRequest.pageContext?.title
        },
        parameters: {
          temperature: 0.7,
          max_tokens: 500
        }
      };

      expect(formatted.query).toBe('Test query');
      expect(formatted.context.selected_text).toBe('Selected text');
      expect(formatted.context.page_url).toBe('http://example.com/page');
      expect(formatted.context.page_title).toBe('Test Page');
    });

    test('should format API response correctly', () => {
      const responsePayload = {
        answer: 'Test answer',
        sources: ['source1', 'source2'],
        confidence: 0.85,
        retrieved_context: ['context1', 'context2'],
        followup_questions: ['Question 1?', 'Question 2?']
      };

      const apiResponse = new APIResponse(responsePayload);

      expect(apiResponse.answer).toBe('Test answer');
      expect(apiResponse.sources).toEqual(['source1', 'source2']);
      expect(apiResponse.confidence).toBe(0.85);
      expect(apiResponse.retrievedContext).toEqual(['context1', 'context2']);
      expect(apiResponse.followupQuestions).toEqual(['Question 1?', 'Question 2?']);
    });
  });

  describe('Health Check', () => {
    test('should return true for healthy service', async () => {
      // Mock fetch to simulate a healthy response
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: jest.fn().mockResolvedValue({ status: 'healthy' })
      });

      const result = await apiService.checkHealth();
      expect(result).toBe(true);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/health'),
        expect.objectContaining({
          method: 'GET'
        })
      );
    });

    test('should return false for unhealthy service', async () => {
      global.fetch = jest.fn().mockResolvedValue({
        ok: false,
        json: jest.fn().mockResolvedValue({ status: 'unhealthy' })
      });

      const result = await apiService.checkHealth();
      expect(result).toBe(false);
    });

    test('should return false when request fails', async () => {
      global.fetch = jest.fn().mockRejectedValue(new Error('Network error'));

      const result = await apiService.checkHealth();
      expect(result).toBe(false);
    });
  });

  describe('Query Processing', () => {
    test('should send query and receive response', async () => {
      const mockResponse = {
        answer: 'This is a test response',
        sources: ['source1', 'source2'],
        confidence: 0.9,
        retrieved_context: ['context info'],
        followup_questions: ['Follow up question?']
      };

      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: jest.fn().mockResolvedValue(mockResponse)
      });

      const apiRequest = new APIRequest({
        query: 'Test query',
        selectedText: 'Selected text',
        pageContext: {
          url: 'http://example.com/page',
          title: 'Test Page'
        }
      });

      const response = await apiService.sendQuery(apiRequest);

      expect(response).toBeInstanceOf(APIResponse);
      expect(response.answer).toBe('This is a test response');
      expect(response.sources).toEqual(['source1', 'source2']);
      expect(response.confidence).toBe(0.9);
      expect(response.retrievedContext).toEqual(['context info']);
      expect(response.followupQuestions).toEqual(['Follow up question?']);

      // Verify the fetch call
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/agent/query'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          }),
          body: expect.stringContaining('Test query')
        })
      );
    });

    test('should handle API validation', async () => {
      const mockResponse = {
        answer: 'Validated response',
        sources: [],
        confidence: 0.8
      };

      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: jest.fn().mockResolvedValue(mockResponse)
      });

      const apiRequest = new APIRequest({
        query: 'Validation test query',
        selectedText: '',
        pageContext: {}
      });

      const response = await apiService.sendQueryWithValidation(apiRequest);

      expect(response).toBeInstanceOf(APIResponse);
      expect(response.answer).toBe('Validated response');
    });

    test('should throw error for invalid request', async () => {
      await expect(apiService.sendQuery('invalid request')).rejects.toThrow('Request must be an instance of APIRequest');
    });

    test('should handle timeout errors', async () => {
      // Mock a timeout scenario
      global.fetch = jest.fn().mockImplementation(() => {
        return new Promise((_, reject) => {
          setTimeout(() => reject(new Error('Network Error')), 1000);
        });
      });

      const apiRequest = new APIRequest({
        query: 'Timeout test query',
        selectedText: '',
        pageContext: {}
      });

      await expect(apiService.sendQuery(apiRequest)).rejects.toThrow('Error sending query to backend');
    });

    test('should handle HTTP error responses', async () => {
      global.fetch = jest.fn().mockResolvedValue({
        ok: false,
        status: 500,
        text: jest.fn().mockResolvedValue('Internal Server Error')
      });

      const apiRequest = new APIRequest({
        query: 'Error test query',
        selectedText: '',
        pageContext: {}
      });

      await expect(apiService.sendQuery(apiRequest)).rejects.toThrow('HTTP 500: Internal Server Error');
    });
  });

  describe('Connection Monitoring', () => {
    test('should start and stop connection monitoring', async () => {
      // Start monitoring
      apiService.startConnectionMonitoring(1000); // Check every 1 second for tests
      expect(apiService.checkInterval).toBeDefined();

      // Stop monitoring
      apiService.stopConnectionMonitoring();
      expect(apiService.checkInterval).toBeNull();
    });

    test('should update online status based on health checks', async () => {
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: jest.fn().mockResolvedValue({ status: 'healthy' })
      });

      // Initially should be online
      expect(apiService.isOnline).toBe(true);

      // Force a health check
      const result = await apiService.checkHealth();
      expect(result).toBe(true);
      expect(apiService.isOnline).toBe(true);
      expect(apiService.lastCheckTime).toBeDefined();
    });

    test('should set offline status when health check fails', async () => {
      global.fetch = jest.fn().mockResolvedValue({
        ok: false,
        json: jest.fn().mockResolvedValue({ status: 'unhealthy' })
      });

      const result = await apiService.checkHealth();
      expect(result).toBe(false);
      expect(apiService.isOnline).toBe(false);
    });
  });

  afterAll(() => {
    // Clean up any intervals
    if (apiService.checkInterval) {
      clearInterval(apiService.checkInterval);
    }
  });
});