/**
 * Unit tests for the ChatHistory component
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { ChatHistory } from '../../book/src/components/Chatbot/ChatHistory';
import { Message } from '../../book/src/components/Chatbot/Message';

// Mock the Message component
jest.mock('../../book/src/components/Chatbot/Message', () => ({
  Message: ({ message, sender, content, sources, showSources }) => (
    <div data-testid={`message-${sender}`}>
      <div data-testid="message-content">{content}</div>
      <div data-testid="message-sender">{sender}</div>
      <div data-testid="message-sources">{sources?.join(', ') || 'no sources'}</div>
      <div data-testid="show-sources">{showSources ? 'show' : 'hide'}</div>
    </div>
  ),
}));

describe('ChatHistory Component', () => {
  const mockMessages = [
    {
      id: 'msg1',
      content: 'Hello there!',
      sender: 'user',
      timestamp: '2023-01-01T00:00:00Z',
    },
    {
      id: 'msg2',
      content: 'Hi, how can I help you?',
      sender: 'assistant',
      timestamp: '2023-01-01T00:00:01Z',
      sources: ['source1', 'source2'],
    },
  ];

  test('renders welcome message when no messages exist and not loading', () => {
    render(<ChatHistory messages={[]} isLoading={false} showSources={true} />);

    expect(screen.getByText(/Hello! I'm your AI assistant/i)).toBeInTheDocument();
  });

  test('does not render welcome message when loading', () => {
    render(<ChatHistory messages={[]} isLoading={true} showSources={true} />);

    expect(screen.queryByText(/Hello! I'm your AI assistant/i)).not.toBeInTheDocument();
  });

  test('renders loading indicator when isLoading is true', () => {
    render(<ChatHistory messages={[]} isLoading={true} showSources={true} />);

    expect(screen.getByText('Loading')).toBeInTheDocument();
  });

  test('does not render loading indicator when not loading', () => {
    render(<ChatHistory messages={[]} isLoading={false} showSources={true} />);

    expect(screen.queryByText('Loading')).not.toBeInTheDocument();
  });

  test('renders all messages in the history', () => {
    render(<ChatHistory messages={mockMessages} isLoading={false} showSources={true} />);

    // Should render 2 messages
    const userMessages = screen.getAllByTestId('message-user');
    const assistantMessages = screen.getAllByTestId('message-assistant');

    expect(userMessages).toHaveLength(1);
    expect(assistantMessages).toHaveLength(1);
  });

  test('passes correct props to Message components', () => {
    render(<ChatHistory messages={mockMessages} isLoading={false} showSources={true} />);

    const messageElements = screen.getAllByTestId(/message-(user|assistant)/);

    expect(messageElements).toHaveLength(2);

    // Check first message (user)
    expect(screen.getByTestId('message-user')).toBeInTheDocument();
    expect(screen.getByTestId('message-content')).toHaveTextContent('Hello there!');
    expect(screen.getByTestId('message-sender')).toHaveTextContent('user');

    // Check second message (assistant)
    expect(screen.getByTestId('message-assistant')).toBeInTheDocument();
  });

  test('passes showSources prop to Message components', () => {
    render(<ChatHistory messages={mockMessages} isLoading={false} showSources={false} />);

    const messageElements = screen.getAllByTestId('show-sources');
    messageElements.forEach(element => {
      expect(element).toHaveTextContent('hide');
    });
  });

  test('renders sources when provided in assistant message', () => {
    render(<ChatHistory messages={mockMessages} isLoading={false} showSources={true} />);

    // The assistant message has sources
    expect(screen.getByTestId('message-sources')).toHaveTextContent('source1, source2');
  });

  test('renders empty sources when none provided in user message', () => {
    render(<ChatHistory messages={mockMessages} isLoading={false} showSources={true} />);

    // The user message has no sources
    const userMessageSources = screen.getByTestId('message-sources');
    expect(userMessageSources).toHaveTextContent('no sources');
  });

  test('renders correctly with empty messages array', () => {
    render(<ChatHistory messages={[]} isLoading={false} showSources={true} />);

    // Should show welcome message
    expect(screen.getByText(/Hello! I'm your AI assistant/i)).toBeInTheDocument();
  });

  test('renders correctly with many messages', () => {
    const manyMessages = Array.from({ length: 10 }, (_, i) => ({
      id: `msg${i}`,
      content: `Message ${i}`,
      sender: i % 2 === 0 ? 'user' : 'assistant',
      timestamp: `2023-01-01T00:00:0${i}Z`,
    }));

    render(<ChatHistory messages={manyMessages} isLoading={false} showSources={true} />);

    // Should render all 10 messages
    const allMessages = screen.getAllByTestId(/message-(user|assistant)/);
    expect(allMessages).toHaveLength(10);
  });

  test('renders loading state with existing messages', () => {
    render(<ChatHistory messages={mockMessages} isLoading={true} showSources={true} />);

    // Should render messages and loading indicator
    expect(screen.getByTestId('message-user')).toBeInTheDocument();
    expect(screen.getByText('Loading')).toBeInTheDocument();
  });
});