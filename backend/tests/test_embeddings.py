"""
Tests for the embedding generator module in the Book URL Ingestion Pipeline.
"""

import pytest
from unittest.mock import Mock, patch
from src.embedding.generator import EmbeddingGenerator
from src.utils.config import Config


class TestEmbeddingGenerator:
    """
    Test class for the EmbeddingGenerator module.
    """

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create a mock config object
        self.mock_config = Mock(spec=Config)
        self.mock_config.cohere_api_key = "test-api-key"

        # Mock the cohere import and client
        with patch('src.embedding.generator.cohere') as mock_cohere_module:
            mock_cohere_client = Mock()
            mock_cohere_module.Client.return_value = mock_cohere_client
            self.generator = EmbeddingGenerator(self.mock_config)

    def test_generate_single_embedding(self):
        """Test the generate_single_embedding method."""
        test_text = "This is a test sentence."

        # Mock the Cohere API response
        mock_response = Mock()
        mock_response.embeddings = [[0.1, 0.2, 0.3, 0.4]]

        with patch('src.embedding.generator.cohere') as mock_cohere_module:
            mock_cohere_client = Mock()
            mock_cohere_client.embed.return_value = mock_response
            mock_cohere_module.Client.return_value = mock_cohere_client

            # Recreate the generator with the mocked client
            config = Mock(spec=Config)
            config.cohere_api_key = "test-api-key"
            generator = EmbeddingGenerator(config)

            result = generator.generate_single_embedding(test_text)

            # Verify the result is a list of floats
            assert isinstance(result, list)
            assert len(result) > 0
            assert all(isinstance(val, (int, float)) for val in result)

            # Verify the API was called with correct parameters
            mock_cohere_client.embed.assert_called_once_with(
                texts=[test_text],
                model='embed-multilingual-v3.0',
                input_type="search_document"
            )

    def test_generate_single_embedding_empty_text(self):
        """Test generating embedding for empty text."""
        with patch('src.embedding.generator.cohere') as mock_cohere_module:
            mock_cohere_client = Mock()
            mock_cohere_module.Client.return_value = mock_cohere_client

            # Recreate the generator with the mocked client
            config = Mock(spec=Config)
            config.cohere_api_key = "test-api-key"
            generator = EmbeddingGenerator(config)

            result = generator.generate_single_embedding("")

            # Should return an empty list for empty text
            assert result == []

    def test_generate_single_embedding_api_error(self):
        """Test handling of API errors in generate_single_embedding."""
        test_text = "This is a test sentence."

        with patch('src.embedding.generator.cohere') as mock_cohere_module:
            mock_cohere_client = Mock()
            mock_cohere_client.embed.side_effect = Exception("API Error")
            mock_cohere_module.Client.return_value = mock_cohere_client

            # Recreate the generator with the mocked client
            config = Mock(spec=Config)
            config.cohere_api_key = "test-api-key"
            generator = EmbeddingGenerator(config)

            result = generator.generate_single_embedding(test_text)

            # Should return an empty list on error
            assert result == []

    def test_generate_embeddings_batch(self):
        """Test the generate_embeddings method with a batch of texts."""
        test_texts = ["First sentence.", "Second sentence.", "Third sentence."]

        # Mock the Cohere API response
        mock_response = Mock()
        mock_response.embeddings = [
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
            [0.7, 0.8, 0.9]
        ]

        with patch('src.embedding.generator.cohere') as mock_cohere_module:
            mock_cohere_client = Mock()
            mock_cohere_client.embed.return_value = mock_response
            mock_cohere_module.Client.return_value = mock_cohere_client

            # Recreate the generator with the mocked client
            config = Mock(spec=Config)
            config.cohere_api_key = "test-api-key"
            generator = EmbeddingGenerator(config)

            result = generator.generate_embeddings(test_texts, batch_size=2)

            # Should return a list of embedding vectors
            assert isinstance(result, list)
            assert len(result) == len(test_texts)

            # Each embedding should be a list of floats
            for embedding in result:
                assert isinstance(embedding, list)
                assert len(embedding) > 0
                assert all(isinstance(val, (int, float)) for val in embedding)

            # Verify the API was called twice (since batch_size=2 and we have 3 texts)
            assert mock_cohere_client.embed.call_count == 2

    def test_generate_embeddings_empty_list(self):
        """Test generating embeddings for an empty list."""
        with patch('src.embedding.generator.cohere') as mock_cohere_module:
            mock_cohere_client = Mock()
            mock_cohere_module.Client.return_value = mock_cohere_client

            # Recreate the generator with the mocked client
            config = Mock(spec=Config)
            config.cohere_api_key = "test-api-key"
            generator = EmbeddingGenerator(config)

            result = generator.generate_embeddings([])

            # Should return an empty list
            assert result == []

    def test_generate_embeddings_api_error(self):
        """Test handling of API errors in generate_embeddings."""
        test_texts = ["First sentence.", "Second sentence."]

        with patch('src.embedding.generator.cohere') as mock_cohere_module:
            mock_cohere_client = Mock()
            mock_cohere_client.embed.side_effect = Exception("API Error")
            mock_cohere_module.Client.return_value = mock_cohere_client

            # Recreate the generator with the mocked client
            config = Mock(spec=Config)
            config.cohere_api_key = "test-api-key"
            generator = EmbeddingGenerator(config)

            result = generator.generate_embeddings(test_texts, batch_size=2)

            # Should return a list of empty embeddings on error
            assert isinstance(result, list)
            assert len(result) == len(test_texts)
            assert all(embedding == [] for embedding in result)


if __name__ == "__main__":
    pytest.main([__file__])