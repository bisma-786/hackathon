# Quickstart: Book URL Ingestion & Vector Indexing

## Overview
This quickstart guide helps you set up and run the Book URL Ingestion & Vector Indexing pipeline. The pipeline discovers book URLs, extracts content, generates embeddings, and stores them in Qdrant Cloud.

## Prerequisites
- Python 3.11 or higher
- `uv` package manager
- Cohere API key
- Qdrant Cloud cluster URL and API key

## Setup

### 1. Clone and Navigate to Backend Directory
```bash
cd backend
```

### 2. Install Dependencies with uv
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

Or if using pyproject.toml:
```bash
uv sync
```

### 3. Configure Environment Variables
Create a `.env` file in the backend directory:

```env
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_URL=your_qdrant_cluster_url_here
QDRANT_API_KEY=your_qdrant_api_key_here
BOOK_BASE_URL=https://your-book-site.github.io
QDRANT_COLLECTION_NAME=book_content_chunks
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

## Running the Pipeline

### 1. Basic Execution
```bash
cd backend
python main.py
```

### 2. With Custom Configuration
```bash
cd backend
python main.py --config-path ./config.yaml
```

### 3. Command Line Options
```bash
python main.py --help
```

Common options:
- `--base-url`: Base URL of the book site (default from .env)
- `--collection`: Qdrant collection name (default from .env)
- `--chunk-size`: Size of text chunks (default: 1000)
- `--chunk-overlap`: Overlap between chunks (default: 200)
- `--rebuild`: Rebuild the entire index (default: false)

## Pipeline Phases

### Phase 1: URL Discovery
```bash
# Discover all book URLs from the base URL
python -m src.ingestion.crawler --discover
```

### Phase 2: Content Extraction
```bash
# Extract content from discovered URLs
python -m src.ingestion.parser --extract
```

### Phase 3: Text Chunking
```bash
# Chunk extracted content with overlap
python -m src.ingestion.chunker --chunk
```

### Phase 4: Embedding Generation
```bash
# Generate embeddings for all chunks
python -m src.embedding.generator --generate
```

### Phase 5: Vector Storage
```bash
# Store vectors in Qdrant Cloud
python -m src.storage.vector_store --store
```

## Verification

### 1. Check Stored Vectors
```bash
# Verify vector count and metadata
python -c "
from src.storage.qdrant_client import QdrantClient
client = QdrantClient()
count = client.get_vector_count()
print(f'Vectors stored: {count}')
"
```

### 2. Sample Similarity Query
```bash
# Test similarity search functionality
python -c "
from src.storage.qdrant_client import QdrantClient
client = QdrantClient()
query = 'sample search query about AI'
results = client.search_similar(query, limit=5)
print(f'Found {len(results)} similar chunks')
for i, result in enumerate(results):
    print(f'{i+1}. {result[\"text_preview\"][:100]}...')
"
```

### 3. Pipeline Statistics
```bash
# Get ingestion statistics
python -c "
from src.utils.logger import get_ingestion_stats
stats = get_ingestion_stats()
print(f'Pages processed: {stats[\"pages\"]}')
print(f'Chunks created: {stats[\"chunks\"]}')
print(f'Embeddings generated: {stats[\"embeddings\"]}')
print(f'Errors: {stats[\"errors\"]}')
"
```

## Troubleshooting

### Common Issues

#### 1. API Rate Limits
- **Issue**: Cohere or Qdrant rate limit errors
- **Solution**: Implement exponential backoff in batch processing

#### 2. Memory Issues
- **Issue**: High memory usage during embedding generation
- **Solution**: Process in smaller batches using the `--batch-size` option

#### 3. Connection Issues
- **Issue**: Cannot connect to Qdrant Cloud
- **Solution**: Verify URL and API key in `.env` file

### Debugging
Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python main.py
```

## Next Steps

1. **Production Deployment**: Configure for scheduled runs using cron or a task scheduler
2. **Monitoring**: Set up logging and monitoring for the pipeline
3. **Validation**: Implement validation tests for content accuracy
4. **Scaling**: Adjust batch sizes and parallelism for larger book collections