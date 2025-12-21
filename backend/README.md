# RAG Vector Retrieval and Validation System

This system provides comprehensive vector retrieval and validation capabilities for RAG (Retrieval-Augmented Generation) systems. It enables retrieval of vectors from Qdrant by URL, module, or section, with extensive validation of metadata integrity and embedding quality.

## Features

- **Vector Retrieval**: Retrieve vectors by URL, module, or section identifiers
- **OpenAI Agent Integration**: Natural language query processing with RAG functionality
- **Metadata Validation**: Validate that all metadata fields are preserved correctly
- **Similarity Testing**: Validate embedding quality using cosine similarity
- **Comprehensive Validation**: End-to-end validation of the entire retrieval pipeline
- **Performance Monitoring**: Track response times and system performance
- **Scalability Testing**: Validate system performance with large datasets (10,000+ vectors)

## Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your environment variables by copying `.env.example` to `.env` and filling in your values:
   ```bash
   cp .env.example .env
   # Edit .env with your Qdrant and Cohere credentials
   ```

## Usage

### CLI Commands

#### Vector Retrieval

Retrieve vectors by URL:
```bash
python -m src.cli.retrieval_cli retrieve-by-url --url "https://example.com/page"
```

Retrieve vectors by module:
```bash
python -m src.cli.retrieval_cli retrieve-by-module --module "module-name"
```

Retrieve vectors by section:
```bash
python -m src.cli.retrieval_cli retrieve-by-section --section "section-name"
```

All retrieval commands support pagination:
```bash
python -m src.cli.retrieval_cli retrieve-by-url --url "https://example.com/page" --limit 50 --offset 0
```

#### Validation

Validate metadata integrity:
```bash
python -m src.cli.retrieval_cli validate-metadata --url "https://example.com/page"
```

Validate embedding similarity:
```bash
python -m src.cli.retrieval_cli validate-similarity --url "https://example.com/page" --count 20
```

Run comprehensive validation:
```bash
python -m src.cli.retrieval_cli validate-comprehensive --url "https://example.com/page"
```

### Script Usage

#### Run Validation Scripts

Run comprehensive validation:
```bash
python scripts/validate_retrieval.py --url "https://example.com/page" --output reports/validation_report.json
```

Run similarity checks:
```bash
python scripts/run_similarity_checks.py --url "https://example.com/page" --count 50 --output reports/similarity_report.json
```

Run performance tests:
```bash
python scripts/performance_test.py --url "https://example.com/page" --requests 100 --concurrency 10
```

Run reliability tests (simulation mode):
```bash
python scripts/reliability_test.py --url "https://example.com/page" --simulate
```

Run scalability tests:
```bash
python scripts/scalability_test.py --url "https://example.com/page" --target 10000
```

Run comprehensive NFR validation:
```bash
python scripts/nfr_validation.py --url "https://example.com/page"
```

## API Usage Examples

### Running the API Server

Start the FastAPI server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Agent Query Examples

Ask a question to the AI agent:
```bash
curl -X POST http://localhost:8000/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the key principles of embodied cognition in robotics?",
    "instructions": "You are an AI assistant for the AI-Driven Robotics Textbook. Answer questions based on the provided context.",
    "temperature": 0.7,
    "max_tokens": 150
  }'
```

### Vector Retrieval Examples

Retrieve vectors by URL:
```bash
curl -G \
  --data-urlencode "url=https://example.com/textbook/module1" \
  http://localhost:8000/api/vectors/by-url
```

Retrieve vectors by module:
```bash
curl -G \
  --data-urlencode "module=embodied_cognition" \
  http://localhost:8000/api/vectors/by-module
```

Retrieve vectors by section:
```bash
curl -G \
  --data-urlencode "section=pid_control" \
  http://localhost:8000/api/vectors/by-section
```

Perform semantic search:
```bash
curl -G \
  --data-urlencode "query=PID control in robotics" \
  -d "limit=5" \
  http://localhost:8000/api/vectors/semantic-search
```

### Validation Examples

Check validation status:
```bash
curl http://localhost:8000/api/validation/status
```

Get validation report:
```bash
curl http://localhost:8000/api/validation/report
```

Check health:
```bash
curl http://localhost:8000/health
```

## Architecture

The system is organized into the following components:

- **Models**: Data classes for VectorRecord and ValidationReport
- **Services**:
  - QdrantRetrievalService: Handles vector retrieval operations
  - ValidationService: Manages metadata and comprehensive validation
  - SimilarityService: Performs embedding similarity calculations
- **CLI**: Command-line interface for all operations
- **Config**: Environment configuration and logging setup
- **Scripts**: Standalone validation and testing scripts
- **Tests**: Unit and integration tests

## Environment Variables

- `QDRANT_URL`: URL for your Qdrant instance
- `QDRANT_API_KEY`: API key for Qdrant authentication
- `QDRANT_COLLECTION_NAME`: Name of the collection to use (default: "vectors")
- `COHERE_API_KEY`: API key for Cohere services
- `SIMILARITY_THRESHOLD`: Minimum similarity threshold (default: 0.8)

## Non-Functional Requirements

### Performance
- 95% of retrieval requests respond within 5 seconds
- Support for concurrent requests
- Performance metrics collection

### Reliability
- 99% uptime over defined time windows
- Graceful error handling and degradation
- Comprehensive logging

### Scalability
- Handle 10,000+ vector chunks in single validation run
- Efficient retrieval algorithms
- Memory-efficient processing

## Testing

Run unit tests:
```bash
pytest tests/unit/
```

Run integration tests:
```bash
pytest tests/integration/
```

Run all tests:
```bash
pytest tests/
```

## Data Model

### VectorRecord
- `id`: Unique identifier for the vector
- `embedding`: Vector embedding data (list of floats)
- `metadata`: Dictionary containing:
  - `url`: Source URL
  - `module`: Module identifier
  - `section`: Section identifier
  - `position`: Position in document sequence
  - `hash`: Content hash for idempotency
  - `source_text`: Original text content
- `timestamps`: Ingestion and retrieval timestamps

### ValidationReport
- `id`: Unique report identifier
- `timestamp`: When the validation was performed
- `summary`: Overall validation statistics
- `details`: Individual validation results
- `errors`: List of validation errors
- `metrics`: Performance and quality metrics