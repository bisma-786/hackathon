import unittest
from unittest.mock import Mock, patch
from src.services.qdrant_retrieval_service import QdrantRetrievalService
from src.models.vector_record import VectorRecord


class TestQdrantRetrievalService(unittest.TestCase):
    def setUp(self):
        self.service = QdrantRetrievalService()

    @patch.object(QdrantRetrievalService, '_validate_and_sanitize_url')
    @patch.object(QdrantRetrievalService, 'client', create=True)
    def test_retrieve_by_url_success(self, mock_client, mock_validate):
        # Arrange
        mock_validate.return_value = "https://example.com/test"
        mock_client.scroll.return_value = ([], None)  # Empty results for this test

        # Act
        result, count = self.service.retrieve_by_url("https://example.com/test")

        # Assert
        self.assertEqual(count, 0)  # No results expected
        mock_validate.assert_called_once_with("https://example.com/test")
        mock_client.scroll.assert_called()

    def test_validate_and_sanitize_url_valid(self):
        # Arrange
        valid_url = "https://example.com/test"

        # Act
        result = self.service._validate_and_sanitize_url(valid_url)

        # Assert
        self.assertEqual(result, "https://example.com/test")

    def test_validate_and_sanitize_url_invalid(self):
        # Arrange
        invalid_url = "not-a-url"

        # Act & Assert
        with self.assertRaises(ValueError):
            self.service._validate_and_sanitize_url(invalid_url)

    def test_validate_and_sanitize_url_empty(self):
        # Act & Assert
        with self.assertRaises(ValueError):
            self.service._validate_and_sanitize_url("")

        with self.assertRaises(ValueError):
            self.service._validate_and_sanitize_url(None)

    def test_validate_and_sanitize_text_valid(self):
        # Arrange
        text = "  test text  "

        # Act
        result = self.service._validate_and_sanitize_text(text, "test_field")

        # Assert
        self.assertEqual(result, "test text")

    def test_validate_and_sanitize_text_empty(self):
        # Act & Assert
        with self.assertRaises(ValueError):
            self.service._validate_and_sanitize_text("", "test_field")

        with self.assertRaises(ValueError):
            self.service._validate_and_sanitize_text("   ", "test_field")

        with self.assertRaises(ValueError):
            self.service._validate_and_sanitize_text(None, "test_field")


if __name__ == '__main__':
    unittest.main()