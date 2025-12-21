# RAG Chatbot Component

## Overview
This React component provides a chatbot interface that integrates with the RAG (Retrieval Augmented Generation) system. It allows users to ask questions about book content and receive contextually appropriate answers from the backend RAG system powered by Qdrant-stored embeddings and OpenAI Agent.

## Features
- Embedded chat interface on book pages
- Real-time communication with backend RAG API
- Support for selected text context
- Error handling and graceful degradation
- Responsive design for all screen sizes

## Setup

### Prerequisites
- Node.js 18+ and npm/yarn
- Docusaurus 3.x project
- Running backend API (FastAPI + OpenAI Agent + Qdrant)

### Environment Variables
Create a `.env` file in the root directory with the following configuration:

```env
CHATBOT_API_ENDPOINT=http://localhost:8000
```

### Installation
The component is integrated directly into the Docusaurus project and will be built with the site.

## Usage

### Component Props
The Chatbot component accepts the following props:

```javascript
<Chatbot
  pageContext={{
    url: string,           // Current page URL
    title: string          // Current page title
  }}
  config={{
    apiEndpoint: string,   // Backend API endpoint
    timeoutMs: number,     // Request timeout in milliseconds
    maxQueryLength: number // Maximum query length
  }}
  options={{
    showSources: boolean,     // Whether to show source information
    enableSelectedText: boolean // Whether to capture selected text
  }}
/>
```

## Development

### Running Tests
```bash
# Run all tests
npm run test

# Run tests in watch mode
npm run test:watch

# Generate coverage report
npm run test:coverage
```

### Available Scripts
- `npm run test`: Run Jest tests
- `npm run test:watch`: Run tests in watch mode
- `npm run test:coverage`: Generate coverage reports

## API Integration

The component communicates with the backend via these endpoints:
- POST `/api/agent/query` - Submit user queries
- GET `/health` - Check backend health status

## File Structure
```
src/components/Chatbot/
├── Chatbot.jsx          # Main chatbot container component
├── Chatbot.css          # Styling for the chatbot
├── ChatHistory.jsx      # Component for chat history display
├── Message.jsx          # Component for individual messages
├── UserInput.jsx        # Component for user input
├── chatbot-api.js       # API service for backend communication
├── data-model.js        # Data models for chat entities
└── text-selection.js    # Text selection utilities
```

## Testing Strategy
- Unit tests for individual components using React Testing Library
- Integration tests for API communication
- Component interaction tests

## Error Handling
- Network error detection and user feedback
- Graceful degradation when backend is unavailable
- Input validation and sanitization

## Security Considerations
- Input sanitization before display
- Secure communication with backend (HTTPS)
- No sensitive data stored in frontend

## Performance
- Minimal bundle size impact
- Optimized rendering for message lists
- Efficient state management
```