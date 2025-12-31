"""
Configuration management for the Book URL Ingestion Pipeline.
"""

import os
from typing import Optional
from dotenv import load_dotenv


class Config:
    """
    Configuration class that manages all environment variables and settings
    for the Book URL Ingestion Pipeline.
    """

    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

        # Cohere API configuration
        self.cohere_api_key = os.getenv('COHERE_API_KEY')
        if not self.cohere_api_key:
            raise ValueError("COHERE_API_KEY environment variable is required")

        # Qdrant Cloud configuration
        self.qdrant_url = os.getenv('QDRANT_URL')
        if not self.qdrant_url:
            raise ValueError("QDRANT_URL environment variable is required")

        self.qdrant_api_key = os.getenv('QDRANT_API_KEY')
        # Qdrant API key is optional (for public clusters)

        # Book site configuration
        self.book_base_url = os.getenv('BOOK_BASE_URL')
        if not self.book_base_url:
            raise ValueError("BOOK_BASE_URL environment variable is required")

        # Qdrant collection name
        self.qdrant_collection_name = os.getenv('QDRANT_COLLECTION_NAME', 'book_content_chunks')

        # Chunking configuration
        self.chunk_size = int(os.getenv('CHUNK_SIZE', '1000'))
        self.chunk_overlap = int(os.getenv('CHUNK_OVERLAP', '200'))

        # API limits and retry settings
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))
        self.retry_delay = float(os.getenv('RETRY_DELAY', '1.0'))
        self.request_timeout = int(os.getenv('REQUEST_TIMEOUT', '30'))

        # Validation
        self._validate_config()

    def _validate_config(self):
        """Validate configuration values."""
        if self.chunk_size <= 0:
            raise ValueError("CHUNK_SIZE must be positive")
        if self.chunk_overlap < 0:
            raise ValueError("CHUNK_OVERLAP cannot be negative")
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("CHUNK_OVERLAP must be less than CHUNK_SIZE")
        if self.max_retries <= 0:
            raise ValueError("MAX_RETRIES must be positive")
        if self.retry_delay <= 0:
            raise ValueError("RETRY_DELAY must be positive")
        if self.request_timeout <= 0:
            raise ValueError("REQUEST_TIMEOUT must be positive")

    def get_cohere_config(self) -> dict:
        """Get Cohere API configuration."""
        return {
            'api_key': self.cohere_api_key
        }

    def get_qdrant_config(self) -> dict:
        """Get Qdrant client configuration."""
        config = {
            'url': self.qdrant_url,
            'collection_name': self.qdrant_collection_name
        }
        if self.qdrant_api_key:
            config['api_key'] = self.qdrant_api_key
        return config