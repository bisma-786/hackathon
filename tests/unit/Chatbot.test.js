/**
 * Unit tests for the Chatbot component
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { act } from 'react-dom/test-utils';
import { Chatbot } from '../../book/src/components/Chatbot/Chatbot';
import { ChatMessage, ChatSession, APIRequest, ChatbotConfig } from '../../book/src/components/Chatbot/data-model';
import { createChatbotAPIService } from '../../book/src/components/Chatbot/chatbot-api';

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
  ChatbotConfig: jest.fn(),
}));

// Mock the child components
jest.mock('../../book/src/components/Chatbot/ChatHistory', () => ({
  ChatHistory: ({ messages, isLoading, showSources }) => (
    <div data-testid="chat-history">
      <div>Chat History</div>
      <div data-testid="messages-count">{messages.length}</div>
      <div data-testid="loading-status">{isLoading ? 'loading' : 'not loading'}</div>
      <div data-testid="show-sources">{showSources ? 'show' : 'hide'}</div>
    </div>
  ),
}));

jest.mock('../../book/src/components/Chatbot/UserInput', () => ({
  UserInput: ({ onSendMessage, isLoading, selectedText, maxQueryLength }) => (
    <div data-testid="user-input">
      <input
        data-testid="message-input"
        onChange={(e) => onSendMessage(e.target.value)}
        disabled={isLoading}
        placeholder="Type your message..."
        maxLength={maxQueryLength}
      />
      <div data-testid="selected-text">{selectedText}</div>
      <div data-testid="max-length">{maxQueryLength}</div>
    </div>
  ),
}));

describe('Chatbot Component', () => {
  const mockAPIService = {
    sendQueryWithValidation: jest.fn(),
    startConnectionMonitoring: jest.fn(),
    stopConnectionMonitoring: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    createChatbotAPIService.mockReturnValue(mockAPIService);

    // Mock the data model constructors
    ChatMessage.mockImplementation((props) => ({ id: `msg_${Date.now()}`, ...props }));
    ChatSession.mockImplementation((props) => ({ id: `session_${Date.now()}`, messages: [], ...props }));
    APIRequest.mockImplementation((props) => ({ query: '', ...props }));
    ChatbotConfig.mockImplementation((props) => ({ apiEndpoint: 'http://localhost:8000', ...props }));
  });

  test('renders chatbot toggle button when not visible', () => {
    render(<Chatbot />);

    // Initially, the chatbot should be hidden, so we should see the toggle button
    const toggleButton = screen.getByLabelText('Open chatbot');
    expect(toggleButton).toBeInTheDocument();
  });

  test('renders chatbot container when visible', () => {
    render(<Chatbot />);

    // Click the toggle button to make chatbot visible
    const toggleButton = screen.getByLabelText('Open chatbot');
    fireEvent.click(toggleButton);

    // Now we should see the chatbot container
    expect(screen.getByLabelText('AI Assistant Chatbot')).toBeInTheDocument();
  });

  test('toggles visibility when toggle button is clicked', () => {
    render(<Chatbot />);

    const toggleButton = screen.getByLabelText('Open chatbot');

    // Initially hidden
    expect(screen.getByLabelText('Open chatbot')).toBeInTheDocument();

    // Click to show
    fireEvent.click(toggleButton);

    // Now should see the chatbot container
    expect(screen.getByLabelText('AI Assistant Chatbot')).toBeInTheDocument();

    // Click close button to hide
    const closeButton = screen.getByLabelText('Close chatbot');
    fireEvent.click(closeButton);

    // Should be back to toggle button
    expect(screen.getByLabelText('Open chatbot')).toBeInTheDocument();
  });

  test('sends query to API service when message is submitted', async () => {
    const mockResponse = {
      answer: 'This is a test response',
      sources: ['source1', 'source2'],
      confidence: 0.9
    };

    mockAPIService.sendQueryWithValidation.mockResolvedValue(mockResponse);

    render(<Chatbot />);

    // Make chatbot visible
    const toggleButton = screen.getByLabelText('Open chatbot');
    fireEvent.click(toggleButton);

    // Find the input and submit a message
    const messageInput = screen.getByTestId('message-input');
    fireEvent.change(messageInput, { target: { value: 'Test query' } });

    // Simulate sending the message (the actual sending happens in UserInput)
    fireEvent.change(messageInput, { target: { value: 'Test query' } });

    // Wait for the API call
    await waitFor(() => {
      expect(mockAPIService.sendQueryWithValidation).toHaveBeenCalled();
    });
  });

  test('shows error message when query fails', async () => {
    const errorMessage = 'Network error';
    mockAPIService.sendQueryWithValidation.mockRejectedValue(new Error(errorMessage));

    render(<Chatbot />);

    // Make chatbot visible
    const toggleButton = screen.getByLabelText('Open chatbot');
    fireEvent.click(toggleButton);

    // Find the input and submit a message
    const messageInput = screen.getByTestId('message-input');
    fireEvent.change(messageInput, { target: { value: 'Test query' } });

    // Wait for the error to be displayed
    await waitFor(() => {
      expect(screen.getByText(/Error:/i)).toBeInTheDocument();
    });
  });

  test('starts connection monitoring on mount', () => {
    render(<Chatbot />);

    expect(mockAPIService.startConnectionMonitoring).toHaveBeenCalledWith(30000);
  });

  test('stops connection monitoring on unmount', () => {
    const { unmount } = render(<Chatbot />);

    unmount();

    expect(mockAPIService.stopConnectionMonitoring).toHaveBeenCalled();
  });

  test('handles selected text from props', () => {
    const selectedText = 'This is selected text';
    render(<Chatbot options={{ enableSelectedText: true }} />);

    // Make chatbot visible
    const toggleButton = screen.getByLabelText('Open chatbot');
    fireEvent.click(toggleButton);

    // Check that selected text is passed to UserInput
    expect(screen.getByTestId('selected-text')).toHaveTextContent(selectedText);
  });

  test('applies custom configuration', () => {
    const customConfig = {
      apiEndpoint: 'http://custom-api:8000',
      timeoutMs: 60000,
      maxQueryLength: 2000
    };

    render(<Chatbot config={customConfig} />);

    // Make chatbot visible
    const toggleButton = screen.getByLabelText('Open chatbot');
    fireEvent.click(toggleButton);

    // Check that custom config is used
    expect(screen.getByTestId('max-length')).toHaveTextContent('2000');
  });

  test('shows welcome message when no messages exist', () => {
    render(<Chatbot />);

    // Make chatbot visible
    const toggleButton = screen.getByLabelText('Open chatbot');
    fireEvent.click(toggleButton);

    expect(screen.getByTestId('messages-count')).toHaveTextContent('0');
  });

  test('disables input when loading', async () => {
    mockAPIService.sendQueryWithValidation.mockImplementation(() => {
      return new Promise((resolve) => {
        setTimeout(() => resolve({ answer: 'response', sources: [], confidence: 0.8 }), 100);
      });
    });

    render(<Chatbot />);

    // Make chatbot visible
    const toggleButton = screen.getByLabelText('Open chatbot');
    fireEvent.click(toggleButton);

    // Find the input and submit a message
    const messageInput = screen.getByTestId('message-input');
    fireEvent.change(messageInput, { target: { value: 'Test query' } });

    // Input should be disabled during loading
    expect(messageInput).toBeDisabled();
  });
});