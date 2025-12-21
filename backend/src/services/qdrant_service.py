from typing import List, Dict, Optional
from src.lib.config import get_qdrant_client, get_collection_name, RetrievalException, ValidationException
from src.models.api_models import VectorResponse, VectorListResponse
from qdrant_client.http import models
import logging


class QdrantService:
    """
    Service class to handle all Qdrant vector operations
    """

    def __init__(self):
        self.collection_name = get_collection_name()
        self.logger = logging.getLogger(__name__)
        self._client = None
        self._connection_valid = False
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the Qdrant client with connection validation"""
        try:
            self._client = get_qdrant_client()
            # Test the connection
            self._connection_valid = self.validate_connection()
            if not self._connection_valid:
                self.logger.warning(f"Qdrant connection failed during initialization for collection {self.collection_name}")
        except Exception as e:
            self.logger.error(f"Failed to initialize Qdrant client: {str(e)}")
            self._connection_valid = False
            self._client = None

    @property
    def client(self):
        """Property to access the client with automatic reconnection if needed"""
        if not self._client or not self._connection_valid:
            self.logger.info("Reinitializing Qdrant client due to connection issues")
            self._initialize_client()
        return self._client

    def retrieve_by_url(self, url: str, limit: int = 100, offset: int = 0) -> VectorListResponse:
        """
        Retrieve all vector chunks associated with a specific URL
        """
        import time
        start_time = time.time()

        try:
            # Validate and sanitize URL input
            sanitized_url = self._validate_and_sanitize_url(url)

            # Prepare the filter for Qdrant
            filter_condition = models.Filter(
                must=[
                    models.FieldCondition(
                        key="url",
                        match=models.MatchValue(value=sanitized_url)
                    )
                ]
            )

            # Perform the search with pagination
            points = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=filter_condition,
                limit=limit,
                offset=offset,
                with_payload=True,
                with_vectors=True
            )

            # Convert the results to VectorResponse objects
            vector_responses = []
            for point in points[0]:  # points is a tuple (points, next_offset)
                vector_response = VectorResponse(
                    id=str(point.id),
                    embedding=point.vector if point.vector else [],
                    metadata=point.payload,
                    similarity_score=None  # Not applicable for exact match
                )
                vector_responses.append(vector_response)

            duration = time.time() - start_time
            self.logger.info(f"Retrieved {len(vector_responses)} vectors for URL {sanitized_url} in {duration:.3f} seconds")

            return VectorListResponse(
                vectors=vector_responses,
                total_count=len(vector_responses),
                limit=limit,
                offset=offset
            )

        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Error retrieving vectors by URL {url} after {duration:.3f} seconds: {str(e)}")

            # Return empty result instead of raising exception for graceful degradation
            return VectorListResponse(
                vectors=[],
                total_count=0,
                limit=limit,
                offset=offset
            )

    def retrieve_by_module(self, module: str, limit: int = 100, offset: int = 0) -> VectorListResponse:
        """
        Retrieve all vector chunks associated with a specific module
        """
        import time
        start_time = time.time()

        try:
            # Validate module input
            sanitized_module = self._validate_and_sanitize_text(module, "module")

            # Prepare the filter for Qdrant
            filter_condition = models.Filter(
                must=[
                    models.FieldCondition(
                        key="module",
                        match=models.MatchValue(value=sanitized_module)
                    )
                ]
            )

            # Perform the search with pagination
            points = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=filter_condition,
                limit=limit,
                offset=offset,
                with_payload=True,
                with_vectors=True
            )

            # Convert the results to VectorResponse objects
            vector_responses = []
            for point in points[0]:  # points is a tuple (points, next_offset)
                vector_response = VectorResponse(
                    id=str(point.id),
                    embedding=point.vector if point.vector else [],
                    metadata=point.payload,
                    similarity_score=None  # Not applicable for exact match
                )
                vector_responses.append(vector_response)

            duration = time.time() - start_time
            self.logger.info(f"Retrieved {len(vector_responses)} vectors for module {sanitized_module} in {duration:.3f} seconds")

            return VectorListResponse(
                vectors=vector_responses,
                total_count=len(vector_responses),
                limit=limit,
                offset=offset
            )

        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Error retrieving vectors by module {module} after {duration:.3f} seconds: {str(e)}")

            # Return empty result instead of raising exception for graceful degradation
            return VectorListResponse(
                vectors=[],
                total_count=0,
                limit=limit,
                offset=offset
            )

    def retrieve_by_section(self, section: str, limit: int = 100, offset: int = 0) -> VectorListResponse:
        """
        Retrieve all vector chunks associated with a specific section
        """
        import time
        start_time = time.time()

        try:
            # Validate section input
            sanitized_section = self._validate_and_sanitize_text(section, "section")

            # Prepare the filter for Qdrant
            filter_condition = models.Filter(
                must=[
                    models.FieldCondition(
                        key="section",
                        match=models.MatchValue(value=sanitized_section)
                    )
                ]
            )

            # Perform the search with pagination
            points = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=filter_condition,
                limit=limit,
                offset=offset,
                with_payload=True,
                with_vectors=True
            )

            # Convert the results to VectorResponse objects
            vector_responses = []
            for point in points[0]:  # points is a tuple (points, next_offset)
                vector_response = VectorResponse(
                    id=str(point.id),
                    embedding=point.vector if point.vector else [],
                    metadata=point.payload,
                    similarity_score=None  # Not applicable for exact match
                )
                vector_responses.append(vector_response)

            duration = time.time() - start_time
            self.logger.info(f"Retrieved {len(vector_responses)} vectors for section {sanitized_section} in {duration:.3f} seconds")

            return VectorListResponse(
                vectors=vector_responses,
                total_count=len(vector_responses),
                limit=limit,
                offset=offset
            )

        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Error retrieving vectors by section {section} after {duration:.3f} seconds: {str(e)}")

            # Return empty result instead of raising exception for graceful degradation
            return VectorListResponse(
                vectors=[],
                total_count=0,
                limit=limit,
                offset=offset
            )

    def semantic_search(self, query_text: str, limit: int = 10, min_similarity: float = 0.5) -> VectorListResponse:
        """
        Perform semantic search using the query text to find similar content
        This method assumes that embeddings are already computed and stored in Qdrant
        """
        import time
        start_time = time.time()

        try:
            # In a real implementation, we would need to generate an embedding for the query_text
            # using the same model that was used during ingestion (e.g., Cohere model)
            # For now, we'll use a placeholder implementation that assumes pre-computed embeddings
            # In a production system, you'd have a dedicated service to generate embeddings
            # from text using the same model used during ingestion

            # Since we don't have the actual embedding generation here, we'll use Qdrant's
            # dense vector search with a placeholder - in a real system, we would:
            # 1. Generate embedding for query_text using the same model as during ingestion
            # 2. Use client.search with the generated vector

            # For now, using Qdrant's search functionality
            # Note: In a real semantic search, you would have generated embeddings during ingestion
            # and would search using vector similarity
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_text=query_text,  # This uses Qdrant's text-based search if available
                limit=limit,
                score_threshold=min_similarity,
                with_payload=True,
                with_vectors=True
            )

            # Convert the results to VectorResponse objects
            vector_responses = []
            for result in search_results:
                vector_response = VectorResponse(
                    id=str(result.id),
                    embedding=result.vector if result.vector else [],
                    metadata=result.payload,
                    similarity_score=result.score
                )
                vector_responses.append(vector_response)

            duration = time.time() - start_time
            self.logger.info(f"Semantic search returned {len(vector_responses)} vectors for query: {query_text} in {duration:.3f} seconds")

            return VectorListResponse(
                vectors=vector_responses,
                total_count=len(vector_responses),
                limit=limit,
                query_text=query_text
            )

        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Error performing semantic search for query '{query_text}' after {duration:.3f} seconds: {str(e)}")

            # Return empty result instead of raising exception for graceful degradation
            return VectorListResponse(
                vectors=[],
                total_count=0,
                limit=limit,
                query_text=query_text
            )

    def _validate_and_sanitize_url(self, url: str) -> str:
        """
        Validate and sanitize URL input
        """
        if not url or not isinstance(url, str):
            raise ValidationException("URL must be a non-empty string")

        # Basic URL format validation
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if not url_pattern.match(url):
            raise ValidationException(f"Invalid URL format: {url}")

        return url.strip()

    def _validate_and_sanitize_text(self, text: str, field_name: str) -> str:
        """
        Validate and sanitize text input for module, section, etc.
        """
        if not text or not isinstance(text, str):
            raise ValidationException(f"{field_name} must be a non-empty string")

        # Remove leading/trailing whitespace
        sanitized = text.strip()

        if not sanitized:
            raise ValidationException(f"{field_name} cannot be empty after sanitization")

        return sanitized

    def get_collection_info(self) -> Dict:
        """
        Get information about the collection
        """
        try:
            if not self._connection_valid:
                self.logger.warning("Qdrant connection is not valid, returning default info")
                return {
                    "name": self.collection_name,
                    "vector_size": 0,
                    "distance": "unknown",
                    "points_count": 0,
                    "status": "connection_failed"
                }

            collection_info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vector_size": collection_info.config.params.vectors.size,
                "distance": collection_info.config.params.vectors.distance,
                "points_count": collection_info.points_count,
                "status": "connected"
            }
        except Exception as e:
            self.logger.error(f"Error getting collection info: {str(e)}")
            # Return default info instead of raising exception for graceful degradation
            return {
                "name": self.collection_name,
                "vector_size": 0,
                "distance": "unknown",
                "points_count": 0,
                "status": "connection_failed",
                "error": str(e)
            }

    def validate_connection(self) -> bool:
        """
        Validate that the connection to Qdrant is working
        """
        try:
            if not self._client:
                return False
            # Try to get collection info to verify connection
            collection_info = self._client.get_collection(self.collection_name)
            return True
        except Exception as e:
            self.logger.warning(f"Qdrant connection validation failed: {str(e)}")
            return False