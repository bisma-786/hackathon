# Quickstart: Qdrant Retrieval & Validation Pipeline

## Overview
This guide will help you set up and run the Qdrant retrieval and validation pipeline that connects to Qdrant Cloud, performs semantic similarity searches on stored book embeddings, and validates results.

## Prerequisites
- Python 3.11 or higher
- Access to Qdrant Cloud instance with existing embeddings from Spec-1
- Cohere API key for generating query embeddings
- Existing vector collection in Qdrant with book content embeddings

## Setup

### 1. Install Dependencies
```bash
pip install qdrant-client cohere python-dotenv
```

### 2. Configure Environment Variables
Create a `.env` file in the project root with the following variables:
```env
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_api_key
COLLECTION_NAME=your_collection_name
COHERE_API_KEY=your_cohere_api_key
```

### 3. Verify Qdrant Connection
Ensure your Qdrant Cloud instance is accessible and the target collection exists with stored embeddings from Spec-1.

## Usage

### Run the Retrieval Script
```bash
cd backend
python retrieve.py
```

The script will:
1. Connect to Qdrant Cloud using the configured credentials
2. Load a test query (either hardcoded or passed as a command-line argument)
3. Generate embeddings for the query using the Cohere model
4. Perform a top-K similarity search against the Qdrant collection
5. Print retrieved text chunks with associated metadata (URL, module, section)
6. Log similarity scores for each result
7. Measure and report response time
8. Validate metadata alignment with original sources

### Custom Query
To run with a custom query, you can modify the script to accept command-line arguments:
```bash
python retrieve.py --query "your search query here" --top-k 5
```

## Expected Output
The script will display:
- Retrieved text chunks relevant to the query
- Source URLs and metadata (module, section) for each chunk
- Similarity scores for each result
- Performance metrics (response time)
- Validation results confirming metadata alignment

## Validation Checks Performed
- Connection to Qdrant Cloud successful
- Query embedding generation successful
- Top-K search completed without errors
- Retrieved content has valid metadata
- Source URLs are properly formatted
- Response time within 5-second threshold
- Consistent results across multiple runs (deterministic behavior)