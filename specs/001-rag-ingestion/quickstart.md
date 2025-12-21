# Quickstart Guide: RAG Content Ingestion Pipeline

## Prerequisites

- Python 3.11 or higher
- UV package manager
- Cohere API key
- Qdrant Cloud API key and endpoint URL

## Setup

### 1. Create Backend Directory
```bash
mkdir backend && cd backend
```

### 2. Initialize Project with UV
```bash
uv init
```

### 3. Install Dependencies
```bash
uv add requests beautifulsoup4 cohere qdrant-client python-dotenv
```

### 4. Set up Environment Variables
Create a `.env` file with:
```env
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_URL=your_qdrant_cluster_url_here
TEXTBOOK_BASE_URL=https://ai-driven-humanoid-robotics-textboo-chi.vercel.app/
```

## Running the Pipeline

### 1. Create main.py with the required functions
The main.py file should contain all the required functions:
- get_all_urls
- extract_text_from_urls
- chunk_text
- embed
- create_collection
- save_chunk_to_qdrant

### 2. Execute the pipeline
```bash
cd backend
python main.py
```

## Expected Output

The pipeline will:
1. Crawl all pages from the textbook website
2. Extract clean text from each page
3. Chunk the text appropriately
4. Generate embeddings using Cohere
5. Create a "rag_embedding" collection in Qdrant
6. Store all embeddings with metadata in Qdrant
7. Generate logs and validation reports

## Verification

After execution, verify:
- All textbook pages were processed (check logs)
- Embeddings are stored in Qdrant collection
- Metadata (URL, module, section) is preserved
- Pipeline is idempotent (safe to run again)