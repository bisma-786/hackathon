"""
FastAPI server for RAG Chatbot integration with Docusaurus frontend.
Exposes a /query endpoint that integrates with the existing RAG agent.
"""
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="RAG Chatbot API",
    description="API for integrating RAG chatbot with Docusaurus frontend",
    version="1.0.0"
)

# Add CORS middleware to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",     # Standard Docusaurus port
        "http://127.0.0.1:3000",
        "http://localhost:3001",     # Alternative Docusaurus port
        "http://127.0.0.1:3001",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)




# Pydantic models
class QueryRequest(BaseModel):
    """Model representing a query request from the frontend"""
    query: str = Field(..., min_length=1, max_length=10000)
    session_id: Optional[str] = None


class MinimalResponse(BaseModel):
    """Minimal response model that matches frontend expectation"""
    answer: str


# Import the RAG agent functionality
import sys
import os
# Add the backend directory to the path so we can import agent
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import answer_question


@app.get("/")
def read_root():
    return {"message": "RAG Chatbot API is running"}


@app.post("/query", response_model=MinimalResponse)
async def query_endpoint(request: QueryRequest):
    """
    Process a user query through the RAG agent and return a response.

    Args:
        request: QueryRequest containing the user's question and optional session ID

    Returns:
        MinimalResponse with just the answer field as expected by frontend
    """
    try:
        # Call the existing RAG agent functionality
        result = answer_question(query=request.query, session_id=request.session_id)

        # Ensure we always return the correct answer field and handle both 'answer' and 'response' keys
        answer_text = result.get("answer", result.get("response", "I couldn't process your request. Please try again."))

        # Ensure answer is a string and JSON-safe
        if not isinstance(answer_text, str):
            answer_text = str(answer_text)

        # Remove any potential problematic characters for JSON
        answer_text = answer_text.replace('\n', '\\n').replace('\r', '\\r')

        # Return only the answer field as expected by frontend
        return MinimalResponse(answer=answer_text)
    except Exception as e:
        # LOG THE REAL ERROR for debugging
        print(f"Error in query_endpoint: {str(e)}")

        # HARDEN BACKEND - ALWAYS return HTTP 200 with correct format
        return MinimalResponse(answer="Shut the fuck up and try again")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)