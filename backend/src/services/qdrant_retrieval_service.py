import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import time
import re
from qdrant_client import QdrantClient
from qdrant_client.http import models
from src.models.vector_record import VectorRecord
from src.lib.config import get_qdrant_client, QDRANT_COLLECTION_NAME


class QdrantRetrievalService:
    """
    Service class to handle all Qdrant vector retrieval operations
    """
    def __init__(self):
        self.client = get_qdrant_client()
        self.collection_name = QDRANT_COLLECTION_NAME
        self.logger = logging.getLogger(__name__)

    def retrieve_by_url(
        self,
        url: str,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[VectorRecord], int]:
        """
        Retrieve all vector chunks associated with a specific URL
        """
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
            # For scroll with offset, we need to scroll through results to reach the offset
            points = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=filter_condition,
                limit=limit,
                offset=offset,
                with_payload=True,
                with_vectors=True
            )

            # Convert the results to VectorRecord objects
            vector_records = []
            for point in points[0]:  # points is a tuple (points, next_offset)
                vector_record = VectorRecord.create_from_qdrant_payload(
                    vector_id=str(point.id),
                    embedding=point.vector if point.vector else [],
                    payload=point.payload
                )
                vector_records.append(vector_record)

            query_time = time.time() - start_time
            self.logger.info(f"Retrieved {len(vector_records)} vectors for URL {sanitized_url} in {query_time:.3f}s")

            return vector_records, len(vector_records)

        except Exception as e:
            self.logger.error(f"Error retrieving vectors by URL {url}: {str(e)}")
            raise

    def _validate_and_sanitize_url(self, url: str) -> str:
        """
        Validate and sanitize URL input
        """
        if not url or not isinstance(url, str):
            raise ValueError("URL must be a non-empty string")

        # Basic URL format validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if not url_pattern.match(url):
            raise ValueError(f"Invalid URL format: {url}")

        return url.strip()

    def retrieve_by_module(
        self,
        module: str,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[VectorRecord], int]:
        """
        Retrieve all vector chunks associated with a specific module
        """
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

            # Convert the results to VectorRecord objects
            vector_records = []
            for point in points[0]:  # points is a tuple (points, next_offset)
                vector_record = VectorRecord.create_from_qdrant_payload(
                    vector_id=str(point.id),
                    embedding=point.vector if point.vector else [],
                    payload=point.payload
                )
                vector_records.append(vector_record)

            query_time = time.time() - start_time
            self.logger.info(f"Retrieved {len(vector_records)} vectors for module {sanitized_module} in {query_time:.3f}s")

            return vector_records, len(vector_records)

        except Exception as e:
            self.logger.error(f"Error retrieving vectors by module {module}: {str(e)}")
            raise

    def _validate_and_sanitize_text(self, text: str, field_name: str) -> str:
        """
        Validate and sanitize text input for module, section, etc.
        """
        if not text or not isinstance(text, str):
            raise ValueError(f"{field_name} must be a non-empty string")

        # Remove leading/trailing whitespace
        sanitized = text.strip()

        if not sanitized:
            raise ValueError(f"{field_name} cannot be empty after sanitization")

        return sanitized

    def retrieve_by_section(
        self,
        section: str,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[VectorRecord], int]:
        """
        Retrieve all vector chunks associated with a specific section
        """
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

            # Convert the results to VectorRecord objects
            vector_records = []
            for point in points[0]:  # points is a tuple (points, next_offset)
                vector_record = VectorRecord.create_from_qdrant_payload(
                    vector_id=str(point.id),
                    embedding=point.vector if point.vector else [],
                    payload=point.payload
                )
                vector_records.append(vector_record)

            query_time = time.time() - start_time
            self.logger.info(f"Retrieved {len(vector_records)} vectors for section {sanitized_section} in {query_time:.3f}s")

            return vector_records, len(vector_records)

        except Exception as e:
            self.logger.error(f"Error retrieving vectors by section {section}: {str(e)}")
            raise

    def add_error_handling(self):
        """
        Placeholder method for error handling structure.
        Error handling is already implemented in each retrieval method.
        """
        pass

    def add_query_timing_metrics(self, start_time: float) -> float:
        """
        Calculate and return query execution time
        """
        return time.time() - start_time

    def format_retrieval_response(
        self,
        vectors: List[VectorRecord],
        query_time: float
    ) -> Dict:
        """
        Format retrieval results for API response
        """
        return {
            'vectors': [vector.to_dict() for vector in vectors],
            'count': len(vectors),
            'query_time': query_time
        }