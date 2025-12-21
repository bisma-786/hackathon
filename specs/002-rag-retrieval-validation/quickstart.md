# Quickstart Guide: RAG Vector Retrieval and Validation System

## Overview
This guide provides instructions to quickly set up and run the RAG vector retrieval and validation system. This system allows you to retrieve vectors from Qdrant by URL, module, or section, and validate the integrity of your RAG pipeline.

## Prerequisites
- Python 3.11 or higher
- Access to Qdrant vector database (with vectors from Spec 1)
- Cohere API key for similarity checks
- Git for version control

## Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ai-driven-book
```

### 2. Navigate to Backend Directory
```bash
cd backend
```

### 3. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Create a `.env` file in the backend directory:
```bash
cp .env.example .env
```

Edit the `.env` file and add your configuration:
```
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
COHERE_API_KEY=your_cohere_api_key
QDRANT_COLLECTION_NAME=your_collection_name
```

## Usage

### 1. Run Vector Retrieval
To retrieve vectors by URL:
```bash
python -m src.cli.retrieval_cli --by-url "https://example.com/docs/intro"
```

To retrieve vectors by module:
```bash
python -m src.cli.retrieval_cli --by-module "introduction"
```

To retrieve vectors by section:
```bash
python -m src.cli.retrieval_cli --by-section "overview"
```

### 2. Run Validation
To perform comprehensive validation:
```bash
python scripts/validate_retrieval.py --validation-type comprehensive
```

To perform metadata integrity validation:
```bash
python scripts/validate_retrieval.py --validation-type metadata_integrity
```

To perform similarity checks:
```bash
python scripts/run_similarity_checks.py --threshold 0.8
```

### 3. Using the API
Start the API server:
```bash
python -m src.api.server
```

Then make requests to the endpoints:
```bash
# Retrieve vectors by URL
curl "http://localhost:8000/vectors/by-url?url=https://example.com/docs/intro"

# Run validation
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{"validation_type": "comprehensive"}'
```

## Key Components

### Models
- `VectorRecord`: Represents a single vector chunk with metadata
- `ValidationReport`: Contains results of validation operations

### Services
- `QdrantRetrievalService`: Handles all Qdrant interactions
- `ValidationService`: Performs validation checks
- `SimilarityService`: Handles embedding similarity comparisons

### Scripts
- `validate_retrieval.py`: Main validation script
- `run_similarity_checks.py`: Performs similarity validation

## Testing
Run unit tests:
```bash
pytest tests/unit/
```

Run integration tests:
```bash
pytest tests/integration/
```

## Troubleshooting

### Common Issues
1. **Qdrant Connection Error**: Verify your QDRANT_URL and QDRANT_API_KEY are correct
2. **Cohere API Error**: Check your COHERE_API_KEY is valid
3. **No Vectors Found**: Ensure vectors were ingested in Spec 1

### Validation Reports
Validation reports are stored in the `validation_reports/` directory and contain detailed information about validation runs, including success rates, errors, and performance metrics.