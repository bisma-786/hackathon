"""
API router for the OpenAI agent endpoints
"""

from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from src.models.agent_models import AgentRequest, AgentResponse
from src.services.agent_service import AgentService
from src.lib.config import generate_request_id, setup_logging, format_error_response, ErrorCode
import logging
import html
import re

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create router
agent_router = APIRouter()

# Initialize services
agent_service = AgentService()

# Set up logging
logger = setup_logging()


def sanitize_query(query: str) -> str:
    """
    Sanitize the query input to prevent injection attacks
    """
    if not query:
        return query

    # Remove HTML tags
    query = html.escape(query)

    # Remove potentially dangerous patterns
    # This is a basic sanitization - in production, you might want more comprehensive validation
    query = re.sub(r'<script.*?>.*?</script>', '', query, flags=re.IGNORECASE | re.DOTALL)
    query = re.sub(r'javascript:', '', query, flags=re.IGNORECASE)
    query = re.sub(r'on\w+\s*=', '', query, flags=re.IGNORECASE)

    return query.strip()


@agent_router.post("/query", response_model=AgentResponse)
@limiter.limit("10/minute")  # Limit to 10 requests per minute per IP
async def query_agent(request: Request, agent_request: AgentRequest):
    """
    Process a natural language query and return a context-aware response
    """
    request_id = generate_request_id()
    logger.info(f"Request {request_id}: Processing agent query: {agent_request.query[:100]}...")

    try:
        # Validate the request
        if not agent_request.query or len(agent_request.query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        if len(agent_request.query) > 1000:  # Max length as per the model definition
            raise HTTPException(status_code=400, detail="Query is too long (max 1000 characters)")

        # Sanitize the query
        sanitized_query = sanitize_query(agent_request.query)
        agent_request.query = sanitized_query

        # Process the agent query
        response = agent_service.process_agent_query(agent_request)

        logger.info(f"Request {request_id}: Successfully processed agent query")
        return response

    except HTTPException:
        # Re-raise HTTP exceptions as they are
        raise
    except Exception as e:
        logger.error(f"Request {request_id}: Error processing agent query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing agent query: {str(e)}")


# Add rate limit exceeded handler
agent_router.app = None  # This will be set by main.py when the router is included


@agent_router.get("/health")
async def agent_health():
    """
    Health check endpoint for the agent service
    """
    try:
        # Test basic functionality
        # For now, just return that the service is available
        return {
            "status": "healthy",
            "service": "agent",
            "message": "Agent service is running"
        }
    except Exception as e:
        logger.error(f"Agent health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Agent service is not healthy")


# Function to setup rate limit handler (to be called from main.py)
def setup_rate_limiting(app):
    """
    Setup rate limiting for the application
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)