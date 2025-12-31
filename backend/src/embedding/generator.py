"""
Embedding generation module for the Book URL Ingestion Pipeline.
"""

import time
from typing import List
from src.utils.config import Config


class EmbeddingGenerator:
    """
    Handles Cohere embedding generation for the Book URL Ingestion Pipeline.
    """

    def __init__(self, config: Config):
        self.config = config
        # Import Cohere here to avoid dependency issues if not installed
        try:
            import cohere
            self.cohere_client = cohere.Client(config.cohere_api_key)
        except ImportError:
            raise ImportError("Cohere package is required for embedding generation. Install with: pip install cohere")

    def generate_embeddings(self, texts: List[str], batch_size: int = 10) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to generate embeddings for
            batch_size: Size of batches for API requests

        Returns:
            List of embedding vectors (each vector is a list of floats)
        """
        if not texts:
            return []

        all_embeddings = []

        # Process in batches to respect API limits
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            # Generate embeddings for the batch
            embeddings = self._generate_batch_embeddings(batch)
            all_embeddings.extend(embeddings)

            # Add delay between batches to respect rate limits
            if i + batch_size < len(texts):
                time.sleep(1)  # Adjust based on API rate limits

        return all_embeddings

    def _generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.

        Args:
            texts: List of text strings to generate embeddings for

        Returns:
            List of embedding vectors
        """
        try:
            # Call Cohere API to generate embeddings
            response = self.cohere_client.embed(
                texts=texts,
                model='embed-multilingual-v3.0',  # Using multilingual model as specified
                input_type="search_document"  # Using search_document as the input type
            )

            # Extract embeddings from response
            embeddings = []
            for embedding in response.embeddings:
                embeddings.append(embedding)

            return embeddings

        except Exception as e:
            print(f"Error generating embeddings: {str(e)}")
            # Return empty embeddings for failed batch (in a real implementation, you might want to retry)
            return [[] for _ in texts]

    def generate_single_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text string to generate embedding for

        Returns:
            Embedding vector (list of floats)
        """
        if not text:
            return []

        try:
            response = self.cohere_client.embed(
                texts=[text],
                model='embed-multilingual-v3.0',
                input_type="search_document"
            )

            if response.embeddings and len(response.embeddings) > 0:
                return response.embeddings[0]
            else:
                return []

        except Exception as e:
            print(f"Error generating embedding for text: {str(e)}")
            return []


# Example usage and testing
if __name__ == "__main__":
    # This would require actual configuration to run
    pass