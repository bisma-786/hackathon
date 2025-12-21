# Data Model: RAG Content Ingestion Pipeline

## Entities

### TextContent
- **id**: Unique identifier for the content chunk
- **url**: Original source URL of the content
- **module**: Module/section identifier from the textbook structure
- **section**: Specific section name within the module
- **content**: The actual text content (cleaned and processed)
- **created_at**: Timestamp when the content was extracted
- **processed_at**: Timestamp when the content was embedded

### EmbeddingVector
- **id**: Unique identifier for the vector (matches TextContent.id)
- **vector**: The numerical embedding vector from Cohere
- **metadata**: Dictionary containing source information (URL, module, section)
- **created_at**: Timestamp when the embedding was generated

### Chunk
- **id**: Unique identifier for the text chunk
- **text_content_id**: Reference to the TextContent entity
- **text**: The chunked text content
- **position**: Position of this chunk within the original content
- **hash**: Content hash for idempotency checks
- **metadata**: Additional metadata including source URL, module, section

### CrawlResult
- **url**: The URL that was crawled
- **status_code**: HTTP status of the crawl
- **content_length**: Size of the content retrieved
- **processed**: Boolean indicating if content was successfully processed
- **error_message**: Any error encountered during processing
- **timestamp**: When the crawl was performed

## Relationships

- One `TextContent` entity can have multiple `Chunk` entities (1:N)
- One `Chunk` entity maps to one `EmbeddingVector` entity (1:1)
- One `CrawlResult` entity corresponds to one `TextContent` entity (1:1)

## Validation Rules

### TextContent Validation
- URL must be a valid URL format
- Content must not be empty after cleaning
- Module and section must be non-empty strings

### Chunk Validation
- Text must be within embedding model length limits
- Position must be a non-negative integer
- Hash must be unique within the system for idempotency

### EmbeddingVector Validation
- Vector must have consistent dimensions based on Cohere model
- Metadata must contain required source information
- Vector values must be valid floating-point numbers

## State Transitions

### Content Processing States
1. `CRAWLED` - URL successfully retrieved but content not yet processed
2. `EXTRACTED` - Text content extracted and cleaned
3. `CHUNKED` - Content split into appropriate chunks
4. `EMBEDDED` - Embeddings generated and stored in Qdrant
5. `VALIDATED` - All quality checks passed, ready for use

## Constraints

- Each chunk must be smaller than Cohere's maximum input token limit
- Duplicate content detection through hash comparison
- Idempotent operations to allow safe re-runs
- All source metadata must be preserved and traceable