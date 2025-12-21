# Quickstart Guide: Agent & FastAPI Integration

## Prerequisites

- Python 3.11 or higher
- pip package manager
- Qdrant Cloud account with API key and URL
- OpenAI account with API key
- Git for version control

## Setup Instructions

### 1. Clone and Navigate to Backend Directory
```bash
cd backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

If requirements.txt doesn't exist, install the core dependencies:
```bash
pip install fastapi uvicorn python-dotenv openai qdrant-client pydantic pytest
```

### 4. Configure Environment Variables
Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```env
QDRANT_URL=your_qdrant_url_here
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_COLLECTION_NAME=vectors
OPENAI_API_KEY=your_openai_api_key_here
```

### 5. Verify Qdrant Connection
Before starting the service, ensure your Qdrant collection exists and has vectors stored from previous specs.

## Running the Application

### Development Mode
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## Testing the API

### 1. Check Health Status
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "success",
  "data": {
    "status": "healthy",
    "timestamp": "2025-12-21T10:30:25Z",
    "services": {
      "qdrant": "connected",
      "openai": "available",
      "database": "ok"
    }
  },
  "metadata": {
    "request_id": "...",
    "timestamp": "...",
    "execution_time": 0.01
  }
}
```

### 2. Test Vector Retrieval by URL
```bash
curl -G \
  --data-urlencode "url=https://example.com/textbook/module1" \
  http://localhost:8000/api/vectors/url
```

### 3. Test Agent Query
```bash
curl -X POST http://localhost:8000/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the key principles of embodied cognition in robotics?",
    "context": {
      "selected_text": "embodied cognition"
    }
  }'
```

### 4. Test Semantic Search
```bash
curl -X POST http://localhost:8000/api/vectors/search \
  -H "Content-Type: application/json" \
  -d '{
    "selected_text": "PID control in robotics",
    "limit": 5
  }'
```

## Validation

### Verify Vector Storage
```bash
curl http://localhost:8000/api/validate
```

### Check Available Endpoints
Visit `http://localhost:8000/docs` for interactive API documentation.

## Common Issues and Troubleshooting

### 1. Qdrant Connection Issues
- Verify QDRANT_URL and QDRANT_API_KEY are correct
- Ensure the Qdrant collection exists
- Check that vectors were properly ingested in previous specs

### 2. OpenAI API Issues
- Verify OPENAI_API_KEY is valid
- Check OpenAI account usage limits
- Ensure proper network connectivity to OpenAI

### 3. Environment Variables Not Loading
- Verify .env file is in the correct directory
- Check that python-dotenv is installed
- Restart the application after changing environment variables

### 4. API Response Times
- First queries may be slower due to initialization
- Subsequent queries should respond within the expected timeframes
- Monitor resource usage during high load

## Next Steps

1. Integrate with your frontend application
2. Add authentication if required for production use
3. Set up monitoring and logging for production deployment
4. Configure rate limiting based on your usage requirements