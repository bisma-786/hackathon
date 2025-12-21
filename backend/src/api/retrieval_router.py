"""
API router for the retrieval endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from src.models.api_models import VectorListResponse
from src.services.qdrant_service import QdrantService
from src.services.retrieval_service import RetrievalValidationService
from src.lib.config import generate_request_id, setup_logging, format_error_response, ErrorCode
import logging
import html
import re

# Create router
retrieval_router = APIRouter()

# Initialize services
qdrant_service = QdrantService()
validation_service = RetrievalValidationService()

def sanitize_text_input(text: str) -> str:
    """
    Sanitize text input to prevent injection attacks
    """
    if not text:
        return text

    # Remove HTML tags
    text = html.escape(text)

    # Remove potentially dangerous patterns
    # This is a basic sanitization - in production, you might want more comprehensive validation
    text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)

    return text.strip()


# Set up logging
logger = setup_logging()


@retrieval_router.get("/vectors/by-url", response_model=VectorListResponse)
async def retrieve_by_url(
    url: str = Query(..., description="URL to retrieve vectors for"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of vectors to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    Retrieve all vector chunks associated with a specific URL
    """
    request_id = generate_request_id()
    logger.info(f"Request {request_id}: Retrieving vectors for URL: {url}")

    try:
        # Process the retrieval request
        result = qdrant_service.retrieve_by_url(url, limit=limit, offset=offset)

        logger.info(f"Request {request_id}: Successfully retrieved {result.total_count} vectors for URL")
        return result

    except ValueError as e:
        logger.warning(f"Request {request_id}: Invalid URL provided: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid URL: {str(e)}")
    except Exception as e:
        logger.error(f"Request {request_id}: Error retrieving vectors by URL: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving vectors: {str(e)}")


@retrieval_router.get("/vectors/by-module", response_model=VectorListResponse)
async def retrieve_by_module(
    module: str = Query(..., description="Module to retrieve vectors for"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of vectors to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    Retrieve all vector chunks associated with a specific module
    """
    request_id = generate_request_id()
    logger.info(f"Request {request_id}: Retrieving vectors for module: {module}")

    try:
        # Process the retrieval request
        result = qdrant_service.retrieve_by_module(module, limit=limit, offset=offset)

        logger.info(f"Request {request_id}: Successfully retrieved {result.total_count} vectors for module")
        return result

    except ValueError as e:
        logger.warning(f"Request {request_id}: Invalid module provided: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid module: {str(e)}")
    except Exception as e:
        logger.error(f"Request {request_id}: Error retrieving vectors by module: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving vectors: {str(e)}")


@retrieval_router.get("/vectors/by-section", response_model=VectorListResponse)
async def retrieve_by_section(
    section: str = Query(..., description="Section to retrieve vectors for"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of vectors to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    Retrieve all vector chunks associated with a specific section
    """
    request_id = generate_request_id()
    logger.info(f"Request {request_id}: Retrieving vectors for section: {section}")

    try:
        # Process the retrieval request
        result = qdrant_service.retrieve_by_section(section, limit=limit, offset=offset)

        logger.info(f"Request {request_id}: Successfully retrieved {result.total_count} vectors for section")
        return result

    except ValueError as e:
        logger.warning(f"Request {request_id}: Invalid section provided: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid section: {str(e)}")
    except Exception as e:
        logger.error(f"Request {request_id}: Error retrieving vectors by section: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving vectors: {str(e)}")


@retrieval_router.get("/vectors/semantic-search", response_model=VectorListResponse)
async def semantic_search(
    query: str = Query(..., min_length=1, max_length=500, description="Query text for semantic search"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of vectors to return"),
    min_similarity: float = Query(0.5, ge=0.0, le=1.0, description="Minimum similarity threshold")
):
    """
    Perform semantic search using the query text to find similar content
    """
    request_id = generate_request_id()

    # Sanitize the query input
    sanitized_query = sanitize_text_input(query)

    logger.info(f"Request {request_id}: Performing semantic search with query: {sanitized_query[:100]}...")

    try:
        # Process the semantic search request with sanitized query
        result = qdrant_service.semantic_search(query_text=sanitized_query, limit=limit, min_similarity=min_similarity)

        logger.info(f"Request {request_id}: Semantic search returned {result.total_count} vectors")
        return result

    except Exception as e:
        logger.error(f"Request {request_id}: Error performing semantic search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error performing semantic search: {str(e)}")


@retrieval_router.get("/validation/status")
async def validation_status():
    """
    Validation endpoint to check the status of vector storage in Qdrant
    """
    request_id = generate_request_id()
    logger.info(f"Request {request_id}: Checking validation status")

    try:
        # Perform validation check
        result = validation_service.validate_vector_storage()

        logger.info(f"Request {request_id}: Validation status check completed")
        return result

    except Exception as e:
        logger.error(f"Request {request_id}: Error during validation status check: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during validation: {str(e)}")


@retrieval_router.get("/validation/report")
async def validation_report():
    """
    Validation endpoint to generate a comprehensive validation report
    """
    request_id = generate_request_id()
    logger.info(f"Request {request_id}: Generating validation report")

    try:
        # Generate validation report
        report = validation_service.generate_validation_report()

        logger.info(f"Request {request_id}: Validation report generated")
        return report

    except Exception as e:
        logger.error(f"Request {request_id}: Error generating validation report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating validation report: {str(e)}")


@retrieval_router.get("/health")
async def retrieval_health():
    """
    Health check endpoint for the retrieval service
    """
    try:
        # Test basic functionality
        is_connected = qdrant_service.validate_connection()
        collection_info = qdrant_service.get_collection_info() if is_connected else None

        return {
            "status": "healthy" if is_connected else "unhealthy",
            "service": "retrieval",
            "connection": is_connected,
            "collection_info": collection_info,
            "message": "Retrieval service is running" if is_connected else "Could not connect to Qdrant"
        }
    except Exception as e:
        logger.error(f"Retrieval health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "retrieval",
            "connection": False,
            "message": f"Retrieval service is not healthy: {str(e)}"
        }