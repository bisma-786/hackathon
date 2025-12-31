# Data Model: AI Agent with Retrieval-Augmented Capabilities

## Core Entities

### AI Agent
- **Properties**:
  - id: string (unique identifier)
  - name: string (agent name)
  - instructions: string (system instructions for behavior)
  - tools: list (available tools including retrieval tool)
  - model: string (AI model identifier)
- **Relationships**: Uses retrieval tool for context

### Retrieval Tool
- **Properties**:
  - name: string ("retrieve_chunks")
  - description: string (describes the tool's purpose)
  - parameters: object (query string, top_k integer)
- **Relationships**: Connects to Qdrant vector database

### Query Session
- **Properties**:
  - thread_id: string (OpenAI thread identifier)
  - created_at: datetime (session start time)
  - last_accessed: datetime (last interaction time)
  - context_history: list (conversation history)
- **Relationships**: Contains multiple queries and responses

### Retrieved Chunks
- **Properties**:
  - id: string (chunk identifier)
  - content: string (text content of the chunk)
  - score: float (relevance score)
  - metadata: object (source information, page numbers, etc.)
- **Relationships**: Returned by retrieval tool as context for agent

### Query
- **Properties**:
  - id: string (unique identifier)
  - content: string (user query text)
  - timestamp: datetime (when query was made)
  - session_id: string (reference to Query Session)
- **Relationships**: Belongs to a Query Session

### Response
- **Properties**:
  - id: string (unique identifier)
  - content: string (agent response text)
  - timestamp: datetime (when response was generated)
  - source_chunks: list (references to Retrieved Chunks used)
  - query_id: string (reference to associated Query)
- **Relationships**: Associated with a Query and uses Retrieved Chunks as source