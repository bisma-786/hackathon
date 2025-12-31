# Data Model: Frontend-Backend RAG Integration

## Entities

### QueryRequest
**Description**: Represents a user query sent from the frontend to the backend API

**Fields**:
- `query`: string (required) - The user's question text
- `session_id`: string (optional) - Identifier for maintaining conversation context

**Validation Rules**:
- `query` must be non-empty and less than 10000 characters
- `session_id` must be a valid UUID format if provided

### QueryResponse
**Description**: Represents the response from the RAG agent returned to the frontend

**Fields**:
- `response`: string (required) - The agent's answer to the user's query
- `session_id`: string (required) - Session identifier (newly created or existing)
- `source_chunks`: array of SourceChunk objects - Content chunks used to generate the response
- `content_quality`: object - Quality metrics of the retrieved content
- `query_time`: number - Unix timestamp of when the query was processed

**Validation Rules**:
- `response` must be non-empty
- `session_id` must be a valid UUID format
- `source_chunks` must be an array of valid SourceChunk objects

### SourceChunk
**Description**: Represents a segment of book content used to generate the response

**Fields**:
- `id`: string (required) - Unique identifier for the content chunk
- `content`: string (required) - The text content of the chunk
- `score`: number (required) - Relevance score between 0 and 1

**Validation Rules**:
- `id` must be non-empty
- `content` must be non-empty
- `score` must be between 0 and 1

### ContentQuality
**Description**: Represents quality metrics of the retrieved content

**Fields**:
- `total_chunks`: number (required) - Total number of chunks retrieved
- `valid_chunks`: number (required) - Number of chunks with acceptable scores
- `low_score_chunks`: number (required) - Number of chunks with low scores
- `min_score_threshold`: number (required) - Minimum score threshold used
- `has_valid_content`: boolean (required) - Whether any valid content was found
- `all_chunks_low_score`: boolean (required) - Whether all chunks had low scores
- `average_score`: number (required) - Average score of all chunks

**Validation Rules**:
- All numeric fields must be non-negative
- `average_score` must be between 0 and 1

## State Transitions

### Query Processing Flow
1. **Initial State**: Frontend has user input (query text)
2. **Request State**: Frontend sends QueryRequest to backend API
3. **Processing State**: Backend calls RAG agent with query and session context
4. **Response State**: Backend returns QueryResponse to frontend
5. **Display State**: Frontend displays response and updates UI

## API Contract

### POST /query
**Purpose**: Process a user query through the RAG agent

**Request**:
- Method: POST
- Content-Type: application/json
- Body: QueryRequest object

**Response**:
- Success: 200 OK with QueryResponse object
- Bad Request: 400 Bad Request with error details
- Server Error: 500 Internal Server Error with error details