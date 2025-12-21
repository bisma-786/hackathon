# Data Model: Agent & FastAPI Integration

## Entity Definitions

### VectorEmbedding
**Description**: Represents a chunk of textbook content with associated vector embedding and metadata

**Attributes**:
- `id` (string): Unique identifier for the vector record
- `embedding` (list of floats): The vector embedding representation of the content
- `metadata` (object): Key-value pairs containing contextual information
  - `url` (string): Source URL of the content
  - `module` (string): Module identifier in the textbook
  - `section` (string): Section identifier within the module
  - `position` (integer): Sequential position in the document
  - `hash` (string): Content hash for idempotency
  - `source_text` (string): Original text content
- `timestamp` (datetime): When the vector was created/updated

**Validation Rules**:
- `id` must be unique and non-empty
- `embedding` must have consistent dimensions
- `url` must be a valid URL format
- `position` must be non-negative integer
- `hash` must be non-empty

### QueryRequest
**Description**: Represents a user query request to the system

**Attributes**:
- `query` (string): The natural language query from the user
- `query_type` (enum): Type of query (text_search, url_search, module_search, section_search)
- `parameters` (object): Additional parameters for the query
  - `url` (string, optional): URL to search within
  - `module` (string, optional): Module to search within
  - `section` (string, optional): Section to search within
  - `selected_text` (string, optional): Specific text to search for
- `context` (object): Additional context for the agent
  - `user_id` (string, optional): Identifier for the requesting user
  - `session_id` (string, optional): Session identifier for conversation context

**Validation Rules**:
- `query` must be non-empty and less than 1000 characters
- `query_type` must be one of the valid enum values
- At least one of `query`, `url`, `module`, `section`, or `selected_text` must be provided

### APIResponse
**Description**: Standard response structure returned by API endpoints

**Attributes**:
- `status` (string): Response status (success, error)
- `data` (object): The main response data
- `metadata` (object): Additional metadata about the response
  - `request_id` (string): Unique identifier for the request
  - `timestamp` (datetime): When the response was generated
  - `execution_time` (float): Time taken to process the request in seconds
- `errors` (array of objects): List of errors if status is error
  - `code` (string): Error code
  - `message` (string): Human-readable error message
  - `details` (object): Additional error details

**Validation Rules**:
- `status` must be either "success" or "error"
- When status is "success", `data` must be present
- When status is "error", `errors` must contain at least one error

### AgentResponse
**Description**: Response from the OpenAI agent with context-aware answers

**Attributes**:
- `answer` (string): The agent's answer to the user's query
- `sources` (array of strings): List of source identifiers used to generate the answer
- `confidence` (float): Confidence score for the answer (0.0 to 1.0)
- `retrieved_context` (array of objects): Context used to generate the answer
  - `id` (string): Vector ID
  - `content` (string): Text content of the retrieved chunk
  - `similarity_score` (float): Similarity score of the match
  - `metadata` (object): Metadata associated with the vector
- `followup_questions` (array of strings): Suggested follow-up questions

**Validation Rules**:
- `answer` must be non-empty
- `confidence` must be between 0.0 and 1.0
- `sources` must contain valid vector IDs
- `retrieved_context` items must have non-empty content

### AgentRequest
**Description**: Request structure for the OpenAI agent

**Attributes**:
- `query` (string): The original user query
- `context` (array of strings): Retrieved context to provide to the agent
- `instructions` (string): Instructions for how the agent should respond
- `temperature` (float): Temperature setting for response creativity
- `max_tokens` (integer): Maximum tokens in the response

**Validation Rules**:
- `query` must be non-empty
- `context` must contain at least one item
- `temperature` must be between 0.0 and 1.0
- `max_tokens` must be positive

## Relationships

### VectorEmbedding → QueryRequest
- A `QueryRequest` retrieves multiple `VectorEmbedding` records based on similarity
- Relationship: One-to-many (one query can match many vectors)

### QueryRequest → APIResponse
- A `QueryRequest` produces one `APIResponse`
- Relationship: One-to-one (one request maps to one response)

### QueryRequest → AgentResponse
- A `QueryRequest` may produce an `AgentResponse` when using the OpenAI agent
- Relationship: One-to-zero-or-one (not all queries require agent processing)

### AgentRequest → AgentResponse
- An `AgentRequest` produces one `AgentResponse`
- Relationship: One-to-one (one agent request maps to one response)

## State Transitions

### Query Processing States
1. **Received**: Query has been received by the API
2. **Processing**: Vector retrieval is in progress
3. **ContextRetrieved**: Relevant vectors have been retrieved
4. **AgentProcessing**: OpenAI agent is processing the query with context
5. **Completed**: Response has been generated and is ready to return
6. **Failed**: An error occurred during processing

## Constraints

### Data Integrity
- Vector embeddings must maintain consistent dimensionality across the system
- Content hash must match the actual content to ensure data integrity
- Metadata fields must be consistently formatted across all vector records

### Performance
- Vector search operations should return results within 5 seconds
- API responses should be generated within 10 seconds for agent queries
- Large context payloads should be chunked appropriately for OpenAI API limits

### Security
- Sensitive API keys must not be exposed in responses
- User queries should be sanitized to prevent injection attacks
- Request IDs should be securely generated to prevent prediction