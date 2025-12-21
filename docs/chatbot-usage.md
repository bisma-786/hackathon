# Chatbot Usage Guide

This document provides usage examples and guidelines for the RAG (Retrieval Augmented Generation) chatbot component integrated into the Docusaurus-based textbook.

## Table of Contents
- [Overview](#overview)
- [Basic Usage](#basic-usage)
- [Features](#features)
- [Configuration Options](#configuration-options)
- [Accessibility Features](#accessibility-features)
- [Troubleshooting](#troubleshooting)

## Overview

The RAG chatbot is a React-based component that allows users to ask questions about book content and receive contextually appropriate answers from a backend RAG system powered by Qdrant-stored embeddings and OpenAI Agent.

## Basic Usage

The chatbot is automatically integrated into all documentation pages through the Docusaurus theme configuration. Users can interact with it using the floating chat button in the bottom-right corner of the screen.

### Opening the Chatbot
1. Click the chat icon in the bottom-right corner of any page
2. The chat interface will slide in from the right
3. Type your question in the input field at the bottom
4. Press Enter or click the send button to submit

### Asking Questions
- Type your question in the input field at the bottom of the chat interface
- Press Enter or click the send button to submit
- The AI assistant will process your question and provide a response
- Responses include sources and confidence indicators when available

## Features

### Text Selection
1. Select text on any page by dragging your cursor over the content
2. The selected text will appear in the chat input field
3. You can ask questions specifically about the selected text
4. The context of the selected text is sent to the backend for more targeted responses

### Source Attribution
- Responses include source references when available
- Sources are displayed below the answer
- Click on sources to navigate to relevant content

### Confidence Indicators
- Responses include confidence scores (High, Medium, Low)
- Color-coded indicators help assess response reliability
- High confidence (green): 80%+ confidence in accuracy
- Medium confidence (yellow): 50-79% confidence in accuracy
- Low confidence (red): Below 50% confidence in accuracy

### Follow-up Questions
- Responses may include suggested follow-up questions
- Click on suggested questions to continue the conversation
- Follow-up questions are contextually relevant to the current topic

### Offline Handling
- When the backend service is unavailable, the chatbot shows an offline status
- Input is disabled when the service is offline
- Users receive appropriate feedback when service is unavailable

## Configuration Options

The chatbot can be configured through the Docusaurus theme configuration:

```javascript
themeConfig: {
  chatbot: {
    enabled: true,                 // Enable/disable the chatbot
    apiEndpoint: process.env.CHATBOT_API_ENDPOINT || 'http://localhost:8000',  // Backend API endpoint
    showOnDocPages: true,          // Show on documentation pages
    showOnBlogPages: false,        // Show on blog pages
    showOnNonDocPages: false,      // Show on other pages (homepage, etc.)
    showSources: true,             // Show source attribution
    enableSelectedText: true       // Enable text selection feature
  }
}
```

### Environment Variables

The following environment variables can be set:

- `CHATBOT_API_ENDPOINT`: Backend API endpoint URL
- `CHATBOT_TIMEOUT_MS`: Request timeout in milliseconds (default: 30000)

## Accessibility Features

The chatbot includes several accessibility features:

### Keyboard Navigation
- **Ctrl/Cmd + K**: Focus the chat input field
- **Ctrl/Cmd + Shift + K**: Toggle chatbot visibility
- **Escape**: Close the chatbot when open
- **Tab**: Navigate between interactive elements
- **Enter**: Submit messages (Shift+Enter for new line)

### Screen Reader Support
- All interactive elements have appropriate ARIA labels
- Live regions announce new messages
- Status changes are announced to screen readers
- Semantic HTML structure for proper navigation

### Reduced Motion
- Animations are disabled for users who prefer reduced motion
- Smooth transitions respect user preferences

## Troubleshooting

### Common Issues

**Q: The chatbot button doesn't appear on some pages**
A: Check the `docusaurus.config.js` chatbot configuration. Ensure the page type is enabled in `showOnDocPages`, `showOnBlogPages`, or `showOnNonDocPages`.

**Q: I get "Unable to connect to the backend service" error**
A:
1. Verify the `CHATBOT_API_ENDPOINT` is correctly configured
2. Check that the backend service is running and accessible
3. Ensure there are no network connectivity issues

**Q: Selected text doesn't appear in the chat input**
A:
1. Make sure `enableSelectedText` is set to `true` in the configuration
2. Select text by dragging your cursor over the content
3. The chatbot must be open for selected text to be captured

**Q: Responses are taking too long**
A:
1. Check your internet connection
2. The backend service may be experiencing high load
3. Try again after a few moments

### Performance Tips

- Keep questions concise and specific for better results
- Use the text selection feature for context-specific questions
- Check confidence indicators to assess response reliability
- Use follow-up questions to continue relevant discussions

## API Endpoints Used

The chatbot communicates with the following backend endpoints:

- `POST /api/agent/query` - Send user queries and receive responses
- `GET /health` - Check backend service health status

## Security Considerations

- User inputs are sanitized before being sent to the backend
- Selected text is validated and sanitized
- All responses are validated before display
- The component follows React security best practices