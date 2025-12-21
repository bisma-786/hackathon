# API Contract: Frontend Integration of RAG Chatbot

## Overview
This contract defines the API interactions between the frontend chatbot component and the backend RAG system. The frontend will use existing FastAPI endpoints that are already implemented as part of the backend system.

## Base URL
The base URL will be configured through environment variables and will vary by deployment environment:
- Development: `http://localhost:8000`
- Production: `[Configurable via environment]`

## Authentication
API key authentication via `Authorization: Bearer {API_KEY}` header (if required by deployment)

## Common Headers
- `Content-Type: application/json`
- `Accept: application/json`

## Endpoints

### 1. Agent Query Endpoint (Existing Backend Endpoint)
**POST** `/api/agent/query`

#### Description
Process a natural language query through the OpenAI agent with retrieved context from Qdrant. This endpoint already exists from the backend implementation.

#### Request
```json
{
  "query": "What are the key principles of embodied cognition in robotics?",
  "context": {
    "selected_text": "embodied cognition principles",
    "page_url": "https://example.com/textbook/module3"
  },
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 500
  }
}
```

#### Response (Success - 200 OK)
```json
{
  "answer": "Embodied cognition in robotics emphasizes that cognitive processes emerge from the interaction between an agent's body, its environment, and its control system...",
  "sources": ["vector_123", "vector_456", "vector_789"],
  "confidence": 0.85,
  "retrieved_context": [
    {
      "id": "vector_123",
      "content": "Embodied cognition is the theory that cognitive processes are deeply rooted in the body's interactions with the world...",
      "similarity_score": 0.92,
      "metadata": {
        "url": "https://example.com/textbook/module3",
        "module": "embodied_cognition",
        "section": "introduction",
        "position": 0
      }
    }
  ],
  "followup_questions": [
    "How does this relate to sensorimotor contingencies?",
    "What are practical implementations of these principles?"
  ]
}
```

#### Response (Error - 400 Bad Request)
```json
{
  "status": "error",
  "data": null,
  "metadata": {
    "request_id": "req_abc123",
    "timestamp": "2025-12-21T10:30:00Z",
    "execution_time": 0.01
  },
  "errors": [
    {
      "code": "INVALID_QUERY",
      "message": "Query must be non-empty and less than 1000 characters",
      "details": {
        "field": "query",
        "value": ""
      }
    }
  ]
}
```

#### Error Responses
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Missing or invalid API key
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server-side error during processing

---

### 2. Health Check Endpoint (Existing Backend Endpoint)
**GET** `/health`

#### Description
Check the health status of the backend API service.

#### Response (Success - 200 OK)
```json
{
  "status": "healthy",
  "message": "AI-Driven Robotics Textbook RAG API is running"
}
```

#### Error Responses
- `503 Service Unavailable`: Backend services are not available

---

## Frontend-to-Backend Data Flow

### Query Request Structure
When a user submits a query in the chatbot:

1. **Frontend captures**:
   - User's question/query text
   - Any selected text on the current page
   - Current page URL and context

2. **Frontend formats request**:
   ```json
   {
     "query": "[user's question]",
     "context": {
       "selected_text": "[user-selected text, if any]",
       "page_url": "[current page URL]",
       "page_title": "[current page title]"
     }
   }
   ```

3. **Backend processes**:
   - Uses query and context to search Qdrant vectors
   - Sends relevant context to OpenAI agent
   - Returns formatted response

4. **Frontend displays**:
   - Answer with source attribution
   - Shows confidence level
   - Provides follow-up suggestions

## Frontend Component API Requirements

### Configuration Object
The frontend component expects the following configuration:

```javascript
{
  "apiEndpoint": "https://api.example.com",
  "timeoutMs": 30000,
  "maxQueryLength": 1000,
  "showSources": true,
  "enableSelectedText": true
}
```

### Event Callbacks
The component should support these callbacks for integration:

- `onQuerySubmit(query: string)`: Called when user submits a query
- `onResponseReceived(response: APIResponse)`: Called when response is received
- `onError(error: Error)`: Called when an error occurs
- `onLoadingChange(loading: boolean)`: Called when loading state changes

## Error Handling Contract

### Network Errors
- Frontend should display user-friendly error messages
- Should not expose technical details to end users
- Should provide option to retry failed requests

### Backend Unavailability
- Frontend should gracefully degrade functionality
- Should inform users when backend services are temporarily unavailable
- Should maintain chat history during outages

### Rate Limiting
- Frontend should handle rate limiting responses gracefully
- Should inform users about rate limits and when they can try again

## Performance Expectations

### Response Times
- 90% of queries should return within 10 seconds
- Simple queries should return within 3 seconds
- Complex queries may take up to 15 seconds

### Reliability
- API should be available 99% of the time
- Component should handle intermittent connectivity gracefully
- Should maintain state during temporary network issues

## Security Considerations

### Data Transmission
- All communication must use HTTPS in production
- Query content should not contain sensitive user data
- Selected text should be sanitized before transmission

### Input Validation
- Frontend should validate query length before sending
- Backend is responsible for all content validation
- Malformed requests should return appropriate error responses