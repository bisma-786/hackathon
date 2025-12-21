# Quickstart Guide: Frontend Integration of RAG Chatbot

## Overview
This guide provides instructions for integrating the RAG chatbot component into the Docusaurus book frontend. The chatbot enables readers to ask questions about book content and receive contextually appropriate answers from the backend RAG system.

## Prerequisites

- Node.js 18+ and npm/yarn
- Docusaurus 3.x project (the book project)
- Running backend API (FastAPI + OpenAI Agent + Qdrant) from previous specs
- Basic knowledge of React and Docusaurus customization

## Setup Instructions

### 1. Install Dependencies
First, navigate to your book directory and install any required dependencies:

```bash
cd book  # or wherever your Docusaurus project is located
npm install  # or yarn install
```

### 2. Create Chatbot Component Directory
Create the directory structure for the chatbot component:

```bash
mkdir -p src/components/Chatbot
```

### 3. Add Environment Configuration
Update your `docusaurus.config.js` to include environment-specific API configuration:

```javascript
// In docusaurus.config.js
module.exports = {
  // ... existing config
  themeConfig: {
    // ... existing theme config
  },
  // Add custom fields for chatbot configuration
  customFields: {
    chatbot: {
      apiEndpoint: process.env.REACT_APP_CHATBOT_API_ENDPOINT || 'http://localhost:8000',
      enabled: process.env.REACT_APP_CHATBOT_ENABLED !== 'false',
    }
  }
};
```

### 4. Create Chatbot Components
Create the following files in the `src/components/Chatbot/` directory:

**Chatbot.jsx** - Main chatbot container component
**ChatHistory.jsx** - Component to display conversation history
**Message.jsx** - Component for individual messages
**UserInput.jsx** - Component for user input area
**chatbot-api.js** - API service for backend communication

### 5. Environment Variables
Create or update your `.env` file in the book directory:

```env
# API endpoint for the backend RAG service
REACT_APP_CHATBOT_API_ENDPOINT=https://your-backend-api.com

# Toggle to enable/disable the chatbot
REACT_APP_CHATBOT_ENABLED=true

# Optional: API key if required (note: frontend keys are not secure)
# REACT_APP_CHATBOT_API_KEY=your-api-key
```

## Integration with Book Pages

### 1. Import and Use Component
To add the chatbot to specific pages, import the component:

```jsx
import Chatbot from '@site/src/components/Chatbot/Chatbot';

// In your page component
function MyPage() {
  return (
    <div>
      <h1>My Book Content</h1>
      {/* Your existing content */}
      <Chatbot pageContext={{ url: location.pathname, title: 'Current Page Title' }} />
    </div>
  );
}
```

### 2. Global Integration
To add the chatbot to all pages, modify your theme:

```jsx
// In src/theme/Layout/index.js
import Chatbot from '@site/src/components/Chatbot/Chatbot';

export default function Layout(props) {
  return (
    <>
      <OriginalLayout {...props} />
      <Chatbot pageContext={{ url: location.pathname, title: 'Current Page' }} />
    </>
  );
}
```

## Configuration Options

The chatbot component accepts the following props:

```jsx
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

## API Communication

The chatbot communicates with the existing FastAPI backend endpoints:

- Query endpoint: `POST /api/agent/query`
- Health check: `GET /health`

The component will automatically handle:
- Request/response serialization
- Error handling
- Loading states
- Session management

## Testing the Integration

### 1. Development Server
Start the Docusaurus development server:

```bash
cd book
npm run start
```

### 2. Verify Backend Connection
Check that the backend API is accessible:
- Navigate to your backend health endpoint: `http://localhost:8000/health`
- Ensure you get a healthy response

### 3. Test Chat Functionality
- Visit any book page with the chatbot component
- Type a question related to the book content
- Verify that you receive a response from the backend
- Test with selected text to ensure context capture works

## Troubleshooting

### Common Issues

**Issue**: Chatbot not appearing on pages
- **Solution**: Verify that the component is properly imported and added to your page/layout

**Issue**: API requests failing
- **Solution**: Check that the backend is running and the API endpoint is correctly configured

**Issue**: Selected text not being captured
- **Solution**: Ensure the page has selectable text and the selection capture feature is enabled

**Issue**: CORS errors
- **Solution**: Configure your backend to allow requests from your frontend origin

### Debugging
Enable React Developer Tools to inspect the component state and props.
Check browser console for JavaScript errors.
Verify network requests in browser dev tools.

## Next Steps

1. Customize the chatbot styling to match your book's design
2. Add analytics to track user interactions
3. Implement additional features like chat history persistence
4. Add accessibility enhancements
5. Set up production environment configuration