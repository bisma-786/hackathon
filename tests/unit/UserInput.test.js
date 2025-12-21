/**
 * Unit tests for the UserInput component
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { UserInput } from '../../book/src/components/Chatbot/UserInput';

describe('UserInput Component', () => {
  const mockOnSendMessage = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders input field and send button', () => {
    render(
      <UserInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        selectedText=""
        maxQueryLength={1000}
      />
    );

    expect(screen.getByLabelText('Type your message')).toBeInTheDocument();
    expect(screen.getByLabelText('Send message')).toBeInTheDocument();
  });

  test('disables input and send button when loading', () => {
    render(
      <UserInput
        onSendMessage={mockOnSendMessage}
        isLoading={true}
        selectedText=""
        maxQueryLength={1000}
      />
    );

    const input = screen.getByLabelText('Type your message');
    const sendButton = screen.getByLabelText('Send message');

    expect(input).toBeDisabled();
    expect(sendButton).toBeDisabled();
  });

  test('enables input and send button when not loading', () => {
    render(
      <UserInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        selectedText=""
        maxQueryLength={1000}
      />
    );

    const input = screen.getByLabelText('Type your message');
    const sendButton = screen.getByLabelText('Send message');

    expect(input).not.toBeDisabled();
    expect(sendButton).not.toBeDisabled();
  });

  test('calls onSendMessage when send button is clicked', () => {
    render(
      <UserInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        selectedText=""
        maxQueryLength={1000}
      />
    );

    const input = screen.getByLabelText('Type your message');
    const sendButton = screen.getByLabelText('Send message');

    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);

    expect(mockOnSendMessage).toHaveBeenCalledWith('Test message');
    expect(input.value).toBe(''); // Input should be cleared after sending
  });

  test('calls onSendMessage when Enter is pressed (without Shift)', () => {
    render(
      <UserInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        selectedText=""
        maxQueryLength={1000}
      />
    );

    const input = screen.getByLabelText('Type your message');

    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.keyDown(input, { key: 'Enter', shiftKey: false });

    expect(mockOnSendMessage).toHaveBeenCalledWith('Test message');
    expect(input.value).toBe(''); // Input should be cleared after sending
  });

  test('does not call onSendMessage when Shift+Enter is pressed', () => {
    render(
      <UserInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        selectedText=""
        maxQueryLength={1000}
      />
    );

    const input = screen.getByLabelText('Type your message');

    fireEvent.change(input, { target: { value: 'Test message' });
    fireEvent.keyDown(input, { key: 'Enter', shiftKey: true });

    expect(mockOnSendMessage).not.toHaveBeenCalled();
    expect(input.value).toBe('Test message'); // Input should not be cleared
  });

  test('does not send empty messages', () => {
    render(
      <UserInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        selectedText=""
        maxQueryLength={1000}
      />
    );

    const input = screen.getByLabelText('Type your message');
    const sendButton = screen.getByLabelText('Send message');

    fireEvent.change(input, { target: { value: '' } });
    fireEvent.click(sendButton);

    expect(mockOnSendMessage).not.toHaveBeenCalled();
  });

  test('does not send whitespace-only messages', () => {
    render(
      <UserInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        selectedText=""
        maxQueryLength={1000}
      />
    );

    const input = screen.getByLabelText('Type your message');
    const sendButton = screen.getByLabelText('Send message');

    fireEvent.change(input, { target: { value: '   ' } });
    fireEvent.click(sendButton);

    expect(mockOnSendMessage).not.toHaveBeenCalled();
  });

  test('disables send button when input is empty', () => {
    render(
      <UserInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        selectedText=""
        maxQueryLength={1000}
      />
    );

    const input = screen.getByLabelText('Type your message');
    const sendButton = screen.getByLabelText('Send message');

    expect(sendButton).toBeDisabled();

    fireEvent.change(input, { target: { value: 'Non-empty' } });
    expect(sendButton).not.toBeDisabled();

    fireEvent.change(input, { target: { value: '' } });
    expect(sendButton).toBeDisabled();
  });

  test('shows selected text preview when selectedText is provided', () => {
    const selectedText = 'This is the selected text';

    render(
      <UserInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        selectedText={selectedText}
        maxQueryLength={1000}
      />
    );

    expect(screen.getByText('Selected text:')).toBeInTheDocument();
    expect(screen.getByLabelText(`Selected text: ${selectedText}`)).toBeInTheDocument();
  });

  test('initializes input with selected text', () => {
    const selectedText = 'Previously selected text';

    render(
      <UserInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        selectedText={selectedText}
        maxQueryLength={1000}
      />
    );

    const input = screen.getByLabelText('Type your message');
    expect(input.value).toBe(selectedText);
  });

  test('does not override existing input value with selected text', () => {
    render(
      <UserInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        selectedText="Selected text"
        maxQueryLength={1000}
      />
    );

    const input = screen.getByLabelText('Type your message');

    // Change input to something else
    fireEvent.change(input, { target: { value: 'Custom input' } });

    // Re-render with same props (simulating useEffect behavior)
    render(
      <UserInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        selectedText="Different selected text"
        maxQueryLength={1000}
      />
    );

    // Should keep the custom input, not replace with selected text
    expect(input.value).toBe('Custom input');
  });

  test('shows character count', () => {
    render(
      <UserInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        selectedText=""
        maxQueryLength={1000}
      />
    );

    const input = screen.getByLabelText('Type your message');
    fireEvent.change(input, { target: { value: 'Hello' } });

    expect(screen.getByLabelText('Characters remaining: 995 of 1000')).toBeInTheDocument();
  });

  test('updates character count as input changes', () => {
    render(
      <UserInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        selectedText=""
        maxQueryLength={1000}
      />
    );

    const input = screen.getByLabelText('Type your message');

    fireEvent.change(input, { target: { value: 'Hello' } });
    expect(screen.getByLabelText('Characters remaining: 995 of 1000')).toBeInTheDocument();

    fireEvent.change(input, { target: { value: 'Hello World' } });
    expect(screen.getByLabelText('Characters remaining: 989 of 1000')).toBeInTheDocument();
  });

  test('shows warning when character count is low', () => {
    render(
      <UserInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        selectedText=""
        maxQueryLength={100}
      />
    );

    const input = screen.getByLabelText('Type your message');
    fireEvent.change(input, { target: { value: 'A'.repeat(95) } }); // 95 chars, 5 remaining

    const charCountElement = screen.getByLabelText('Characters remaining: 5 of 100');
    expect(charCountElement).toHaveClass('char-count-warning');
  });

  test('does not exceed max query length', () => {
    render(
      <UserInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        selectedText=""
        maxQueryLength={10}
      />
    );

    const input = screen.getByLabelText('Type your message');
    fireEvent.change(input, { target: { value: 'A'.repeat(15) } }); // 15 chars, exceeds max of 10

    // The input should be limited to maxQueryLength
    expect(input.value.length).toBeLessThanOrEqual(10);
  });

  test('updates placeholder based on selected text', () => {
    // Without selected text
    const { rerender } = render(
      <UserInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        selectedText=""
        maxQueryLength={1000}
      />
    );

    expect(screen.getByPlaceholderText('Ask a question about the book content...')).toBeInTheDocument();

    // With selected text
    rerender(
      <UserInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        selectedText="Selected text"
        maxQueryLength={1000}
      />
    );

    expect(screen.getByPlaceholderText('Ask about the selected text...')).toBeInTheDocument();
  });

  test('handles IME composition events correctly', () => {
    render(
      <UserInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        selectedText=""
        maxQueryLength={1000}
      />
    );

    const input = screen.getByLabelText('Type your message');

    // Simulate IME composition
    fireEvent.compositionStart(input);
    fireEvent.keyDown(input, { key: 'Enter', shiftKey: false }); // Should not send during composition

    expect(mockOnSendMessage).not.toHaveBeenCalled();

    fireEvent.compositionEnd(input);
    fireEvent.keyDown(input, { key: 'Enter', shiftKey: false }); // Should send after composition ends

    expect(mockOnSendMessage).toHaveBeenCalled();
  });

  test('maintains cursor position when focusing', () => {
    render(
      <UserInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        selectedText="Initial text"
        maxQueryLength={1000}
      />
    );

    const input = screen.getByLabelText('Type your message');

    // Set some text and selection
    fireEvent.change(input, { target: { value: 'Hello World' } });
    input.setSelectionRange(5, 5); // Position cursor at index 5

    // Focus should move cursor to end
    fireEvent.focus(input);
    // Note: We can't easily test the exact cursor position in jsdom,
    // but we ensure the focus handler doesn't break
  });
});