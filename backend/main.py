"""
Main application file that supports both the RAG ingestion pipeline and the new FastAPI agent API.
This file serves as the entry point for the FastAPI application while preserving the original ingestion functionality.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import os
import sys
from typing import Optional

# Initialize FastAPI app
app = FastAPI(
    title="AI-Driven Robotics Textbook RAG API",
    description="API for retrieving vector embeddings and querying textbook content via OpenAI agent",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers after app creation to avoid circular imports
try:
    from src.api.agent_router import agent_router, setup_rate_limiting
    from src.api.retrieval_router import retrieval_router

    # Include routers
    app.include_router(agent_router, prefix="/api/agent", tags=["agent"])
    app.include_router(retrieval_router, prefix="/api", tags=["retrieval"])

    # Setup rate limiting
    setup_rate_limiting(app)

    # Health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check():
        return {
            "status": "healthy",
            "message": "AI-Driven Robotics Textbook RAG API is running"
        }

except ImportError as e:
    logging.error(f"Error importing routers: {e}")
    # Define minimal health check if imports fail
    @app.get("/health", tags=["health"])
    async def health_check():
        return {
            "status": "starting",
            "message": f"Service starting, import error: {str(e)}"
        }

def run_ingestion_pipeline():
    """
    Function to run the original RAG ingestion pipeline when called directly.
    This preserves the original functionality of the main.py file.
    """
    # Import the original pipeline functions
    from main_ingestion import main as ingestion_main

    # Run the original ingestion pipeline
    ingestion_main()

if __name__ == "__main__":
    # Check if we're running in ingestion mode or API mode
    if len(sys.argv) > 1 and sys.argv[1] == "ingest":
        # Run the original ingestion pipeline
        run_ingestion_pipeline()
    else:
        # Run the FastAPI application
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)