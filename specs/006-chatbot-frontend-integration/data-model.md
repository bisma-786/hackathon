# Data Model: Frontend Integration of RAG Chatbot

## Entity Definitions

### ChatMessage
**Description**: Represents a single message in the chat conversation

**Attributes**:
- `id` (string): Unique identifier for the message
- `content` (string): The text content of the message
- `sender` (enum): Type of sender (user, assistant)
- `timestamp` (datetime): When the message was created/sent
- `sources` (array of strings): Source references for assistant responses (optional)
- `status` (enum): Message status (pending, sent, error) for UI display

**Validation Rules**:
- `id` must be unique and non-empty
- `content` must be non-empty and less than 5000 characters
- `sender` must be either "user" or "assistant"
- `timestamp` must be a valid ISO 8601 datetime
- `sources` items must be non-empty strings when present

### ChatSession
**Description**: Represents a single chat session on a book page

**Attributes**:
- `id` (string): Unique identifier for the session
- `pageUrl` (string): URL of the book page where the chat is active
- `selectedText` (string): Text that was selected when the query was initiated (optional)
- `messages` (array of ChatMessage): Array of messages in the conversation
- `createdAt` (datetime): When the session was created
- `updatedAt` (datetime): When the session was last updated

**Validation Rules**:
- `id` must be unique and non-empty
- `pageUrl` must be a valid URL format
- `messages` must not exceed 50 messages in a single session
- `createdAt` and `updatedAt` must be valid ISO 8601 datetimes

### APIRequest
**Description**: Represents a request sent from the frontend to the backend API

**Attributes**:
- `query` (string): The user's question/query text
- `selectedText` (string): The text that was selected on the page (optional)
- `pageContext` (object): Additional context about the current page (optional)
  - `url` (string): Current page URL
  - `title` (string): Page title
- `timestamp` (datetime): When the request was made

**Validation Rules**:
- `query` must be non-empty and less than 1000 characters
- `selectedText` if provided must be less than 1000 characters
- `timestamp` must be a valid ISO 8601 datetime

### APIResponse
**Description**: Represents a response received from the backend API

**Attributes**:
- `answer` (string): The answer to the user's query
- `sources` (array of strings): Source references for the answer
- `confidence` (float): Confidence score for the answer (0.0 to 1.0)
- `retrievedContext` (array of objects): Context used to generate the answer
  - `id` (string): Vector ID
  - `content` (string): Text content of the retrieved chunk
  - `similarityScore` (float): Similarity score of the match
  - `metadata` (object): Metadata associated with the vector
- `followupQuestions` (array of strings): Suggested follow-up questions
- `timestamp` (datetime): When the response was generated

**Validation Rules**:
- `answer` must be non-empty
- `confidence` must be between 0.0 and 1.0
- `sources` must contain valid source identifiers
- `retrievedContext` items must have non-empty content
- `timestamp` must be a valid ISO 8601 datetime

### ChatbotConfig
**Description**: Configuration settings for the chatbot component

**Attributes**:
- `apiEndpoint` (string): Base URL for the backend API
- `maxQueryLength` (integer): Maximum allowed query length
- `maxHistorySize` (integer): Maximum number of messages to keep in session
- `timeoutMs` (integer): Request timeout in milliseconds
- `showSources` (boolean): Whether to display source information
- `enableSelectedText` (boolean): Whether to capture and send selected text

**Validation Rules**:
- `apiEndpoint` must be a valid URL
- `maxQueryLength` must be positive
- `maxHistorySize` must be positive
- `timeoutMs` must be between 1000 and 30000

## Relationships

### ChatSession → ChatMessage
- A `ChatSession` contains multiple `ChatMessage` records
- Relationship: One-to-many (one session, many messages)

### ChatMessage → APIResponse
- A user's `ChatMessage` may generate an `APIResponse` from the backend
- Relationship: One-to-zero-or-one (not all messages require API calls, but responses map to messages)

### APIRequest → APIResponse
- An `APIRequest` produces one `APIResponse`
- Relationship: One-to-one (one request maps to one response)

## State Transitions

### ChatMessage States
1. **Draft**: Message is being composed by user
2. **Sending**: Message has been sent to backend
3. **Sent**: Message was successfully sent and acknowledged
4. **Error**: Message failed to send
5. **Received**: Response received from backend

### Chatbot Component States
1. **Idle**: Chatbot is displayed but inactive
2. **Composing**: User is typing a message
3. **Sending**: Message is being sent to backend
4. **Receiving**: Waiting for response from backend
5. **Ready**: Response received and displayed
6. **Error**: Error occurred during communication

## Constraints

### Data Integrity
- Message content must be properly sanitized before display to prevent XSS
- Session data should be validated before storage in session/local storage
- API responses must be validated before updating UI state

### Performance
- Individual message content should be limited to prevent memory issues
- Session history should be capped to prevent excessive memory usage
- API requests should have appropriate timeout limits

### Security
- Sensitive API keys must not be stored in frontend configuration
- User inputs should be validated and sanitized before transmission
- Backend communication must use HTTPS in production environments