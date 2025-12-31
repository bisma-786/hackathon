"""
AI Agent with Retrieval-Augmented Generation Capabilities

This module implements a RAG agent using Google's Gemini API that retrieves
context from Qdrant to answer questions about book content.
"""

import os
import time
import uuid
import logging
from typing import List, Dict, Optional, Any
from pydantic import BaseModel
# Import required libraries
import google.generativeai as genai
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RetrievedChunk(BaseModel):
    """Model representing a retrieved content chunk from Qdrant."""
    id: str
    content: str
    score: float
    metadata: Dict[str, Any]


class QuerySession(BaseModel):
    """Model representing a conversation session with context history."""
    thread_id: str
    created_at: float
    last_accessed: float
    context_history: List[Dict[str, str]]


# Initialize Gemini client
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

# Dictionary to store session information (in production, use a proper database)
sessions: Dict[str, QuerySession] = {}





def create_session() -> str:
    """
    Create a new session and return the session ID.

    Returns:
        str: A new unique session ID
    """
    session_id = str(uuid.uuid4())
    sessions[session_id] = QuerySession(
        thread_id=session_id,
        created_at=time.time(),
        last_accessed=time.time(),
        context_history=[]
    )
    return session_id


def get_session(session_id: str) -> Optional[QuerySession]:
    """
    Get an existing session by ID.

    Args:
        session_id: The session ID to retrieve

    Returns:
        QuerySession if found, None otherwise
    """
    return sessions.get(session_id)


def update_session_context(session_id: str, query: str, response: str) -> None:
    """
    Update the context history for a session with the latest query and response.

    Args:
        session_id: The session ID to update
        query: The user's query
        response: The agent's response
    """
    session = get_session(session_id)
    if session:
        session.context_history.append({
            "query": query,
            "response": response,
            "timestamp": time.time()
        })
        session.last_accessed = time.time()


def cleanup_old_sessions(max_age_seconds: int = 3600) -> int:
    """
    Clean up sessions that are older than the specified age.

    Args:
        max_age_seconds: Maximum age of sessions in seconds (default: 1 hour)

    Returns:
        Number of sessions cleaned up
    """
    current_time = time.time()
    sessions_to_remove = []

    for session_id, session in sessions.items():
        if current_time - session.last_accessed > max_age_seconds:
            sessions_to_remove.append(session_id)

    for session_id in sessions_to_remove:
        del sessions[session_id]

    return len(sessions_to_remove)


def retrieve_chunks(query: str, top_k: int = 5) -> List[RetrievedChunk]:
    """
    Retrieve top-k relevant chunks from Qdrant based on the query using existing Spec-2 pipeline.

    This function reuses the existing retrieval pipeline from Spec-2 to maintain consistency
    and avoid duplication of effort.

    Args:
        query: The user's query to search for relevant content
        top_k: Number of top results to return (default: 5)

    Returns:
        List of RetrievedChunk objects containing relevant content
    """
    # Import the existing retrieval functionality from Spec-2
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # Add current directory to path
    from retrieve import search_qdrant

    # Perform the search using the existing pipeline
    results = search_qdrant(query_text=query, top_k=top_k)

    # Convert the results to our RetrievedChunk format
    retrieved_chunks = []
    for result in results.get("results", []):
        chunk = RetrievedChunk(
            id=result["metadata"]["chunk_id"],
            content=result["text_chunk"],
            score=result["similarity_score"],
            metadata=result["metadata"]
        )
        retrieved_chunks.append(chunk)

    return retrieved_chunks


def check_retrieved_content_quality(retrieved_chunks: List[RetrievedChunk], min_score: float = 0.1) -> Dict[str, Any]:
    """
    Check the quality of retrieved content and return validation results.

    Args:
        retrieved_chunks: List of retrieved chunks to validate
        min_score: Minimum score threshold for acceptable chunks

    Returns:
        Dictionary with validation results
    """
    total_chunks = len(retrieved_chunks)
    valid_chunks = [chunk for chunk in retrieved_chunks if chunk.score >= min_score]
    low_score_chunks = [chunk for chunk in retrieved_chunks if chunk.score < min_score]

    return {
        "total_chunks": total_chunks,
        "valid_chunks": len(valid_chunks),
        "low_score_chunks": len(low_score_chunks),
        "min_score_threshold": min_score,
        "has_valid_content": len(valid_chunks) > 0,
        "all_chunks_low_score": len(valid_chunks) == 0,
        "average_score": sum(chunk.score for chunk in retrieved_chunks) / total_chunks if total_chunks > 0 else 0
    }


def validate_input(query: str) -> Dict[str, Any]:
    """
    Validate the input query.

    Args:
        query: The query string to validate

    Returns:
        Dictionary with validation results
    """
    errors = []

    if not query:
        errors.append("Query cannot be empty")
    elif not isinstance(query, str):
        errors.append("Query must be a string")
    elif len(query.strip()) == 0:
        errors.append("Query cannot be empty or contain only whitespace")
    elif len(query) > 10000:  # Set a reasonable limit
        errors.append(f"Query is too long ({len(query)} characters), maximum allowed is 10000")

    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }


def health_check() -> Dict[str, Any]:
    """
    Perform a health check of the agent system.

    Returns:
        Dictionary with health status information
    """
    # Check if Gemini API key is configured
    gemini_api_configured = bool(os.getenv("GEMINI_API_KEY"))

    # Check if Qdrant is accessible by trying to import the retrieve module
    try:
        import sys
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # Add current directory to path
        import retrieve
        qdrant_accessible = True
    except ImportError:
        qdrant_accessible = False

    return {
        "status": "healthy" if gemini_api_configured and qdrant_accessible else "unhealthy",
        "dependencies": {
            "gemini": gemini_api_configured,
            "qdrant": qdrant_accessible
        },
        "timestamp": time.time()
    }


def answer_question(query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Answer a question using the RAG agent with retrieved context.

    Args:
        query: The question to answer
        session_id: Optional session ID for maintaining conversation context

    Returns:
        Dictionary containing the response and metadata
    """
    # Validate the input query
    validation_result = validate_input(query)
    if not validation_result["is_valid"]:
        return {
            "response": f"Error: {'; '.join(validation_result['errors'])}",
            "session_id": session_id,
            "source_chunks": [],
            "content_quality": {"has_valid_content": False},
            "query_time": time.time(),
            "error": validation_result["errors"]
        }

    # If no session ID provided, create a new session
    if session_id is None:
        session_id = create_session()

    # Get session context if it exists
    session = get_session(session_id)
    conversation_context = ""
    if session and session.context_history:
        conversation_context = "Previous conversation:\n"
        for item in session.context_history[-3:]:  # Include last 3 exchanges
            conversation_context += f"Q: {item['query']}\nA: {item['response']}\n\n"

    try:
        # Retrieve relevant chunks from Qdrant to get metadata and quality check (LIMIT RETRIEVAL SIZE)
        retrieved_chunks = retrieve_chunks(query, top_k=3)  # Maximum 3 chunks

        # Check the quality of retrieved content
        # Adjusted threshold based on observed scores from Qdrant (typically 0.03-0.06 range)
        content_quality = check_retrieved_content_quality(retrieved_chunks, min_score=0.02)

        # Initialize answer variable
        answer = ""

        # If we have a low quality result, return a message about it
        if content_quality["all_chunks_low_score"]:
            answer = f"I attempted to find relevant information about '{query}' in the book content, but no relevant content was found. I cannot answer this question based on the provided book content."
        else:
            # Prepare the context from retrieved chunks
            context_texts = [chunk.content for chunk in retrieved_chunks]
            context = "\n\n".join(context_texts)

            # Create the full context content
            full_context = f"""You are a Retrieval-Augmented Generation (RAG) assistant embedded in an AI-driven technical book.

You must answer user questions using ONLY the retrieved context provided to you.

Rules:
- The retrieved context is authoritative and trusted.
- You MUST attempt to answer using the retrieved content, even if it is partial.
- Do NOT refuse simply because the context is incomplete.
- If the context only partially answers the question, explain what can be inferred and clearly state limitations.
- Be helpful, explanatory, and instructional in tone.
- Never say 'I couldn't process your request' unless the retrieved context is completely empty.
- Do NOT hallucinate facts outside the retrieved context.

If retrieved content consists mainly of titles or section headers, explain what those sections likely cover and how they relate to the user's question.

CONTEXT:
{context}

PREVIOUS CONVERSATION (if any):
{conversation_context}

QUESTION:
{query}

Please provide an answer based only on the information in the CONTEXT above.
If the context does not contain information to answer the question, please say so explicitly."""

            # Instead of using file_search, directly inject the retrieved chunks into the prompt as plain text
            # Prepare the context from retrieved chunks (LIMIT RETRIEVAL SIZE)
            limited_chunks = retrieved_chunks[:3]  # Maximum 3 chunks
            context_texts = [f"Source {i+1}: {chunk.content}" for i, chunk in enumerate(limited_chunks)]

            # HARD TRUNCATE CONTEXT to max 4,000 characters
            full_context = "\\n\\n".join(context_texts)
            if len(full_context) > 4000:
                full_context = full_context[:4000]

            # SIMPLIFY THE PROMPT
            direct_prompt = f"""Answer the question strictly using the provided context.

RETRIEVED CONTEXT:
{full_context}

PREVIOUS CONVERSATION (if any):
{conversation_context}

USER QUESTION:
{query}

Answer:"""

            # Use the Gemini API to generate content
            response = model.generate_content(
                direct_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=1000,
                    temperature=0.3
                )
            )

            # Extract the answer from the response
            answer = response.text

            # Set thread and run to None since we're not using the assistants API
            thread = None
            run = None


        # Update session context with the new query and response
        update_session_context(session_id, query, answer)

        # Return the response with metadata - ENSURE CONSISTENT FORMAT
        return {
            "answer": answer,  # Use "answer" key to match API expectation
            "session_id": session_id,
            "source_chunks": [
                {
                    "id": chunk.id,
                    "content": chunk.content,
                    "score": chunk.score
                }
                for chunk in retrieved_chunks
            ],
            "content_quality": content_quality,
            "query_time": time.time()  # Using time.time() instead of API header which may not be available
        }

    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")  # LOG THE REAL ERROR

        # ADD EXPLICIT GEMINI ERROR HANDLING - Check for specific token/quota errors
        error_msg = str(e)
        if "quota" in error_msg.lower() or "rate" in error_msg.lower() or "limit" in error_msg.lower() or "token" in error_msg.lower():
            # Return graceful fallback message
            return {
                "answer": "The AI is temporarily unavailable due to usage limits. Please try again later.",
                "session_id": session_id,
                "source_chunks": [],
                "content_quality": {"has_valid_content": False},
                "query_time": time.time()
            }
        else:
            # Return other error message
            return {
                "answer": f"Sorry, there was an error processing your request: {str(e)}",
                "session_id": session_id,
                "source_chunks": [],
                "content_quality": {"has_valid_content": False},
                "query_time": time.time()
            }


if __name__ == "__main__":
    # Main execution block for testing
    print("RAG Agent initialized")

    # Test the health check
    print("\n--- Health Check ---")
    health_status = health_check()
    print(f"Health Status: {health_status}")

    # Test the agent with a sample query
    query = "What is ROS 2 and how does it work?"
    print(f"\nQuery: {query}")

    start_time = time.time()
    result = answer_question(query)
    end_time = time.time()

    print(f"Response: {result['response']}")
    print(f"Query time: {end_time - start_time:.2f} seconds")
    print(f"Number of source chunks used: {len(result['source_chunks'])}")
    print(f"Content quality: {result['content_quality']}")

    # Test follow-up question functionality
    print("\n--- Testing Follow-up Questions ---")
    session_id = result['session_id']

    follow_up_query = "Can you explain more about the communication mechanisms in ROS 2?"
    print(f"Follow-up Query: {follow_up_query}")

    start_time = time.time()
    follow_up_result = answer_question(follow_up_query, session_id=session_id)
    end_time = time.time()

    print(f"Follow-up Response: {follow_up_result['response']}")
    print(f"Follow-up Query time: {end_time - start_time:.2f} seconds")
    print(f"Session ID maintained: {follow_up_result['session_id'] == session_id}")

    # Test another follow-up to ensure context is preserved
    another_follow_up = "How does this relate to robotics applications?"
    print(f"\nAnother Follow-up Query: {another_follow_up}")

    start_time = time.time()
    another_result = answer_question(another_follow_up, session_id=session_id)
    end_time = time.time()

    print(f"Another Follow-up Response: {another_result['response']}")
    print(f"Another Query time: {end_time - start_time:.2f} seconds")
    print(f"Session ID maintained: {another_result['session_id'] == session_id}")

    # Test edge case: query with no relevant content
    print("\n--- Testing Edge Case: No Relevant Content ---")
    irrelevant_query = "What is the weather like on Mars today?"
    print(f"Query: {irrelevant_query}")

    start_time = time.time()
    irrelevant_result = answer_question(irrelevant_query)
    end_time = time.time()

    print(f"Response: {irrelevant_result['response']}")
    print(f"Query time: {end_time - start_time:.2f} seconds")
    print(f"Content quality: {irrelevant_result['content_quality']}")

    # Test edge case: empty query
    print("\n--- Testing Edge Case: Invalid Input ---")
    empty_query = ""
    print(f"Query: '{empty_query}'")

    empty_result = answer_question(empty_query)
    print(f"Response: {empty_result['response']}")

    # Test session cleanup
    print("\n--- Testing Session Cleanup ---")
    cleanup_count = cleanup_old_sessions(max_age_seconds=0)  # Clean up all sessions
    print(f"Cleaned up {cleanup_count} sessions")