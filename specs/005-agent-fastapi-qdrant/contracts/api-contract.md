# API Contract: Agent & FastAPI Integration

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
  "context": {
    "url": "https://example.com/textbook/module3",
    "module": "embodied_cognition",
    "section": "principles",
    "selected_text": "embodied cognition principles"
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
  "status": "success",
  "data": {
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
  },
  "metadata": {
    "request_id": "req_abc123",
    "timestamp": "2025-12-21T10:30:00Z",
    "execution_time": 2.45
  }
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

### 2. Vector Retrieval by URL
**GET** `/api/vectors/url`

#### Description
Retrieve all vector embeddings associated with a specific URL.

#### Query Parameters
- `url` (required): The URL to retrieve vectors for
- `limit` (optional): Maximum number of vectors to return (default: 100, max: 1000)
- `offset` (optional): Offset for pagination (default: 0)

#### Response (Success - 200 OK)
```json
{
  "status": "success",
  "data": {
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
        "timestamp": "2025-12-20T09:00:00Z"
      }
    ],
    "total_count": 1,
    "limit": 100,
    "offset": 0
  },
  "metadata": {
    "request_id": "req_def456",
    "timestamp": "2025-12-21T10:30:05Z",
    "execution_time": 0.12
  }
}
```

#### Error Responses
- `400 Bad Request`: Invalid URL parameter
- `500 Internal Server Error`: Error connecting to Qdrant

---

### 3. Vector Retrieval by Module
**GET** `/api/vectors/module`

#### Description
Retrieve all vector embeddings associated with a specific module.

#### Query Parameters
- `module` (required): The module name to retrieve vectors for
- `limit` (optional): Maximum number of vectors to return (default: 100, max: 1000)
- `offset` (optional): Offset for pagination (default: 0)

#### Response (Success - 200 OK)
```json
{
  "status": "success",
  "data": {
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
        "timestamp": "2025-12-20T09:15:00Z"
      }
    ],
    "total_count": 1,
    "limit": 100,
    "offset": 0
  },
  "metadata": {
    "request_id": "req_ghi789",
    "timestamp": "2025-12-21T10:30:10Z",
    "execution_time": 0.08
  }
}
```

#### Error Responses
- `400 Bad Request`: Invalid module parameter
- `500 Internal Server Error`: Error connecting to Qdrant

---

### 4. Vector Retrieval by Section
**GET** `/api/vectors/section`

#### Description
Retrieve all vector embeddings associated with a specific section.

#### Query Parameters
- `section` (required): The section name to retrieve vectors for
- `limit` (optional): Maximum number of vectors to return (default: 100, max: 1000)
- `offset` (optional): Offset for pagination (default: 0)

#### Response (Success - 200 OK)
```json
{
  "status": "success",
  "data": {
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
        "timestamp": "2025-12-20T09:30:00Z"
      }
    ],
    "total_count": 1,
    "limit": 100,
    "offset": 0
  },
  "metadata": {
    "request_id": "req_jkl012",
    "timestamp": "2025-12-21T10:30:15Z",
    "execution_time": 0.09
  }
}
```

#### Error Responses
- `400 Bad Request`: Invalid section parameter
- `500 Internal Server Error`: Error connecting to Qdrant

---

### 5. Semantic Search by Selected Text
**POST** `/api/vectors/search`

#### Description
Perform semantic search using selected text to find similar content.

#### Request
```json
{
  "selected_text": "embodied cognition principles",
  "limit": 10,
  "min_similarity": 0.5
}
```

#### Response (Success - 200 OK)
```json
{
  "status": "success",
  "data": {
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
        "similarity_score": 0.94,
        "timestamp": "2025-12-20T10:00:00Z"
      }
    ],
    "query_text": "embodied cognition principles",
    "total_count": 1
  },
  "metadata": {
    "request_id": "req_mno345",
    "timestamp": "2025-12-21T10:30:20Z",
    "execution_time": 0.35
  }
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
    "request_id": "req_health_check",
    "timestamp": "2025-12-21T10:30:25Z",
    "execution_time": 0.01
  }
}
```

#### Error Responses
- `503 Service Unavailable`: One or more services are unavailable

---

### 7. Validation Endpoint
**GET** `/api/validate`

#### Description
Validate that vectors are properly stored and queryable in Qdrant.

#### Response (Success - 200 OK)
```json
{
  "status": "success",
  "data": {
    "qdrant_connection": true,
    "collections": ["vectors"],
    "vector_count": 5420,
    "last_ingestion": "2025-12-20T15:30:00Z",
    "validation_passed": true,
    "issues": []
  },
  "metadata": {
    "request_id": "req_validation",
    "timestamp": "2025-12-21T10:30:30Z",
    "execution_time": 0.25
  }
}
```

#### Error Responses
- `500 Internal Server Error`: Error validating Qdrant connection

## Common Error Codes

| Code | Description |
|------|-------------|
| `INVALID_QUERY` | Query parameter is invalid or missing |
| `INVALID_URL` | URL parameter is malformed |
| `INVALID_MODULE` | Module parameter is invalid |
| `INVALID_SECTION` | Section parameter is invalid |
| `VECTOR_NOT_FOUND` | No vectors found for the given criteria |
| `QDRANT_CONNECTION_ERROR` | Unable to connect to Qdrant |
| `OPENAI_API_ERROR` | Error communicating with OpenAI API |
| `RATE_LIMIT_EXCEEDED` | API rate limit has been exceeded |
| `INTERNAL_ERROR` | General internal server error |

## Rate Limits
- Default: 100 requests per minute per IP
- Agent queries: 10 requests per minute per IP (due to OpenAI costs)
- Bearer tokens can be used to increase limits

## Versioning
API versioning is handled through the URL path (e.g., `/api/v1/...`) with the current version being v1.