# Tasks: Book URL Ingestion & Vector Indexing

**Feature**: Book URL Ingestion & Vector Indexing
**Branch**: 005-book-url-ingestion
**Created**: 2025-12-24
**Status**: Draft
**Input**: Implementation plan from `/specs/005-book-url-ingestion/plan.md`

## Implementation Strategy

**MVP Approach**: Implement User Story 1 (Vector Database Indexing) as the minimum viable product, which provides the complete end-to-end pipeline from URL discovery to vector storage. This enables the foundational capability for all downstream RAG workflows.

**Incremental Delivery**: Each user story builds upon the previous ones, with independent testability at each phase. User Story 2 (Content Extraction and Chunking) enhances the extraction pipeline, and User Story 3 (Metadata Preservation) ensures complete metadata accuracy.

## Dependencies

**User Story Completion Order**:
1. US1 (P1): Vector Database Indexing - Foundation for all other stories
2. US2 (P2): Content Extraction and Chunking - Enhances extraction quality
3. US3 (P3): Metadata Preservation - Ensures metadata completeness

**Parallel Execution Examples**:
- Within US1: URL discovery and content fetching can run in parallel with different URL batches
- Within US2: Content parsing and chunking can be parallelized per document
- Within US3: Metadata extraction can run in parallel with content processing

## Phase 1: Setup (Project Initialization)

- [X] T001 Create backend/ directory structure as specified in implementation plan
- [X] T002 Initialize Python project with uv and create pyproject.toml with dependencies
- [X] T003 [P] Create .env file template for environment variables (COHERE_API_KEY, QDRANT_URL, etc.)
- [X] T004 [P] Create .gitignore file with Python-specific ignores
- [X] T005 Create main.py entry point with basic structure
- [X] T006 Create src/ directory structure with subdirectories (ingestion, embedding, storage, utils)
- [X] T007 Create tests/ directory structure with subdirectories for each module
- [X] T008 [P] Install required dependencies: requests, beautifulsoup4, cohere, qdrant-client, lxml

## Phase 2: Foundational (Blocking Prerequisites)

- [X] T009 Implement configuration management in src/utils/config.py
- [X] T010 Implement logging utilities in src/utils/logger.py
- [X] T011 Implement data validation utilities in src/utils/validators.py
- [X] T012 [P] Create Qdrant client wrapper in src/storage/qdrant_client.py
- [X] T013 [P] Create ContentChunk model representation in src/models/content_chunk.py
- [X] T014 [P] Create BookPage model representation in src/models/book_page.py
- [X] T015 [P] Create VectorRecord model representation in src/models/vector_record.py

## Phase 3: User Story 1 - Vector Database Indexing (Priority: P1)

**Goal**: Internal RAG system components need to access indexed book content through vector storage. The system must crawl all public book URLs, extract content, generate embeddings, and store them with proper metadata in Qdrant Cloud.

**Independent Test**: Can be fully tested by running the ingestion pipeline and verifying that content from book URLs is successfully stored in Qdrant with correct metadata and embeddings.

- [X] T016 [US1] Implement URL discovery and fetching in src/ingestion/crawler.py
- [X] T017 [US1] Implement basic HTML content extraction in src/ingestion/parser.py
- [X] T018 [US1] Implement simple text chunking in src/ingestion/chunker.py
- [X] T019 [US1] Implement Cohere embedding generation in src/embedding/generator.py
- [X] T020 [US1] Implement vector storage operations in src/storage/vector_store.py
- [X] T021 [US1] Create main pipeline orchestration in main.py
- [X] T022 [US1] Implement basic metadata preservation (URL, module, section)
- [X] T023 [US1] Implement idempotent storage using content hash as ID
- [X] T024 [US1] [P] Add basic error handling and retry logic
- [X] T025 [US1] [P] Add logging for pipeline progress tracking
- [X] T026 [US1] Write basic tests for crawler functionality in tests/test_crawler.py
- [X] T027 [US1] Write basic tests for parser functionality in tests/test_parser.py
- [X] T028 [US1] Write basic tests for chunker functionality in tests/test_chunker.py
- [X] T029 [US1] Write basic tests for embedding functionality in tests/test_embeddings.py
- [X] T030 [US1] Write basic tests for storage functionality in tests/test_storage.py
- [X] T031 [US1] Test end-to-end pipeline with sample URLs

## Phase 4: User Story 2 - Content Extraction and Chunking (Priority: P2)

**Goal**: The system must extract readable textual content from book pages including headings, paragraphs, and relevant code blocks, then chunk this content deterministically with overlap to maintain context.

**Independent Test**: Can be tested by running content extraction on sample book pages and verifying that text, headings, and code blocks are properly identified and chunked with appropriate overlap.

- [X] T032 [US2] Enhance HTML content extraction to preserve heading hierarchy in src/ingestion/parser.py
- [X] T033 [US2] Implement code block extraction from HTML in src/ingestion/parser.py
- [X] T034 [US2] Improve content cleaning to remove navigation and boilerplate in src/ingestion/parser.py
- [X] T035 [US2] Implement configurable chunk size and overlap in src/ingestion/chunker.py
- [X] T036 [US2] Implement sliding window chunking with overlap in src/ingestion/chunker.py
- [X] T037 [US2] Add chunk validation to ensure consistent token counts in src/ingestion/chunker.py
- [X] T038 [US2] [P] Add performance optimization for large documents
- [X] T039 [US2] Update tests to verify heading preservation in tests/test_parser.py
- [X] T040 [US2] Update tests to verify code block extraction in tests/test_parser.py
- [X] T041 [US2] Update tests to verify chunk overlap in tests/test_chunker.py
- [X] T042 [US2] Test content extraction with complex book pages

## Phase 5: User Story 3 - Metadata Preservation (Priority: P3)

**Goal**: The system must preserve structural metadata including URL, module, section title, and heading hierarchy to enable contextual retrieval by downstream systems.

**Independent Test**: Can be tested by verifying that metadata fields (URL, module, section, heading hierarchy) are correctly captured and stored with each content chunk.

- [X] T043 [US3] Enhance metadata extraction to capture heading hierarchy in src/ingestion/parser.py
- [X] T044 [US3] Implement module and section detection from URL structure in src/ingestion/parser.py
- [X] T045 [US3] Update ContentChunk model to include complete metadata in src/models/content_chunk.py
- [X] T046 [US3] Update VectorRecord payload to include complete metadata in src/models/vector_record.py
- [X] T047 [US3] Enhance Qdrant storage to include all metadata in payload in src/storage/vector_store.py
- [X] T048 [US3] [P] Add metadata validation to ensure completeness
- [X] T049 [US3] [P] Add metadata integrity checks during storage
- [X] T050 [US3] Update tests to verify complete metadata preservation in tests/test_parser.py
- [X] T051 [US3] Update tests to verify metadata storage in tests/test_storage.py
- [X] T052 [US3] Test metadata preservation with complex document structures

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T053 Implement comprehensive error handling and graceful degradation
- [X] T054 Add rate limiting and exponential backoff for API calls
- [X] T055 Implement batch processing for embedding generation
- [X] T056 Add progress tracking and statistics reporting
- [X] T057 Implement re-run capability with idempotent operations
- [X] T058 Add command-line argument parsing for pipeline configuration
- [X] T059 Write comprehensive tests covering edge cases
- [X] T060 Add documentation for the ingestion pipeline
- [X] T061 Perform end-to-end testing with full book corpus
- [X] T062 Verify all success criteria from specification are met