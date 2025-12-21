# Research Summary: RAG Content Ingestion Pipeline

## Decision: Use Python with specific libraries for RAG pipeline
**Rationale**: Python is the standard language for data processing, NLP, and ML pipelines. It has excellent libraries for web scraping, text processing, and integration with both Cohere and Qdrant services.

**Alternatives considered**:
- JavaScript/Node.js: Less suitable for ML/NLP tasks
- Go: Good for web scraping but less ecosystem for embeddings
- Java: More complex for this type of data processing task

## Decision: Use requests + BeautifulSoup for web crawling and text extraction
**Rationale**: requests is the standard Python library for HTTP requests, and BeautifulSoup is the go-to for HTML parsing. Together they provide reliable web scraping capabilities that work well with Docusaurus-generated sites.

**Alternatives considered**:
- Selenium: More complex, needed only for JavaScript-heavy sites
- Scrapy: More complex framework, overkill for this specific task
- Playwright: Good for dynamic content but more complex setup

## Decision: Use Cohere's embedding API
**Rationale**: The specification specifically requires Cohere embeddings, and Cohere provides high-quality text embeddings optimized for search and similarity tasks.

**Alternatives considered**:
- OpenAI embeddings: Not specified in requirements
- Hugging Face models: Self-hosted option but more complex
- Sentence Transformers: Local option but doesn't meet requirement for Cohere

## Decision: Use Qdrant Cloud for vector storage
**Rationale**: The specification specifically requires Qdrant Cloud (Free Tier), which provides managed vector database services with good Python client support.

**Alternatives considered**:
- Pinecone: Not specified in requirements
- Weaviate: Alternative vector DB but not requested
- Self-hosted solutions: More complex than required

## Decision: Single main.py file structure
**Rationale**: The user specifically requested that all functionality be in one file named main.py with specific functions (get_all_urls, extract_text_from_urls, chunk_text, embed, create_collection, save_chunk_to_qdrant).

**Alternatives considered**:
- Modular structure: More maintainable but doesn't meet user requirements
- Multiple files: Better organization but against user specifications

## Decision: Text chunking strategy
**Rationale**: For textbook content, we'll use a combination of semantic boundaries (sections, paragraphs) and token limits to ensure chunks are contextually coherent while fitting within embedding model limits.

**Alternatives considered**:
- Fixed character length: May split in middle of concepts
- Sentence-based: May create too many small chunks
- Document-section based: May exceed model limits

## Decision: Deployment URL handling
**Rationale**: The provided URL (https://ai-driven-humanoid-robotics-textboo-chi.vercel.app/) will be crawled to extract all internal links, ensuring complete textbook coverage.

**Implementation approach**:
- Start with the base URL
- Extract all relative links within the same domain
- Follow a breadth-first approach to discover all pages
- Handle potential pagination or navigation structures specific to Docusaurus

## Decision: Metadata tracking
**Rationale**: Each chunk must retain source information (URL, module, section) as required by the specification. This will be stored as payload in Qdrant vectors.

**Implementation approach**:
- Store original URL
- Extract Docusaurus-specific metadata (sidebar labels, category, etc.)
- Include chunk position information for reconstruction