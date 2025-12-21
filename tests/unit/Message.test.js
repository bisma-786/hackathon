/**
 * Unit tests for the Message component
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { Message } from '../../book/src/components/Chatbot/Message';

describe('Message Component', () => {
  test('renders user message with correct styling', () => {
    render(
      <Message
        message={{ id: '1', sender: 'user' }}
        sender="user"
        content="Hello, this is a user message"
      />
    );

    const messageElement = screen.getByRole('listitem');
    expect(messageElement).toHaveClass('message-user');
    expect(screen.getByText('Hello, this is a user message')).toBeInTheDocument();
  });

  test('renders assistant message with correct styling', () => {
    render(
      <Message
        message={{ id: '2', sender: 'assistant' }}
        sender="assistant"
        content="Hello, this is an assistant message"
      />
    );

    const messageElement = screen.getByRole('listitem');
    expect(messageElement).toHaveClass('message-assistant');
    expect(screen.getByText('Hello, this is an assistant message')).toBeInTheDocument();
  });

  test('renders sources when provided and showSources is true', () => {
    const sources = ['source1', 'source2', 'source3'];

    render(
      <Message
        message={{ id: '3', sender: 'assistant' }}
        sender="assistant"
        content="Assistant response"
        sources={sources}
        showSources={true}
      />
    );

    sources.forEach(source => {
      expect(screen.getByText(source)).toBeInTheDocument();
    });
  });

  test('does not render sources when showSources is false', () => {
    render(
      <Message
        message={{ id: '4', sender: 'assistant' }}
        sender="assistant"
        content="Assistant response"
        sources={['source1', 'source2']}
        showSources={false}
      />
    );

    expect(screen.queryByText('Sources:')).not.toBeInTheDocument();
  });

  test('does not render sources when sources array is empty', () => {
    render(
      <Message
        message={{ id: '5', sender: 'assistant' }}
        sender="assistant"
        content="Assistant response"
        sources={[]}
        showSources={true}
      />
    );

    expect(screen.queryByText('Sources:')).not.toBeInTheDocument();
  });

  test('renders confidence indicator for assistant messages with confidence score', () => {
    render(
      <Message
        message={{ id: '6', sender: 'assistant' }}
        sender="assistant"
        content="Assistant response"
        confidence={0.85}
      />
    );

    expect(screen.getByText('High confidence (85%)')).toBeInTheDocument();
    expect(screen.getByText('High confidence (85%)')).toHaveClass('confidence-high');
  });

  test('does not render confidence indicator for user messages', () => {
    render(
      <Message
        message={{ id: '7', sender: 'user' }}
        sender="user"
        content="User message"
        confidence={0.85}
      />
    );

    expect(screen.queryByText(/confidence/i)).not.toBeInTheDocument();
  });

  test('renders medium confidence text and styling', () => {
    render(
      <Message
        message={{ id: '8', sender: 'assistant' }}
        sender="assistant"
        content="Assistant response"
        confidence={0.65}
      />
    );

    expect(screen.getByText('Medium confidence (65%)')).toBeInTheDocument();
    expect(screen.getByText('Medium confidence (65%)')).toHaveClass('confidence-medium');
  });

  test('renders low confidence text and styling', () => {
    render(
      <Message
        message={{ id: '9', sender: 'assistant' }}
        sender="assistant"
        content="Assistant response"
        confidence={0.35}
      />
    );

    expect(screen.getByText('Low confidence (35%)')).toBeInTheDocument();
    expect(screen.getByText('Low confidence (35%)')).toHaveClass('confidence-low');
  });

  test('renders follow-up questions when provided', () => {
    const followupQuestions = ['Question 1', 'Question 2', 'Question 3'];

    render(
      <Message
        message={{ id: '10', sender: 'assistant' }}
        sender="assistant"
        content="Assistant response"
        followupQuestions={followupQuestions}
      />
    );

    expect(screen.getByText('Related questions:')).toBeInTheDocument();

    followupQuestions.forEach(question => {
      expect(screen.getByText(question)).toBeInTheDocument();
    });
  });

  test('does not render follow-up questions when not provided', () => {
    render(
      <Message
        message={{ id: '11', sender: 'assistant' }}
        sender="assistant"
        content="Assistant response"
      />
    );

    expect(screen.queryByText('Related questions:')).not.toBeInTheDocument();
  });

  test('does not render follow-up questions when empty array', () => {
    render(
      <Message
        message={{ id: '12', sender: 'assistant' }}
        sender="assistant"
        content="Assistant response"
        followupQuestions={[]}
      />
    );

    expect(screen.queryByText('Related questions:')).not.toBeInTheDocument();
  });

  test('applies error styling when message status is error', () => {
    render(
      <Message
        message={{ id: '13', sender: 'assistant', status: 'error' }}
        sender="assistant"
        content="Error message"
      />
    );

    const messageElement = screen.getByRole('listitem');
    expect(messageElement).toHaveClass('message-error');
  });

  test('does not apply error styling when message status is not error', () => {
    render(
      <Message
        message={{ id: '14', sender: 'assistant', status: 'sent' }}
        sender="assistant"
        content="Normal message"
      />
    );

    const messageElement = screen.getByRole('listitem');
    expect(messageElement).not.toHaveClass('message-error');
  });

  test('renders content correctly', () => {
    const content = "This is the message content that should be displayed";

    render(
      <Message
        message={{ id: '15', sender: 'user' }}
        sender="user"
        content={content}
      />
    );

    expect(screen.getByText(content)).toBeInTheDocument();
  });

  test('handles content with special characters', () => {
    const content = "Message with special chars: !@#$%^&*()";

    render(
      <Message
        message={{ id: '16', sender: 'assistant' }}
        sender="assistant"
        content={content}
      />
    );

    expect(screen.getByText(content)).toBeInTheDocument();
  });

  test('renders with default showSources as true', () => {
    // This tests that when showSources is not provided, it defaults to true
    // and sources should be shown if they exist
    render(
      <Message
        message={{ id: '17', sender: 'assistant' }}
        sender="assistant"
        content="Assistant response"
        sources={['default-source']}
        // showSources not provided, should default to true
      />
    );

    expect(screen.getByText('default-source')).toBeInTheDocument();
  });
});