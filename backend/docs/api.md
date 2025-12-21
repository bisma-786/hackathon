# API Documentation: AI-Driven Robotics Textbook RAG API

## Base URL
`http://localhost:8000` (or configured host/port)

## Common Headers
- `Content-Type: application/json`
- `Accept: application/json`

## Authentication
API key authentication via `Authorization: Bearer {API_KEY}` header (if enabled)

## Endpoints

### 1. Agent Query Endpoint
**POST** `/api/agent/query`

#### Description
Process a natural language query through the OpenAI agent with retrieved context from Qdrant.

#### Request
```json
{
  "query": "What are the key principles of embodied cognition in robotics?",
  "instructions": "You are an AI assistant for the AI-Driven Robotics Textbook. Answer questions based on the provided context.",
  "temperature": 0.7,
  "max_tokens": 150
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

#### Error Responses
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Missing or invalid API key
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server-side error during processing

---

### 2. Vector Retrieval by URL
**GET** `/api/vectors/by-url`

#### Description
Retrieve all vector embeddings associated with a specific URL.

#### Query Parameters
- `url` (required): The URL to retrieve vectors for
- `limit` (optional): Maximum number of vectors to return (default: 100, max: 1000)
- `offset` (optional): Offset for pagination (default: 0)

#### Response (Success - 200 OK)
```json
{
  "vectors": [
    {
      "id": "vector_123",
      "embedding": [0.1, 0.2, 0.3, ...],
      "metadata": {
        "url": "https://example.com/textbook/module1",
        "module": "introduction",
        "section": "overview",
        "position": 0,
        "hash": "abc123",
        "source_text": "This is the introduction to robotics..."
      },
      "similarity_score": null
    }
  ],
  "total_count": 1,
  "limit": 100,
  "offset": 0
}
```

#### Error Responses
- `400 Bad Request`: Invalid URL parameter
- `500 Internal Server Error`: Error connecting to Qdrant

---

### 3. Vector Retrieval by Module
**GET** `/api/vectors/by-module`

#### Description
Retrieve all vector embeddings associated with a specific module.

#### Query Parameters
- `module` (required): The module name to retrieve vectors for
- `limit` (optional): Maximum number of vectors to return (default: 100, max: 1000)
- `offset` (optional): Offset for pagination (default: 0)

#### Response (Success - 200 OK)
```json
{
  "vectors": [
    {
      "id": "vector_456",
      "embedding": [0.4, 0.5, 0.6, ...],
      "metadata": {
        "url": "https://example.com/textbook/module2",
        "module": "kinematics",
        "section": "forward_kinematics",
        "position": 1,
        "hash": "def456",
        "source_text": "Forward kinematics is the process of determining..."
      },
      "similarity_score": null
    }
  ],
  "total_count": 1,
  "limit": 100,
  "offset": 0
}
```

#### Error Responses
- `400 Bad Request`: Invalid module parameter
- `500 Internal Server Error`: Error connecting to Qdrant

---

### 4. Vector Retrieval by Section
**GET** `/api/vectors/by-section`

#### Description
Retrieve all vector embeddings associated with a specific section.

#### Query Parameters
- `section` (required): The section name to retrieve vectors for
- `limit` (optional): Maximum number of vectors to return (default: 100, max: 1000)
- `offset` (optional): Offset for pagination (default: 0)

#### Response (Success - 200 OK)
```json
{
  "vectors": [
    {
      "id": "vector_789",
      "embedding": [0.7, 0.8, 0.9, ...],
      "metadata": {
        "url": "https://example.com/textbook/module3",
        "module": "control_theory",
        "section": "pid_control",
        "position": 2,
        "hash": "ghi789",
        "source_text": "PID control is a feedback control mechanism..."
      },
      "similarity_score": null
    }
  ],
  "total_count": 1,
  "limit": 100,
  "offset": 0
}
```

#### Error Responses
- `400 Bad Request`: Invalid section parameter
- `500 Internal Server Error`: Error connecting to Qdrant

---

### 5. Semantic Search by Selected Text
**GET** `/api/vectors/semantic-search`

#### Description
Perform semantic search using selected text to find similar content.

#### Query Parameters
- `query` (required): Query text for semantic search (min 1, max 500 characters)
- `limit` (optional): Maximum number of vectors to return (default: 10, max: 100)
- `min_similarity` (optional): Minimum similarity threshold (default: 0.5)

#### Response (Success - 200 OK)
```json
{
  "vectors": [
    {
      "id": "vector_101",
      "embedding": [0.1, 0.9, 0.2, ...],
      "metadata": {
        "url": "https://example.com/textbook/module3",
        "module": "embodied_cognition",
        "section": "principles",
        "position": 1,
        "hash": "jkl012",
        "source_text": "Embodied cognition principles emphasize the role of the body in cognitive processes..."
      },
      "similarity_score": 0.94
    }
  ],
  "total_count": 1,
  "limit": 10,
  "query_text": "embodied cognition principles"
}
```

#### Error Responses
- `400 Bad Request`: Invalid search parameters
- `500 Internal Server Error`: Error during semantic search

---

### 6. Health Check
**GET** `/health`

#### Description
Check the health status of the API service.

#### Response (Success - 200 OK)
```json
{
  "status": "healthy",
  "message": "AI-Driven Robotics Textbook RAG API is running"
}
```

---

### 7. Validation Endpoints

#### Validation Status
**GET** `/api/validation/status`

#### Description
Validate that vectors are properly stored and queryable in Qdrant.

#### Response (Success - 200 OK)
```json
{
  "collection_exists": true,
  "vector_count": 5420,
  "is_valid": true,
  "message": "Validation completed successfully"
}
```

#### Validation Report
**GET** `/api/validation/report`

#### Description
Generate a comprehensive validation report.

#### Response (Success - 200 OK)
```json
{
  "timestamp": "2025-12-21T10:30:30Z",
  "collection_name": "vectors",
  "connection_valid": true,
  "validation_result": {
    "collection_exists": true,
    "vector_count": 5420,
    "is_valid": true,
    "message": "Validation completed successfully"
  }
}
```

#### Error Responses
- `500 Internal Server Error`: Error validating Qdrant connection

## Common Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Input validation failed |
| `CONNECTION_ERROR` | Connection to external service failed |
| `RETRIEVAL_ERROR` | Error during vector retrieval |
| `AGENT_ERROR` | Error during agent processing |
| `INTERNAL_ERROR` | General internal server error |

## Rate Limits
- Default: 100 requests per minute per IP
- Agent queries: 10 requests per minute per IP (due to OpenAI costs)
- Bearer tokens can be used to increase limits