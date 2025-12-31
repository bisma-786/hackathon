# Quickstart: AI Agent with Retrieval-Augmented Capabilities

## Prerequisites
- Python 3.11+
- OpenAI API key
- Qdrant instance with book content indexed
- Access to Spec-2 retrieval pipeline

## Setup
1. Install dependencies:
   ```bash
   pip install openai qdrant-client pydantic cohere
   ```

2. Set environment variables:
   ```bash
   export OPENAI_API_KEY="your-api-key"
   export QDRANT_HOST="your-qdrant-host"
   export QDRANT_PORT="6333"
   ```

## Running the Agent
1. Navigate to the backend directory:
   ```bash
   cd backend/
   ```

2. Run the agent:
   ```bash
   python agent.py
   ```

## Basic Usage
The agent can be used in two ways:

1. **Direct function call**:
   ```python
   from agent import answer_question
   response = answer_question("Your question about the book")
   print(response)
   ```

2. **Interactive mode** (if implemented):
   ```bash
   python agent.py --interactive
   ```

## Testing
Run the test suite:
```bash
pytest tests/test_agent.py
```

## Configuration
The agent uses the following default parameters:
- top_k: 5 (number of chunks to retrieve)
- model: gpt-4-turbo (OpenAI model to use)
- temperature: 0.1 (for consistent responses)

These can be modified in the agent.py file as needed.