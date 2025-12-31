"""
Vector storage operations for the Book URL Ingestion Pipeline.
"""

import hashlib
from typing import Dict, List, Any
from src.utils.config import Config
from src.storage.qdrant_client import QdrantClient
from src.models.content_chunk import ContentChunk
from src.models.vector_record import VectorRecord


class VectorStore:
    """
    Handles vector storage operations for the Book URL Ingestion Pipeline.
    """

    def __init__(self, config: Config):
        self.config = config
        self.qdrant_client = QdrantClient(config)
        # Ensure the collection exists
        self.qdrant_client.ensure_collection_exists(
            config.qdrant_collection_name
        )

    def upsert_chunks(self, chunks: List[Dict[str, Any]], rebuild: bool = False) -> int:
        """
        Insert or update content chunks in vector store.

        Args:
            chunks: List of chunk dictionaries to upsert
            rebuild: Whether to rebuild the entire index

        Returns:
            Number of chunks successfully stored
        """
        if rebuild:
            # Delete existing collection if rebuild is requested
            self.qdrant_client.delete_collection(self.config.qdrant_collection_name)
            # Recreate collection
            self.qdrant_client.ensure_collection_exists(
                self.config.qdrant_collection_name
            )

        # Convert chunks to vector records
        vector_records = []
        for chunk in chunks:
            # Skip chunks with empty or missing embeddings
            if 'embedding' not in chunk or not chunk['embedding'] or len(chunk['embedding']) == 0:
                print(f"Skipping chunk with empty embedding for URL: {chunk.get('url', 'unknown')}")
                continue

            # Generate unique ID based on content and URL for idempotency
            content_id = self._generate_content_hash(chunk['text'], chunk['url'])

            # Create payload with complete metadata
            payload = {
                'url': chunk['url'],
                'module': chunk.get('module', 'unknown'),
                'section': chunk.get('section', 'unknown'),
                'chunk_index': chunk.get('chunk_index', 0),
                'text': chunk['text'],  # Store full text content
                'text_preview': chunk['text'][:100] + "..." if len(chunk['text']) > 100 else chunk['text'],
                'source_length': chunk.get('source_length', len(chunk['text']))
            }

            # Add heading hierarchy if present
            if 'heading_hierarchy' in chunk:
                payload['heading_hierarchy'] = chunk['heading_hierarchy']

            # Add additional metadata if present
            if 'heading_hierarchy' in chunk and chunk['heading_hierarchy']:
                payload['heading_hierarchy'] = chunk['heading_hierarchy']

            if 'created_at' in chunk:
                payload['created_at'] = chunk['created_at']

            if 'updated_at' in chunk:
                payload['updated_at'] = chunk['updated_at']

            if 'id' in chunk:
                payload['original_chunk_id'] = chunk['id']

            # Create vector record
            vector_record = {
                'point_id': content_id,
                'vector': chunk['embedding'],
                'payload': payload,
                'collection_name': self.config.qdrant_collection_name
            }

            vector_records.append(vector_record)

        # Upsert the vectors
        count = self.qdrant_client.upsert_vectors(
            self.config.qdrant_collection_name,
            vector_records
        )

        return count

    def _generate_content_hash(self, content: str, url: str) -> str:
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

    def search_similar(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar content chunks.

        Args:
            query: Query text to search for similar content
            limit: Maximum number of results to return

        Returns:
            List of similar chunks with metadata
        """
        # Generate embedding for the query
        # For now, we'll need to generate embedding separately
        # In a real implementation, we'd have access to the embedding generator
        # For this example, we'll just call the Qdrant client's search method directly
        # with a placeholder embedding (this would need to be implemented properly)

        # This is a simplified implementation - in reality, you'd need to:
        # 1. Generate embedding for the query using the same model as the stored vectors
        # 2. Search in Qdrant using that embedding
        # 3. Return formatted results

        # Placeholder - in a real implementation, this would require the embedding generator
        return []

    def get_vector_count(self) -> int:
        """
        Get the count of vectors in the collection.

        Returns:
            Number of vectors in the collection
        """
        return self.qdrant_client.get_vector_count(self.config.qdrant_collection_name)

    def validate_chunk(self, chunk: Dict[str, Any]) -> bool:
        """
        Validate a chunk before storing.

        Args:
            chunk: Chunk dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        required_fields = ['text', 'embedding', 'url', 'module', 'section']
        for field in required_fields:
            if field not in chunk:
                return False

        # Validate embedding is a list of numbers
        if not isinstance(chunk['embedding'], list) or len(chunk['embedding']) == 0:
            return False

        # Validate text is not empty
        if not chunk['text'] or not isinstance(chunk['text'], str):
            return False

        # Validate URL is not empty
        if not chunk['url'] or not isinstance(chunk['url'], str):
            return False

        return True


# Example usage and testing
if __name__ == "__main__":
    # This would require actual configuration to run
    pass