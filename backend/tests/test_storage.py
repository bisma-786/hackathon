"""
Tests for the vector storage module in the Book URL Ingestion Pipeline.
"""

import pytest
from unittest.mock import Mock, patch
from src.storage.vector_store import VectorStore
from src.utils.config import Config


class TestVectorStore:
    """
    Test class for the VectorStore module.
    """

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create a mock config object
        self.mock_config = Mock(spec=Config)
        self.mock_config.qdrant_collection_name = "test_collection"
        self.mock_config.qdrant_url = "https://test-qdrant.com"
        self.mock_config.qdrant_api_key = "test-key"

        # Mock the QdrantClient
        with patch('src.storage.vector_store.QdrantClient') as mock_qdrant_class:
            mock_qdrant_instance = Mock()
            mock_qdrant_class.return_value = mock_qdrant_instance
            self.vector_store = VectorStore(self.mock_config)

    def test_upsert_chunks_basic(self):
        """Test the upsert_chunks method with basic chunks."""
        chunks = [
            {
                'text': 'This is the first chunk of text.',
                'embedding': [0.1, 0.2, 0.3],
                'url': 'https://example.com/page1',
                'module': 'module1',
                'section': 'section1'
            },
            {
                'text': 'This is the second chunk of text.',
                'embedding': [0.4, 0.5, 0.6],
                'url': 'https://example.com/page2',
                'module': 'module2',
                'section': 'section2'
            }
        ]

        # Mock the Qdrant client methods
        with patch('src.storage.vector_store.QdrantClient') as mock_qdrant_class:
            mock_qdrant_instance = Mock()
            mock_qdrant_instance.upsert_vectors.return_value = 2  # Return count of upserted vectors
            mock_qdrant_class.return_value = mock_qdrant_instance

            # Recreate the vector store with the mocked client
            config = Mock(spec=Config)
            config.qdrant_collection_name = "test_collection"
            config.qdrant_url = "https://test-qdrant.com"
            config.qdrant_api_key = "test-key"
            vector_store = VectorStore(config)

            result = vector_store.upsert_chunks(chunks)

            # Verify the result
            assert result == 2  # Should return the count of upserted vectors

            # Verify the Qdrant client was called with correct parameters
            mock_qdrant_instance.upsert_vectors.assert_called_once()
            args, kwargs = mock_qdrant_instance.upsert_vectors.call_args
            assert args[0] == "test_collection"  # First argument should be collection name

            # Verify the vector records were created properly
            vector_records = args[1]
            assert len(vector_records) == 2
            for record in vector_records:
                assert 'point_id' in record
                assert 'vector' in record
                assert 'payload' in record
                assert 'collection_name' in record

    def test_upsert_chunks_empty_list(self):
        """Test upsert_chunks with an empty list."""
        with patch('src.storage.vector_store.QdrantClient') as mock_qdrant_class:
            mock_qdrant_instance = Mock()
            mock_qdrant_class.return_value = mock_qdrant_instance

            # Recreate the vector store with the mocked client
            config = Mock(spec=Config)
            config.qdrant_collection_name = "test_collection"
            config.qdrant_url = "https://test-qdrant.com"
            config.qdrant_api_key = "test-key"
            vector_store = VectorStore(config)

            result = vector_store.upsert_chunks([])

            # Should return 0 for empty list
            assert result == 0

            # Qdrant client should not be called for empty list
            mock_qdrant_instance.upsert_vectors.assert_not_called()

    def test_upsert_chunks_with_rebuild(self):
        """Test the upsert_chunks method with rebuild enabled."""
        chunks = [
            {
                'text': 'Test chunk',
                'embedding': [0.1, 0.2, 0.3],
                'url': 'https://example.com/page',
                'module': 'module1',
                'section': 'section1'
            }
        ]

        with patch('src.storage.vector_store.QdrantClient') as mock_qdrant_class:
            mock_qdrant_instance = Mock()
            mock_qdrant_instance.upsert_vectors.return_value = 1
            mock_qdrant_class.return_value = mock_qdrant_instance

            # Recreate the vector store with the mocked client
            config = Mock(spec=Config)
            config.qdrant_collection_name = "test_collection"
            config.qdrant_url = "https://test-qdrant.com"
            config.qdrant_api_key = "test-key"
            vector_store = VectorStore(config)

            # Call with rebuild=True
            result = vector_store.upsert_chunks(chunks, rebuild=True)

            # Verify the collection was deleted and recreated
            mock_qdrant_instance.delete_collection.assert_called_once_with("test_collection")
            mock_qdrant_instance.ensure_collection_exists.assert_called_once_with("test_collection")

            # Verify the upsert was called
            mock_qdrant_instance.upsert_vectors.assert_called_once()

    def test_generate_content_hash(self):
        """Test the _generate_content_hash method."""
        content = "Sample content text"
        url = "https://example.com/page"

        hash1 = self.vector_store._generate_content_hash(content, url)
        hash2 = self.vector_store._generate_content_hash(content, url)

        # Same content and URL should produce same hash
        assert hash1 == hash2

        # Different content should produce different hash
        hash3 = self.vector_store._generate_content_hash("Different content", url)
        assert hash1 != hash3

        # Different URL should produce different hash
        hash4 = self.vector_store._generate_content_hash(content, "https://example.com/different")
        assert hash1 != hash4

    def test_get_vector_count(self):
        """Test the get_vector_count method."""
        with patch('src.storage.vector_store.QdrantClient') as mock_qdrant_class:
            mock_qdrant_instance = Mock()
            mock_qdrant_instance.get_vector_count.return_value = 42
            mock_qdrant_class.return_value = mock_qdrant_instance

            # Recreate the vector store with the mocked client
            config = Mock(spec=Config)
            config.qdrant_collection_name = "test_collection"
            config.qdrant_url = "https://test-qdrant.com"
            config.qdrant_api_key = "test-key"
            vector_store = VectorStore(config)

            result = vector_store.get_vector_count()

            # Verify the result
            assert result == 42

            # Verify the Qdrant client method was called
            mock_qdrant_instance.get_vector_count.assert_called_once_with("test_collection")

    def test_validate_chunk(self):
        """Test the validate_chunk method."""
        # Valid chunk
        valid_chunk = {
            'text': 'Sample text',
            'embedding': [0.1, 0.2, 0.3],
            'url': 'https://example.com',
            'module': 'module1',
            'section': 'section1'
        }
        assert self.vector_store.validate_chunk(valid_chunk) is True

        # Invalid chunks
        invalid_chunks = [
            # Missing required fields
            {'embedding': [0.1, 0.2, 0.3], 'url': 'https://example.com'},
            {'text': 'Sample text', 'url': 'https://example.com'},
            {'text': 'Sample text', 'embedding': [0.1, 0.2, 0.3]},

            # Invalid embedding
            {'text': 'Sample text', 'embedding': [], 'url': 'https://example.com', 'module': 'module1', 'section': 'section1'},
            {'text': 'Sample text', 'embedding': 'not a list', 'url': 'https://example.com', 'module': 'module1', 'section': 'section1'},

            # Invalid text
            {'text': '', 'embedding': [0.1, 0.2, 0.3], 'url': 'https://example.com', 'module': 'module1', 'section': 'section1'},
            {'text': None, 'embedding': [0.1, 0.2, 0.3], 'url': 'https://example.com', 'module': 'module1', 'section': 'section1'},

            # Invalid URL
            {'text': 'Sample text', 'embedding': [0.1, 0.2, 0.3], 'url': '', 'module': 'module1', 'section': 'section1'},
            {'text': 'Sample text', 'embedding': [0.1, 0.2, 0.3], 'url': None, 'module': 'module1', 'section': 'section1'},
        ]

        for chunk in invalid_chunks:
            assert self.vector_store.validate_chunk(chunk) is False


if __name__ == "__main__":
    pytest.main([__file__])