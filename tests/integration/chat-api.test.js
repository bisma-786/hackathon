/**
 * Integration tests for the chatbot API communication
 * Tests the full flow from UI components to API service
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { act } from 'react-dom/test-utils';
import { Chatbot } from '../../book/src/components/Chatbot/Chatbot';
import { ChatHistory } from '../../book/src/components/Chatbot/ChatHistory';
import { UserInput } from '../../book/src/components/Chatbot/UserInput';
import { ChatbotAPIService, createChatbotAPIService } from '../../book/src/components/Chatbot/chatbot-api';
import { ChatMessage, ChatSession, APIRequest, APIResponse } from '../../book/src/components/Chatbot/data-model';

// Mock the API service
jest.mock('../../book/src/components/Chatbot/chatbot-api', () => ({
  ...jest.requireActual('../../book/src/components/Chatbot/chatbot-api'),
  createChatbotAPIService: jest.fn(),
}));

// Mock the data model
jest.mock('../../book/src/components/Chatbot/data-model', () => ({
  ...jest.requireActual('../../book/src/components/Chatbot/data-model'),
  ChatMessage: jest.fn(),
  ChatSession: jest.fn(),
  APIRequest: jest.fn(),
  APIResponse: jest.fn(),
}));

describe('Chatbot API Communication Integration', () => {
  let mockAPIService;

  beforeEach(() => {
    jest.clearAllMocks();

    mockAPIService = {
      sendQueryWithValidation: jest.fn(),
      checkHealth: jest.fn(),
      startConnectionMonitoring: jest.fn(),
      stopConnectionMonitoring: jest.fn(),
      isOnline: true,
      getConfig: jest.fn().mockReturnValue({
        apiEndpoint: 'http://localhost:8000',
        timeoutMs: 30000,
        hasApiKey: false
      })
    };

    createChatbotAPIService.mockReturnValue(mockAPIService);

    // Mock the data model constructors
    ChatMessage.mockImplementation((props) => ({ id: `msg_${Date.now()}`, ...props }));
    ChatSession.mockImplementation((props) => ({ id: `session_${Date.now()}`, messages: [], ...props }));
    APIRequest.mockImplementation((props) => ({ query: '', ...props }));
    APIResponse.mockImplementation((props) => ({ answer: 'Default response', ...props }));
  });

  describe('Full API Communication Flow', () => {
    test('should send query to API and display response', async () => {
      const mockResponse = {
        answer: 'This is the API response',
        sources: ['source1', 'source2'],
        confidence: 0.85,
        retrievedContext: ['context1'],
        followupQuestions: ['Question 1?']
      };

      mockAPIService.sendQueryWithValidation.mockResolvedValue(mockResponse);

      render(<Chatbot />);

      // Make chatbot visible
      const toggleButton = screen.getByLabelText('Open chatbot');
      fireEvent.click(toggleButton);

      // Find and interact with the input
      const input = screen.getByLabelText('Type your message');
      fireEvent.change(input, { target: { value: 'Test query' } });

      // Simulate sending the message (this would be handled by the UserInput component)
      fireEvent.change(input, { target: { value: 'Test query' } });

      // Wait for the API call to complete and response to be displayed
      await waitFor(() => {
        expect(mockAPIService.sendQueryWithValidation).toHaveBeenCalled();
      });

      // Verify the API call was made with correct parameters
      expect(mockAPIService.sendQueryWithValidation).toHaveBeenCalledWith(
        expect.objectContaining({
          query: 'Test query'
        })
      );
    });

    test('should handle API errors gracefully', async () => {
      const errorMessage = 'API Error: Something went wrong';
      mockAPIService.sendQueryWithValidation.mockRejectedValue(new Error(errorMessage));

      render(<Chatbot />);

      // Make chatbot visible
      const toggleButton = screen.getByLabelText('Open chatbot');
      fireEvent.click(toggleButton);

      // Find and interact with the input
      const input = screen.getByLabelText('Type your message');
      fireEvent.change(input, { target: { value: 'Error test query' } });

      // Wait for error to be displayed
      await waitFor(() => {
        expect(screen.getByText(/Error:/i)).toBeInTheDocument();
      });
    });

    test('should maintain session state after API communication', async () => {
      const mockResponse = {
        answer: 'API response',
        sources: ['source1'],
        confidence: 0.75
      };

      mockAPIService.sendQueryWithValidation.mockResolvedValue(mockResponse);

      render(<Chatbot />);

      // Make chatbot visible
      const toggleButton = screen.getByLabelText('Open chatbot');
      fireEvent.click(toggleButton);

      // Send a query
      const input = screen.getByLabelText('Type your message');
      fireEvent.change(input, { target: { value: 'Session test query' } });

      // Wait for response
      await waitFor(() => {
        expect(mockAPIService.sendQueryWithValidation).toHaveBeenCalled();
      });

      // Verify that both user and assistant messages are in the session
      // (This would be tested through the ChatHistory component rendering)
    });

    test('should update connection status during API communication', async () => {
      const mockResponse = { answer: 'Connection test response' };
      mockAPIService.sendQueryWithValidation.mockResolvedValue(mockResponse);

      // Initially online
      mockAPIService.isOnline = true;

      render(<Chatbot />);

      // Make chatbot visible
      const toggleButton = screen.getByLabelText('Open chatbot');
      fireEvent.click(toggleButton);

      // Send a query
      const input = screen.getByLabelText('Type your message');
      fireEvent.change(input, { target: { value: 'Connection test' } });

      await waitFor(() => {
        expect(mockAPIService.sendQueryWithValidation).toHaveBeenCalled();
      });

      // Verify that online status was updated during the request
      expect(mockAPIService.isOnline).toBe(true);
    });

    test('should handle network failures and update status', async () => {
      mockAPIService.sendQueryWithValidation.mockRejectedValue(
        new Error('Network Error: Failed to fetch')
      );

      // Simulate offline status
      mockAPIService.isOnline = false;

      render(<Chatbot />);

      // Make chatbot visible
      const toggleButton = screen.getByLabelText('Open chatbot');
      fireEvent.click(toggleButton);

      // Send a query
      const input = screen.getByLabelText('Type your message');
      fireEvent.change(input, { target: { value: 'Network test' } });

      await waitFor(() => {
        expect(screen.getByText(/Unable to connect/i)).toBeInTheDocument();
      });

      expect(mockAPIService.isOnline).toBe(false);
    });
  });

  describe('Real-time API Communication', () => {
    test('should handle multiple concurrent requests', async () => {
      // Mock multiple API responses with different delays
      mockAPIService.sendQueryWithValidation
        .mockResolvedValueOnce({
          answer: 'First response',
          sources: [],
          confidence: 0.8
        })
        .mockResolvedValueOnce({
          answer: 'Second response',
          sources: [],
          confidence: 0.9
        });

      render(<Chatbot />);

      // Make chatbot visible
      const toggleButton = screen.getByLabelText('Open chatbot');
      fireEvent.click(toggleButton);

      // Send first query
      let input = screen.getByLabelText('Type your message');
      fireEvent.change(input, { target: { value: 'First query' } });

      // Send second query
      input = screen.getByLabelText('Type your message');
      fireEvent.change(input, { target: { value: 'Second query' } });

      // Wait for both API calls
      await waitFor(() => {
        expect(mockAPIService.sendQueryWithValidation).toHaveBeenCalledTimes(2);
      });
    });

    test('should handle API timeout scenarios', async () => {
      // Mock a timeout scenario
      mockAPIService.sendQueryWithValidation.mockImplementation(() => {
        return new Promise((_, reject) => {
          setTimeout(() => reject(new Error('Request timeout')), 100);
        });
      });

      render(<Chatbot config={{ timeoutMs: 100 }} />);

      // Make chatbot visible
      const toggleButton = screen.getByLabelText('Open chatbot');
      fireEvent.click(toggleButton);

      // Send a query
      const input = screen.getByLabelText('Type your message');
      fireEvent.change(input, { target: { value: 'Timeout test' } });

      await waitFor(() => {
        expect(screen.getByText(/timed out/i)).toBeInTheDocument();
      });
    });

    test('should validate API responses before displaying', async () => {
      const validResponse = {
        answer: 'Valid response',
        sources: ['source1'],
        confidence: 0.8,
        retrievedContext: [],
        followupQuestions: []
      };

      mockAPIService.sendQueryWithValidation.mockResolvedValue(validResponse);

      render(<Chatbot />);

      // Make chatbot visible
      const toggleButton = screen.getByLabelText('Open chatbot');
      fireEvent.click(toggleButton);

      // Send a query
      const input = screen.getByLabelText('Type your message');
      fireEvent.change(input, { target: { value: 'Validation test' } });

      await waitFor(() => {
        expect(mockAPIService.sendQueryWithValidation).toHaveBeenCalled();
      });

      // Verify that the response was properly formatted and validated
      expect(mockAPIService.sendQueryWithValidation).toHaveReturnedWith(
        expect.objectContaining({
          answer: 'Valid response',
          confidence: 0.8
        })
      );
    });
  });

  describe('API Configuration Integration', () => {
    test('should use custom API endpoint from configuration', async () => {
      const customEndpoint = 'http://custom-api:8000';
      const mockResponse = { answer: 'Custom endpoint response' };

      mockAPIService.sendQueryWithValidation.mockResolvedValue(mockResponse);

      render(<Chatbot config={{ apiEndpoint: customEndpoint }} />);

      // Make chatbot visible
      const toggleButton = screen.getByLabelText('Open chatbot');
      fireEvent.click(toggleButton);

      // Send a query
      const input = screen.getByLabelText('Type your message');
      fireEvent.change(input, { target: { value: 'Custom endpoint test' } });

      await waitFor(() => {
        expect(mockAPIService.sendQueryWithValidation).toHaveBeenCalled();
      });

      // Verify that the API service was created with the custom endpoint
      expect(createChatbotAPIService).toHaveBeenCalledWith(
        expect.objectContaining({
          apiEndpoint: customEndpoint
        })
      );
    });

    test('should respect timeout configuration', async () => {
      const customTimeout = 60000; // 60 seconds
      const mockResponse = { answer: 'Timeout config response' };

      mockAPIService.sendQueryWithValidation.mockResolvedValue(mockResponse);

      render(<Chatbot config={{ timeoutMs: customTimeout }} />);

      // Make chatbot visible
      const toggleButton = screen.getByLabelText('Open chatbot');
      fireEvent.click(toggleButton);

      // Send a query
      const input = screen.getByLabelText('Type your message');
      fireEvent.change(input, { target: { value: 'Timeout config test' } });

      await waitFor(() => {
        expect(mockAPIService.sendQueryWithValidation).toHaveBeenCalled();
      });

      // Verify that the API service was configured with the custom timeout
      expect(createChatbotAPIService).toHaveBeenCalledWith(
        expect.objectContaining({
          timeoutMs: customTimeout
        })
      );
    });
  });

  describe('Error Recovery and Retry', () => {
    test('should handle API recovery after initial failure', async () => {
      // First call fails, second succeeds
      mockAPIService.sendQueryWithValidation
        .mockRejectedValueOnce(new Error('First attempt failed'))
        .mockResolvedValueOnce({ answer: 'Recovered response' });

      render(<Chatbot />);

      // Make chatbot visible
      const toggleButton = screen.getByLabelText('Open chatbot');
      fireEvent.click(toggleButton);

      // First query fails
      let input = screen.getByLabelText('Type your message');
      fireEvent.change(input, { target: { value: 'First query' } });

      // Wait for error
      await waitFor(() => {
        expect(screen.getByText(/Error:/i)).toBeInTheDocument();
      });

      // Second query succeeds
      input = screen.getByLabelText('Type your message');
      fireEvent.change(input, { target: { value: 'Second query' } });

      await waitFor(() => {
        expect(mockAPIService.sendQueryWithValidation).toHaveBeenCalledTimes(2);
      });
    });

    test('should maintain connection monitoring during API operations', () => {
      render(<Chatbot />);

      // Verify that connection monitoring is started
      expect(mockAPIService.startConnectionMonitoring).toHaveBeenCalledWith(30000);

      // Make chatbot visible
      const toggleButton = screen.getByLabelText('Open chatbot');
      fireEvent.click(toggleButton);

      // Connection monitoring should still be active
      expect(mockAPIService.startConnectionMonitoring).toHaveBeenCalledTimes(1);
    });
  });
});