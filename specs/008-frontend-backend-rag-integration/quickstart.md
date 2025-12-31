# Quickstart Guide: Frontend-Backend RAG Integration

## Prerequisites

- Python 3.11+
- Node.js (for Docusaurus frontend)
- Access to OpenAI API (valid API key)
- Access to Qdrant vector database (URL and API key)

## Environment Setup

1. **Set up environment variables**:
   ```bash
   # Create .env file in the backend directory
   OPENAI_API_KEY="your_openai_api_key"
   QDRANT_URL="your_qdrant_url"
   QDRANT_API_KEY="your_qdrant_api_key"
   QDRANT_COLLECTION_NAME="book_content_chunks"
   ```

2. **Install backend dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

## Backend Setup

1. **Start the FastAPI server**:
   ```bash
   cd backend
   uvicorn api:app --reload --port 8000
   ```

2. **Verify the API is running**:
   - Visit `http://localhost:8000/docs` to access the Swagger UI
   - Test the `/query` endpoint with sample requests

## Frontend Integration

1. **Add the chatbot component to Docusaurus**:
   - Place the Chatbot component in the Docusaurus src/components directory
   - Configure the component to connect to your backend API endpoint

2. **Configure API endpoint**:
   - Update the frontend to point to your backend API (e.g., `http://localhost:8000/query`)

## Testing the Integration

1. **Test the API endpoint directly**:
   ```bash
   curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What is ROS 2?",
       "session_id": null
     }'
   ```

2. **Test through the frontend**:
   - Access your Docusaurus site
   - Use the chatbot interface to submit queries
   - Verify responses are returned correctly

## API Usage Examples

### Simple Query
```json
{
  "query": "What is the main advantage of ROS 2 over ROS 1?"
}
```

### Query with Session Context
```json
{
  "query": "Can you explain more about that?",
  "session_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### Expected Response
```json
{
  "response": "ROS 2 provides better real-time capabilities...",
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "source_chunks": [
    {
      "id": "chunk_123",
      "content": "ROS 2 improves on ROS 1 with better real-time support...",
      "score": 0.85
    }
  ],
  "content_quality": {
    "total_chunks": 5,
    "valid_chunks": 3,
    "low_score_chunks": 2,
    "min_score_threshold": 0.1,
    "has_valid_content": true,
    "all_chunks_low_score": false,
    "average_score": 0.72
  },
  "query_time": 1703123456.789
}
```

## Troubleshooting

- **API Key Issues**: Verify that your OPENAI_API_KEY and QDRANT_API_KEY are correctly set
- **Connection Issues**: Ensure the QDRANT_URL is accessible and properly formatted
- **Response Time**: Large queries or complex retrieval may take longer than expected
- **Session Management**: Session IDs are returned in responses and should be preserved for conversation context