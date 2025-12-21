# API Contract: RAG Content Ingestion Functions

## Function: get_all_urls
**Purpose**: Crawl the deployed Docusaurus site and extract all valid textbook page URLs

**Input**:
- base_url: string (the root URL of the textbook site)

**Output**:
- List of strings (valid URLs discovered on the site)

**Errors**:
- NetworkError: If the base URL is unreachable
- InvalidURLError: If the provided URL is malformed

## Function: extract_text_from_urls
**Purpose**: Fetch content from provided URLs and extract clean text content

**Input**:
- urls: List of strings (URLs to extract text from)

**Output**:
- List of objects with properties:
  - url: string (source URL)
  - content: string (cleaned text content)
  - module: string (module name extracted from site structure)
  - section: string (section name extracted from site structure)

**Errors**:
- ContentExtractionError: If text extraction fails for a URL
- NetworkError: If a URL is unreachable

## Function: chunk_text
**Purpose**: Split large text content into smaller, semantically coherent chunks

**Input**:
- text: string (the text content to chunk)
- url: string (source URL for metadata)
- module: string (module name for metadata)
- section: string (section name for metadata)
- chunk_size: integer (maximum size of each chunk in characters, default 1000)

**Output**:
- List of objects with properties:
  - id: string (unique identifier for the chunk)
  - text: string (the chunked text content)
  - url: string (source URL)
  - module: string (module name)
  - section: string (section name)
  - position: integer (position of this chunk in the original text)

**Errors**:
- InvalidChunkSizeError: If chunk_size is not positive

## Function: embed
**Purpose**: Generate embeddings for text chunks using Cohere

**Input**:
- chunks: List of chunk objects (from chunk_text function)

**Output**:
- List of objects with properties:
  - chunk_id: string (id of the source chunk)
  - embedding: List of floats (the embedding vector)
  - metadata: object (source metadata: url, module, section)

**Errors**:
- EmbeddingGenerationError: If Cohere API call fails
- InvalidInputError: If input text is invalid for embedding

## Function: create_collection
**Purpose**: Create a Qdrant collection for storing embeddings

**Input**:
- collection_name: string (name for the collection, default "rag_embedding")
- vector_size: integer (dimension of the embedding vectors)
- distance_function: string (distance function for similarity search, default "Cosine")

**Output**:
- Boolean indicating success

**Errors**:
- CollectionCreationError: If collection already exists or creation fails

## Function: save_chunk_to_qdrant
**Purpose**: Save a single chunk with its embedding to Qdrant

**Input**:
- chunk_id: string (unique identifier for the chunk)
- embedding: List of floats (the embedding vector)
- metadata: object (metadata: url, module, section, etc.)
- collection_name: string (name of the collection to save to)

**Output**:
- Boolean indicating success

**Errors**:
- StorageError: If saving to Qdrant fails
- InvalidDataError: If the data format is incorrect

## Main Execution Flow
The main function will execute these functions in sequence:
1. get_all_urls(base_url) -> urls
2. extract_text_from_urls(urls) -> text_contents
3. For each text_content, chunk_text(text, url, module, section) -> chunks
4. embed(chunks) -> embedded_chunks
5. create_collection("rag_embedding")
6. For each embedded_chunk, save_chunk_to_qdrant(chunk_id, embedding, metadata)