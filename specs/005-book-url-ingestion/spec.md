# Feature Specification: Book URL Ingestion & Vector Indexing

**Feature Branch**: `005-book-url-ingestion`
**Created**: 2025-12-24
**Status**: Draft
**Input**: User description: "— Spec-1: Book URL Ingestion & Vector Indexing

Objective:
Ingest all deployed AI-Driven Book website URLs, generate semantic embeddings, and store them in a vector database to enable reliable retrieval for downstream RAG workflows.

Target users:
Internal RAG system components (retrieval pipeline, agent layer).

Scope:

Discover and crawl all public book URLs deployed on GitHub Pages

Extract readable textual content (headings, paragraphs, code blocks where relevant)

Preserve structural metadata:

URL

Module

Section / page title

Heading hierarchy

Chunk content deterministically with overlap

Generate embeddings using Cohere embedding models

Store vectors and metadata in Qdrant Cloud

Functional Requirements

Each chunk must have:

id

text

embedding

url

module

section

Chunking must be repeatable and deterministic

Vector insertion must be idempotent (safe to re-run)

Non-Functional Requirements:

Embedding generation must handle the full book corpus without failure

Vector storage must scale to ≥10,000 chunks

Metadata accuracy must be 100% (no orphaned vectors)

Success Criteria:

All book URLs are indexed in Qdrant

Each vector is retrievable with correct metadata

Re-running ingestion does not create duplicates

A sample similarity query returns relevant book sections

Constraints:

Embeddings: Cohere (no OpenAI embeddings)

Vector DB: Qdrant Cloud (free tier)

Backend language: Python

No retrieval or generation logic in this spec

Not Building:

Retrieval pipelines

Validation tests

Agent or LLM prompts

Frontend or API integration"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Vector Database Indexing (Priority: P1)

Internal RAG system components need to access indexed book content through vector storage. The system must crawl all public book URLs, extract content, generate embeddings, and store them with proper metadata in Qdrant Cloud.

**Why this priority**: This is the foundational capability that enables all downstream RAG workflows. Without properly indexed content, retrieval and generation systems cannot function.

**Independent Test**: Can be fully tested by running the ingestion pipeline and verifying that content from book URLs is successfully stored in Qdrant with correct metadata and embeddings.

**Acceptance Scenarios**:

1. **Given** a list of book URLs deployed on GitHub Pages, **When** the ingestion process runs, **Then** all content is extracted and stored as vectors in Qdrant Cloud with proper metadata
2. **Given** previously indexed content exists in Qdrant, **When** the ingestion process runs again, **Then** no duplicate entries are created and existing entries are updated appropriately

---

### User Story 2 - Content Extraction and Chunking (Priority: P2)

The system must extract readable textual content from book pages including headings, paragraphs, and relevant code blocks, then chunk this content deterministically with overlap to maintain context.

**Why this priority**: Proper content extraction and chunking is essential for effective retrieval. Without well-structured chunks, downstream RAG systems won't be able to retrieve relevant information effectively.

**Independent Test**: Can be tested by running content extraction on sample book pages and verifying that text, headings, and code blocks are properly identified and chunked with appropriate overlap.

**Acceptance Scenarios**:

1. **Given** a book page with headings, paragraphs, and code blocks, **When** the extraction process runs, **Then** all relevant content is captured while preserving structural information
2. **Given** a long book section, **When** the chunking process runs, **Then** content is split into manageable chunks with appropriate overlap to maintain context

---

### User Story 3 - Metadata Preservation (Priority: P3)

The system must preserve structural metadata including URL, module, section title, and heading hierarchy to enable contextual retrieval by downstream systems.

**Why this priority**: Accurate metadata is critical for users of the RAG system to understand the context and source of retrieved information.

**Independent Test**: Can be tested by verifying that metadata fields (URL, module, section, heading hierarchy) are correctly captured and stored with each content chunk.

**Acceptance Scenarios**:

1. **Given** content extracted from a book page, **When** metadata preservation runs, **Then** URL, module, and section information is accurately captured
2. **Given** content with heading hierarchy, **When** the system processes it, **Then** heading relationships are preserved in the metadata

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- What happens when a book URL is temporarily unavailable during crawling?
- How does the system handle extremely large book pages that exceed reasonable chunk sizes?
- What occurs when the Qdrant Cloud service is unavailable during ingestion?
- How does the system handle malformed HTML or non-standard content structures?
- What happens if the Cohere embedding service returns errors or rate limits?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST crawl all public book URLs deployed on GitHub Pages
- **FR-002**: System MUST extract readable textual content including headings, paragraphs, and relevant code blocks
- **FR-003**: System MUST preserve structural metadata (URL, module, section, heading hierarchy)
- **FR-004**: System MUST chunk content deterministically with overlap to maintain context
- **FR-005**: System MUST generate semantic embeddings using Cohere embedding models
- **FR-006**: System MUST store vectors and metadata in Qdrant Cloud
- **FR-007**: Each content chunk MUST have id, text, embedding, url, module, and section fields
- **FR-008**: Chunking process MUST be repeatable and deterministic across runs
- **FR-009**: Vector insertion MUST be idempotent (safe to re-run without creating duplicates)
- **FR-010**: System MUST handle the full book corpus without failure during embedding generation

### Key Entities *(include if feature involves data)*

- **Content Chunk**: Represents a segment of book content with text, embedding vector, and metadata (URL, module, section, id)
- **Book Page**: Represents a single book page with URL, module, section title, and heading hierarchy
- **Vector Record**: Represents an indexed item in Qdrant with embedding vector and associated metadata

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All book URLs are successfully indexed in Qdrant Cloud without data loss
- **SC-002**: Each vector is retrievable with 100% accuracy of associated metadata
- **SC-003**: Re-running ingestion process does not create duplicate entries in the vector database
- **SC-004**: A sample similarity query returns relevant book sections with high precision and recall
- **SC-005**: System can handle ≥10,000 content chunks in the vector database
- **SC-006**: Metadata accuracy is maintained at 100% (no orphaned vectors without proper metadata)
- **SC-007**: Embedding generation completes successfully for the full book corpus
