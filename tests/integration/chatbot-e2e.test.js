/**
 * End-to-End tests for the complete chatbot flow
 * Tests the full integration from UI interaction to API communication and response display
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import { act } from 'react-dom/test-utils';
import { Chatbot } from '../../book/src/components/Chatbot/Chatbot';
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

// Mock the child components to avoid complex rendering
jest.mock('../../book/src/components/Chatbot/ChatHistory', () => ({
  ChatHistory: ({ messages, isLoading, showSources }) => (
    <div data-testid="chat-history">
      <div data-testid="messages-count">{messages.length}</div>
      <div data-testid="loading-status">{isLoading ? 'loading' : 'not loading'}</div>
      {messages.map((msg, index) => (
        <div key={msg.id || `msg-${index}`} data-testid={`message-${msg.sender}`}>
          <span data-testid="message-content">{msg.content}</span>
        </div>
      ))}
    </div>
  ),
}));

jest.mock('../../book/src/components/Chatbot/UserInput', () => ({
  UserInput: ({ onSendMessage, isLoading, selectedText, maxQueryLength, disabled }) => (
    <div data-testid="user-input">
      <textarea
        data-testid="message-input"
        onChange={(e) => onSendMessage(e.target.value)}
        disabled={isLoading || disabled}
        placeholder="Type your message..."
        maxLength={maxQueryLength}
        data-selected-text={selectedText}
      />
      <button
        data-testid="send-button"
        onClick={() => {
          const input = document.querySelector('[data-testid="message-input"]');
          if (input && input.value.trim()) {
            onSendMessage(input.value);
          }
        }}
        disabled={isLoading || disabled}
      >
        Send
      </button>
    </div>
  ),
}));

describe('Chatbot End-to-End Flow', () => {
  let mockAPIService;

  beforeEach(() => {
    jest.clearAllMocks();

    mockAPIService = {
      sendQueryWithValidation: jest.fn(),
      checkHealth: jest.fn().mockResolvedValue(true),
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
    ChatMessage.mockImplementation((props) => ({ id: `msg_${Date.now()}_${Math.random()}`, ...props }));
    ChatSession.mockImplementation((props) => ({ id: `session_${Date.now()}`, messages: [], ...props }));
    APIRequest.mockImplementation((props) => ({ query: '', ...props }));
    APIResponse.mockImplementation((props) => ({ answer: 'Default response', ...props }));
  });

  test('complete flow: open chatbot -> enter query -> receive response -> display message', async () => {
    const mockResponse = {
      answer: 'This is the AI response to your query',
      sources: ['source1', 'source2'],
      confidence: 0.85,
      retrievedContext: ['context information'],
      followupQuestions: ['Follow up question?']
    };

    mockAPIService.sendQueryWithValidation.mockResolvedValue(mockResponse);

    render(<Chatbot />);

    // 1. Initial state: toggle button should be visible
    const toggleButton = screen.getByLabelText('Open chatbot');
    expect(toggleButton).toBeInTheDocument();

    // 2. Click toggle to open chatbot
    fireEvent.click(toggleButton);

    // 3. Verify chatbot container is now visible
    expect(screen.getByLabelText('AI Assistant Chatbot')).toBeInTheDocument();

    // 4. Find the input field and enter a query
    const messageInput = screen.getByTestId('message-input');
    expect(messageInput).toBeInTheDocument();

    fireEvent.change(messageInput, { target: { value: 'What is artificial intelligence?' } });

    // 5. Verify input has the correct value
    expect(messageInput.value).toBe('What is artificial intelligence?');

    // 6. Submit the query (simulated by calling the onSendMessage prop)
    fireEvent.change(messageInput, { target: { value: 'What is artificial intelligence?' } });

    // 7. Wait for API call to complete and response to be displayed
    await waitFor(() => {
      expect(mockAPIService.sendQueryWithValidation).toHaveBeenCalled();
    });

    // 8. Verify the API was called with correct parameters
    expect(mockAPIService.sendQueryWithValidation).toHaveBeenCalledWith(
      expect.objectContaining({
        query: 'What is artificial intelligence?'
      })
    );

    // 9. Verify the response is displayed in the chat history
    await waitFor(() => {
      const messages = screen.getAllByTestId(/message-(user|assistant)/);
      expect(messages).toHaveLength(2); // User message + Assistant response
    });

    // 10. Verify the assistant's response is displayed
    expect(screen.getByTestId('message-content')).toHaveTextContent(mockResponse.answer);
  });

  test('flow with selected text: select text -> open chatbot -> verify text pre-filled', async () => {
    // Mock window.getSelection for selected text
    Object.defineProperty(window, 'getSelection', {
      value: () => ({
        toString: () => 'This is the selected text from the page'
      }),
      writable: true
    });

    const mockResponse = { answer: 'Response based on selected text' };
    mockAPIService.sendQueryWithValidation.mockResolvedValue(mockResponse);

    render(<Chatbot options={{ enableSelectedText: true }} />);

    // Simulate text selection (this would normally happen via user interaction)
    act(() => {
      const selectionEvent = new Event('mouseup', { bubbles: true });
      document.dispatchEvent(selectionEvent);
    });

    // Open chatbot
    const toggleButton = screen.getByLabelText('Open chatbot');
    fireEvent.click(toggleButton);

    // Verify the selected text is shown in the input area
    const userInput = screen.getByTestId('user-input');
    expect(userInput).toHaveAttribute('data-selected-text', 'This is the selected text from the page');
  });

  test('error handling flow: network error -> display error message', async () => {
    const errorMessage = 'Network error occurred';
    mockAPIService.sendQueryWithValidation.mockRejectedValue(new Error(errorMessage));

    render(<Chatbot />);

    // Open chatbot
    const toggleButton = screen.getByLabelText('Open chatbot');
    fireEvent.click(toggleButton);

    // Enter query
    const messageInput = screen.getByTestId('message-input');
    fireEvent.change(messageInput, { target: { value: 'Test query that will fail' } });

    // Submit query
    fireEvent.change(messageInput, { target: { value: 'Test query that will fail' } });

    // Wait for error to be displayed
    await waitFor(() => {
      expect(screen.getByText(/Error:/i)).toBeInTheDocument();
    });

    expect(screen.getByText(new RegExp(errorMessage, 'i'))).toBeInTheDocument();
  });

  test('loading state flow: show loading indicator during API call', async () => {
    // Mock a delayed API response
    mockAPIService.sendQueryWithValidation.mockImplementation(() => {
      return new Promise((resolve) => {
        setTimeout(() => resolve({ answer: 'Delayed response' }), 100);
      });
    });

    render(<Chatbot />);

    // Open chatbot
    const toggleButton = screen.getByLabelText('Open chatbot');
    fireEvent.click(toggleButton);

    // Enter and submit query
    const messageInput = screen.getByTestId('message-input');
    fireEvent.change(messageInput, { target: { value: 'Delayed query' } });
    fireEvent.change(messageInput, { target: { value: 'Delayed query' } });

    // Verify loading state is shown
    expect(screen.getByTestId('loading-status')).toHaveTextContent('loading');

    // Wait for response to complete
    await waitFor(() => {
      expect(screen.getByTestId('loading-status')).toHaveTextContent('not loading');
    });

    // Verify response is displayed
    expect(screen.getByTestId('message-content')).toHaveTextContent('Delayed response');
  });

  test('session persistence flow: refresh maintains conversation history', async () => {
    // Mock localStorage
    const localStorageMock = (() => {
      let store = {};
      return {
        getItem: (key) => store[key] || null,
        setItem: (key, value) => {
          store[key] = value.toString();
        },
        removeItem: (key) => {
          delete store[key];
        },
        clear: () => {
          store = {};
        }
      };
    })();

    Object.defineProperty(window, 'localStorage', {
      value: localStorageMock,
      writable: true
    });

    const mockResponse = { answer: 'Session persistence test response' };
    mockAPIService.sendQueryWithValidation.mockResolvedValue(mockResponse);

    // First render - start a conversation
    const { rerender } = render(<Chatbot />);

    // Open chatbot
    const toggleButton = screen.getByLabelText('Open chatbot');
    fireEvent.click(toggleButton);

    // Send a message
    const messageInput = screen.getByTestId('message-input');
    fireEvent.change(messageInput, { target: { value: 'First message in session' } });
    fireEvent.change(messageInput, { target: { value: 'First message in session' } });

    // Wait for response
    await waitFor(() => {
      expect(mockAPIService.sendQueryWithValidation).toHaveBeenCalled();
    });

    // Verify session was saved to localStorage
    const savedSession = JSON.parse(localStorage.getItem('chatbot-session'));
    expect(savedSession).toBeDefined();
    expect(savedSession.messages).toHaveLength(2); // User + Assistant message

    // Simulate a "refresh" by creating a new component instance
    rerender(<Chatbot />);

    // The new instance should restore the session
    // Note: In a real scenario, we'd need to make the restored session visible
    // For this test, we'll verify the restoration logic by checking if the initial session
    // was properly created from localStorage
    expect(ChatSession).toHaveBeenCalledWith(
      expect.objectContaining({
        messages: expect.arrayContaining([
          expect.objectContaining({ content: 'First message in session' })
        ])
      })
    );
  });

  test('offline mode flow: service unavailable -> show offline message', async () => {
    // Set the service to offline
    mockAPIService.isOnline = false;
    mockAPIService.checkHealth.mockResolvedValue(false);

    render(<Chatbot />);

    // Open chatbot
    const toggleButton = screen.getByLabelText('Open chatbot');
    fireEvent.click(toggleButton);

    // Should show offline status
    expect(screen.getByText(/The AI service is currently unavailable/i)).toBeInTheDocument();

    // Input should be disabled
    const messageInput = screen.getByTestId('message-input');
    expect(messageInput).toBeDisabled();

    // Send button should be disabled
    const sendButton = screen.getByTestId('send-button');
    expect(sendButton).toBeDisabled();
  });

  test('complete conversation flow with multiple exchanges', async () => {
    const responses = [
      { answer: 'Response to first question', sources: ['source1'] },
      { answer: 'Response to second question', sources: ['source2'] },
      { answer: 'Response to third question', sources: ['source3'] }
    ];

    responses.forEach((response, index) => {
      mockAPIService.sendQueryWithValidation
        .mockResolvedValueOnce(response);
    });

    render(<Chatbot />);

    // Open chatbot
    const toggleButton = screen.getByLabelText('Open chatbot');
    fireEvent.click(toggleButton);

    // Send multiple queries in sequence
    const queries = [
      'What is the first question?',
      'What about the second question?',
      'And the third question?'
    ];

    for (let i = 0; i < queries.length; i++) {
      const messageInput = screen.getByTestId('message-input');
      fireEvent.change(messageInput, { target: { value: queries[i] } });
      fireEvent.change(messageInput, { target: { value: queries[i] } });

      await waitFor(() => {
        expect(mockAPIService.sendQueryWithValidation).toHaveBeenCalledTimes(i + 1);
      });
    }

    // Verify all messages are in the chat history
    await waitFor(() => {
      const messages = screen.getAllByTestId(/message-(user|assistant)/);
      // 3 user messages + 3 assistant responses = 6 total
      expect(messages).toHaveLength(6);
    });
  });
});