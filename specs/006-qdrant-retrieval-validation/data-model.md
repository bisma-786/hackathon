# Data Model: Qdrant Retrieval & Validation Pipeline

## Entities

### Query
- **Description**: A text input from the user requesting relevant book content
- **Fields**:
  - text: string (the query text)
  - embedding: list[float] (vector representation of the query)
  - timestamp: datetime (when the query was made)
- **Validation**:
  - text must not be empty
  - text length should be reasonable (not exceed maximum embedding model input)
- **Relationships**: None

### Retrieved Text Chunk
- **Description**: A segment of book content that matches the user's query semantically
- **Fields**:
  - id: string (unique identifier for the chunk)
  - text: string (the actual content of the text chunk)
  - score: float (similarity score relative to the query)
  - embedding: list[float] (vector representation of the text chunk)
- **Validation**:
  - text must not be empty
  - score must be between 0 and 1
- **Relationships**: Associated with Query via similarity search

### Metadata
- **Description**: Information associated with each text chunk including URL, module, and section identifiers
- **Fields**:
  - source_url: string (URL of the original document)
  - module: string (module identifier)
  - section: string (section identifier)
  - chunk_id: string (identifier for this specific chunk)
- **Validation**:
  - source_url must be a valid URL format
  - module and section must not be empty
- **Relationships**: Associated with Retrieved Text Chunk

### Qdrant Vector Store
- **Description**: The vector database containing embedded book content for retrieval
- **Fields**:
  - collection_name: string (name of the Qdrant collection)
  - vector_size: int (dimension of the embedding vectors)
  - total_vectors: int (number of vectors in the collection)
- **Validation**:
  - collection_name must exist in Qdrant
  - vector_size must match the embedding model used
- **Relationships**: Contains Retrieved Text Chunks with their embeddings and metadata

### Search Results
- **Description**: Container for the results of a similarity search operation
- **Fields**:
  - query: Query (the original query that was processed)
  - results: list[Retrieved Text Chunk] (top-K most relevant chunks)
  - execution_time: float (time taken to perform the search in seconds)
  - total_candidates: int (total number of vectors considered in the search)
- **Validation**:
  - results list should not be empty (unless no matches found)
  - execution_time should be positive
- **Relationships**: Contains multiple Retrieved Text Chunks, associated with Query

## State Transitions

### Query Processing Flow
1. Query created with text input
2. Query embedding generated using Cohere model
3. Similarity search performed against Qdrant Vector Store
4. Retrieved Text Chunks with Metadata returned as Search Results
5. Validation performed on results and metadata alignment