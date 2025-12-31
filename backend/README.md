# RAG Chatbot API

This FastAPI server provides an endpoint for the RAG chatbot to integrate with the Docusaurus frontend.

## Features

- `/query` endpoint to process user questions through the RAG agent
- Session management for conversation context
- Input validation and error handling
- Integration with existing RAG agent functionality

## Requirements

- Python 3.11+
- Dependencies listed in `requirements.txt`

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Ensure your `.env` file contains the required environment variables:
   ```env
   GEMINI_API_KEY="your_gemini_api_key_here"
   QDRANT_URL="your_qdrant_url_here"
   QDRANT_API_KEY="your_qdrant_api_key_here"
   QDRANT_COLLECTION_NAME="book_content_chunks"
   ```

## Running the Server

```bash
cd backend
uvicorn api:app --reload --port 8000
```

The API will be available at `http://localhost:8000` with automatic documentation at `http://localhost:8000/docs`.

## API Usage

### Query Endpoint

`POST /query`

Request body:
```json
{
  "query": "Your question here",
  "session_id": "optional session ID (null for new session)"
}
```

Example:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is ROS 2?",
    "session_id": null
  }'
```

Response:
```json
{
  "response": "The answer from the RAG agent",
  "session_id": "session identifier",
  "source_chunks": [...],
  "content_quality": {...},
  "query_time": 1234567890.123
}
```

## Testing

Run the tests with pytest:
```bash
pytest test_api.py -v
pytest test_session.py -v
```

## Endpoints

- `GET /` - Health check
- `POST /query` - Process user query through RAG agent
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)