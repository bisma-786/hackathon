# Data Model: Book URL Ingestion & Vector Indexing

## Entity Models

### ContentChunk
Represents a segment of book content with text, embedding vector, and metadata.

**Fields**:
- `id` (string): Unique identifier (SHA256 hash of content + URL)
- `text` (string): The actual text content of the chunk
- `embedding` (float[]): Vector embedding representation (1024+ dimensions from Cohere)
- `url` (string): Original URL of the source page
- `module` (string): Book module identifier (e.g., "module1", "introduction")
- `section` (string): Section title from the source page
- `heading_hierarchy` (string[]): Array of parent headings in order
- `chunk_index` (int): Sequential index of this chunk within the source document
- `source_length` (int): Original length of the source content
- `created_at` (datetime): Timestamp when chunk was created
- `updated_at` (datetime): Timestamp when chunk was last updated

**Validation Rules**:
- `id` must be unique across all chunks
- `text` must be non-empty and ≤ 2000 tokens
- `embedding` must have consistent dimensions (as per Cohere model)
- `url` must be a valid URL
- `module` and `section` must be non-empty

### BookPage
Represents a single book page with URL, module, section title, and heading hierarchy.

**Fields**:
- `url` (string): Unique URL identifier for the page
- `module` (string): Module identifier
- `section_title` (string): Main title of the section
- `heading_hierarchy` (string[]): Complete heading hierarchy of the page
- `content_length` (int): Total character count of page content
- `word_count` (int): Total word count of page content
- `crawl_status` (enum): Status of crawling (pending, success, failed, retry)
- `last_crawled` (datetime): Timestamp of last crawl attempt
- `metadata` (dict): Additional metadata from HTML (title, description, etc.)

**Validation Rules**:
- `url` must be unique
- `module` and `section_title` must be non-empty
- `heading_hierarchy` elements must be properly nested

### VectorRecord
Represents an indexed item in Qdrant with embedding vector and associated metadata.

**Fields**:
- `point_id` (string): Unique identifier in Qdrant (same as ContentChunk.id)
- `vector` (float[]): The embedding vector
- `payload` (dict): Metadata payload containing:
  - `url` (string): Source URL
  - `module` (string): Module identifier
  - `section` (string): Section identifier
  - `chunk_index` (int): Position in source document
  - `text_preview` (string): Short preview of text content
  - `source_length` (int): Length of source content
- `collection_name` (string): Name of the Qdrant collection

**Validation Rules**:
- `point_id` must be unique within collection
- `vector` dimensions must match model specifications
- `payload` must contain required metadata fields

## Relationships

### ContentChunk → BookPage
- **Relationship**: Many-to-One
- **Description**: Multiple content chunks can originate from the same book page
- **Implementation**: `ContentChunk.url` references `BookPage.url`

### VectorRecord → ContentChunk
- **Relationship**: One-to-One
- **Description**: Each vector record corresponds to exactly one content chunk
- **Implementation**: `VectorRecord.point_id` equals `ContentChunk.id`

## State Transitions

### BookPage State Transitions
```
pending → crawling → success
            ↘ error → retry → crawling
```

- `pending`: Page discovered, ready for crawling
- `crawling`: Currently being processed
- `success`: Successfully crawled and processed
- `error`: Failed during crawling
- `retry`: Marked for retry after failure

## Data Flow

### Ingestion Flow
1. **Discovery**: BookPage records created with `pending` status
2. **Crawling**: BookPage transitions to `crawling`, then to `success` or `error`
3. **Extraction**: ContentChunk records created from successful BookPage content
4. **Embedding**: ContentChunk records get embedding vectors generated
5. **Storage**: VectorRecord records created in Qdrant with metadata payload

### Update Flow
1. **Re-run**: Process can be re-executed safely due to idempotent operations
2. **Deduplication**: ContentChunk.id prevents duplicate storage
3. **Upsert**: VectorRecord updates in Qdrant if content changes
4. **Metadata sync**: Updated metadata propagates to Qdrant payloads

## Schema Examples

### ContentChunk Example
```json
{
  "id": "sha256_hash_of_content_and_url",
  "text": "This is a sample text chunk from the book content...",
  "embedding": [0.12, -0.45, 0.88, ...],
  "url": "https://ai-book.example.com/module1/intro",
  "module": "module1",
  "section": "Introduction to AI",
  "heading_hierarchy": ["Chapter 1", "Section 1.1", "Introduction"],
  "chunk_index": 0,
  "source_length": 1200,
  "created_at": "2025-12-24T10:00:00Z",
  "updated_at": "2025-12-24T10:00:00Z"
}
```

### VectorRecord Payload Example
```json
{
  "point_id": "sha256_hash_of_content_and_url",
  "vector": [0.12, -0.45, 0.88, ...],
  "payload": {
    "url": "https://ai-book.example.com/module1/intro",
    "module": "module1",
    "section": "Introduction to AI",
    "chunk_index": 0,
    "text_preview": "This is a sample text chunk from the...",
    "source_length": 1200
  },
  "collection_name": "book_content_chunks"
}
```