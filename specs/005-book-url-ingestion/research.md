# Research: Book URL Ingestion & Vector Indexing

## Research Summary

This research document addresses the technical requirements for implementing the Book URL Ingestion & Vector Indexing pipeline, focusing on the key components: URL discovery, content extraction, chunking, embedding generation, and vector storage.

## Key Decisions

### 1. URL Discovery and Crawling
**Decision**: Use `requests` library for fetching HTML content and `beautifulsoup4` for parsing links
**Rationale**: These are industry-standard Python libraries for web scraping with good documentation and community support
**Alternatives considered**:
- Selenium (for dynamic content) - rejected as GitHub Pages are static
- Scrapy (for large-scale crawling) - rejected as we have a known set of URLs

### 2. HTML Content Extraction
**Decision**: Use `beautifulsoup4` with `lxml` parser for content extraction
**Rationale**: Best-in-class HTML parsing library with excellent handling of malformed HTML
**Alternatives considered**:
- `html5lib` - slower than lxml
- `lxml` alone - less convenient for complex selections

### 3. Text Chunking Strategy
**Decision**: Implement sliding window chunking with configurable size (1000 tokens) and overlap (200 tokens)
**Rationale**: Provides context preservation while maintaining search efficiency
**Alternatives considered**:
- Sentence-based chunking - may result in uneven chunks
- Paragraph-based chunking - may be too large for embedding models

### 4. Embedding Model Selection
**Decision**: Use Cohere's embed-multilingual-v3.0 model
**Rationale**: Specified in requirements; excellent performance for technical documentation
**Alternatives considered**:
- Cohere's embed-english-v3.0 - rejected as book content may be multilingual
- Other Cohere models - embed-multilingual-v3.0 offers best performance

### 5. Vector Database Integration
**Decision**: Use Qdrant Cloud with cosine similarity
**Rationale**: Specified in requirements; supports metadata storage and efficient similarity search
**Alternatives considered**:
- Pinecone - not specified in requirements
- Weaviate - not specified in requirements

### 6. Pipeline Architecture
**Decision**: Modular architecture with separate components for each pipeline stage
**Rationale**: Follows single responsibility principle and enables independent testing
**Alternatives considered**:
- Monolithic approach - harder to test and maintain

## Technical Implementation Details

### URL Discovery
- Base URL: Determine from GitHub Pages deployment
- Navigation: Parse HTML links to discover all book pages
- Filtering: Exclude assets, search pages, and redirects

### Content Extraction
- Remove navigation, footer, and boilerplate content
- Preserve heading hierarchy and structural context
- Extract text from headings, paragraphs, and code blocks

### Metadata Preservation
- URL: Original page URL
- Module: Book module identifier
- Section: Page/section title
- Heading hierarchy: Preserve document structure

### Idempotent Storage
- Use content hash as document ID to prevent duplicates
- Implement upsert operations in Qdrant
- Support re-runs without creating duplicates

## Best Practices Applied

### Error Handling
- Implement retry logic for network requests
- Graceful degradation for unavailable URLs
- Rate limiting for API calls

### Performance Optimization
- Batch processing for embedding generation
- Parallel URL fetching
- Efficient vector storage operations

### Data Validation
- Content length validation
- Metadata completeness checks
- Embedding dimension verification

## Open Questions Resolved

1. **How to handle large pages?** - Implement chunking with overlap to maintain context
2. **How to ensure deterministic chunking?** - Use consistent chunk size and overlap parameters
3. **How to prevent duplicate storage?** - Use content hash as unique ID
4. **How to preserve metadata?** - Store as payload in Qdrant vectors
5. **How to handle rate limits?** - Implement exponential backoff and batch processing