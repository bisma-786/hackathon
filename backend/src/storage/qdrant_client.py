"""
Qdrant client wrapper for the Book URL Ingestion Pipeline.
"""

import hashlib
from typing import Any, Dict, List, Optional
from qdrant_client import QdrantClient as QdrantBaseClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from src.utils.config import Config
from src.utils.validators import validate_vector_record


class QdrantClient:
    """
    A wrapper around the Qdrant client that provides specific functionality
    for the Book URL Ingestion Pipeline.
    """

    def __init__(self, config: Config):
        self.config = config
        self.client = QdrantClient._create_client(config)

    @staticmethod
    def _create_client(config: Config):
        """Create a Qdrant client instance based on configuration."""
        client_params = {
            "url": config.qdrant_url,
        }

        if config.qdrant_api_key:
            client_params["api_key"] = config.qdrant_api_key

        return QdrantBaseClient(**client_params)

    def ensure_collection_exists(self, collection_name: str, vector_size: int = 1024) -> bool:
        """
        Ensure the specified collection exists, creating it if necessary.

        Args:
            collection_name: Name of the collection to ensure
            vector_size: Size of the embedding vectors (default: 1024 for Cohere)

        Returns:
            True if collection exists or was created successfully
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_exists = any(col.name == collection_name for col in collections.collections)

            if not collection_exists:
                # Create collection with appropriate vector configuration
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE
                    )
                )
                print(f"Created Qdrant collection: {collection_name}")
            else:
                print(f"Qdrant collection exists: {collection_name}")

            return True
        except Exception as e:
            print(f"Error ensuring collection exists: {str(e)}")
            return False

    def upsert_vectors(self, collection_name: str, vectors: List[Dict[str, Any]], batch_size: int = 100) -> int:
        """
        Upsert (insert or update) vectors in the specified collection in batches.

        Args:
            collection_name: Name of the collection
            vectors: List of vector records to upsert
            batch_size: Number of vectors to upsert in each batch (default: 100)

        Returns:
            Number of vectors successfully upserted
        """
        if not vectors:
            return 0

        total_upserted = 0

        # Process vectors in batches to avoid timeout issues
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]

            # Validate vectors in the batch before upserting
            for j, vector_record in enumerate(batch):
                errors = validate_vector_record(vector_record)
                if errors:
                    raise ValueError(f"Vector {i+j} validation failed: {errors}")

            # Prepare points for upsert
            points = []
            for vector_record in batch:
                # Convert the content hash to a UUID format for Qdrant compatibility
                import uuid
                # Take the first 32 characters of the SHA256 hash and format as UUID
                hash_str = vector_record['point_id'][:32]  # First 32 chars for UUID
                # Pad with zeros if needed and format as UUID
                hash_padded = hash_str.ljust(32, '0')
                uuid_str = f"{hash_padded[:8]}-{hash_padded[8:12]}-{hash_padded[12:16]}-{hash_padded[16:20]}-{hash_padded[20:32]}"
                point_id = uuid.UUID(uuid_str)

                point = PointStruct(
                    id=point_id,
                    vector=vector_record['vector'],
                    payload=vector_record.get('payload', {})
                )
                points.append(point)

            # Upsert the batch
            try:
                self.client.upsert(
                    collection_name=collection_name,
                    points=points
                )
                total_upserted += len(batch)
                print(f"Upserted batch: {i+1} to {i+len(batch)} of {len(vectors)} vectors")
            except Exception as e:
                print(f"Error upserting batch {i//batch_size + 1}: {str(e)}")
                raise

        return total_upserted

    def search_similar(self, collection_name: str, query_vector: List[float],
                      limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in the collection.

        Args:
            collection_name: Name of the collection to search
            query_vector: Vector to search for similar items
            limit: Maximum number of results to return

        Returns:
            List of similar vector records with payload
        """
        try:
            # Use query_points method which is the newer API (based on working implementation)
            response = self.client.query_points(
                collection_name=collection_name,
                query=query_vector,
                limit=limit,
                with_payload=True
            )

            # The response is a models.QueryResponse object with points attribute
            search_results = response.points

            # Format results
            formatted_results = []
            for hit in search_results:
                # Handle the response format from query_points
                payload = hit.payload if hasattr(hit, 'payload') and hit.payload else {}

                formatted_results.append({
                    'id': hit.id,
                    'score': getattr(hit, 'score', getattr(hit, 'distance', 0.0)),
                    'payload': payload,
                    'vector': getattr(hit, 'vector', None)  # vector might not always be present
                })

            return formatted_results
        except Exception as e:
            print(f"Error searching for similar vectors: {str(e)}")
            # Try fallback to older search API if query_points fails
            try:
                # Check if the older search method is available
                if hasattr(self.client, 'search'):
                    results = self.client.search(
                        collection_name=collection_name,
                        query_vector=query_vector,
                        limit=limit
                    )
                elif hasattr(self.client, 'search_points'):
                    results = self.client.search_points(
                        collection_name=collection_name,
                        query=query_vector,
                        limit=limit
                    )
                else:
                    print("No search method available on Qdrant client")
                    return []

                # Format results
                formatted_results = []
                for result in results:
                    payload = result.payload if hasattr(result, 'payload') and result.payload else {}
                    formatted_results.append({
                        'id': result.id,
                        'score': getattr(result, 'score', getattr(result, 'distance', 0.0)),
                        'payload': payload,
                        'vector': getattr(result, 'vector', None)
                    })

                return formatted_results
            except Exception as fallback_e:
                print(f"Fallback search also failed: {str(fallback_e)}")
                return []

    def get_vector_count(self, collection_name: str) -> int:
        """
        Get the count of vectors in the specified collection.

        Args:
            collection_name: Name of the collection

        Returns:
            Number of vectors in the collection
        """
        try:
            count_result = self.client.count(
                collection_name=collection_name
            )
            return count_result.count
        except Exception as e:
            print(f"Error getting vector count: {str(e)}")
            return 0

    def delete_collection(self, collection_name: str) -> bool:
        """
        Delete the specified collection.

        Args:
            collection_name: Name of the collection to delete

        Returns:
            True if deletion was successful
        """
        try:
            self.client.delete_collection(collection_name)
            return True
        except Exception as e:
            print(f"Error deleting collection: {str(e)}")
            return False

    def generate_content_hash(self, content: str, url: str) -> str:
        """
        Generate a unique hash for content and URL combination to ensure idempotency.

        Args:
            content: Content text
            url: URL of the source

        Returns:
            SHA256 hash string
        """
        content_to_hash = f"{url}|{content}".encode('utf-8')
        return hashlib.sha256(content_to_hash).hexdigest()


# Example usage and testing
if __name__ == "__main__":
    # This would require actual configuration to run
    pass