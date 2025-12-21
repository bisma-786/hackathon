"""
Unit tests for the RetrievalValidationService class
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.services.retrieval_service import RetrievalValidationService


class TestRetrievalValidationService:
    """Test suite for RetrievalValidationService"""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Mock the dependencies to avoid external connections
        with patch('src.services.retrieval_service.get_qdrant_client'):
            with patch('src.services.retrieval_service.get_collection_name', return_value='test_collection'):
                # We also need to mock QdrantService initialization
                with patch('src.services.retrieval_service.QdrantService'):
                    self.validation_service = RetrievalValidationService()

    def test_validate_connection_success(self):
        """Test successful connection validation"""
        # Mock successful collection info retrieval
        self.validation_service.get_collection_info = Mock(return_value={
            "name": "test_collection",
            "vector_size": 1536,
            "distance": "Cosine",
            "points_count": 100
        })

        # Call the method
        result = self.validation_service.validate_connection()

        # Assertions
        assert result is True
        self.validation_service.get_collection_info.assert_called_once()

    def test_validate_connection_failure(self):
        """Test connection validation failure"""
        # Mock failed collection info retrieval
        self.validation_service.get_collection_info = Mock(side_effect=Exception("Connection failed"))

        # Call the method
        result = self.validation_service.validate_connection()

        # Assertions
        assert result is False

    def test_get_collection_info_success(self):
        """Test successful retrieval of collection info"""
        # Mock the collection info response
        mock_collection_info = Mock()
        mock_collection_info.config.params.vectors.size = 1536
        mock_collection_info.config.params.vectors.distance = "Cosine"
        mock_collection_info.points_count = 100

        self.validation_service.client.get_collection.return_value = mock_collection_info

        # Call the method
        result = self.validation_service.get_collection_info()

        # Assertions
        assert result["name"] == "test_collection"
        assert result["vector_size"] == 1536
        assert result["distance"] == "Cosine"
        assert result["points_count"] == 100

    def test_get_collection_info_failure(self):
        """Test collection info retrieval failure"""
        # Mock failed collection info retrieval
        self.validation_service.client.get_collection.side_effect = Exception("Collection not found")

        # Call the method should raise exception
        with pytest.raises(Exception):
            self.validation_service.get_collection_info()

    def test_validate_vector_count_success(self):
        """Test successful vector count validation"""
        # Mock the collection info
        self.validation_service.get_collection_info = Mock(return_value={
            "name": "test_collection",
            "vector_size": 1536,
            "distance": "Cosine",
            "points_count": 50
        })

        # Call the method
        result = self.validation_service.validate_vector_count()

        # Assertions
        assert result["collection_name"] == "test_collection"
        assert result["vector_count"] == 50
        assert result["is_valid"] is True
        assert "validation completed successfully" in result["message"]

    def test_validate_vector_count_failure(self):
        """Test vector count validation failure"""
        # Mock failed collection info retrieval
        self.validation_service.get_collection_info = Mock(side_effect=Exception("Failed to get count"))

        # Call the method
        with pytest.raises(Exception):
            self.validation_service.validate_vector_count()

    def test_verify_collection_exists_success(self):
        """Test successful collection verification"""
        # Mock successful collection info retrieval
        self.validation_service.get_collection_info = Mock(return_value={
            "name": "test_collection",
            "vector_size": 1536,
            "distance": "Cosine",
            "points_count": 100
        })

        # Call the method
        result = self.validation_service.verify_collection_exists()

        # Assertions
        assert result is True

    def test_verify_collection_exists_failure(self):
        """Test collection verification failure"""
        # Mock failed collection info retrieval
        self.validation_service.get_collection_info = Mock(side_effect=Exception("Collection not found"))

        # Call the method
        result = self.validation_service.verify_collection_exists()

        # Assertions
        assert result is False

    def test_validate_vector_storage_success(self):
        """Test successful vector storage validation"""
        # Mock the methods that are called
        self.validation_service.verify_collection_exists = Mock(return_value=True)
        self.validation_service.validate_vector_count = Mock(return_value={
            "vector_count": 50,
            "is_valid": True
        })

        # Call the method
        result = self.validation_service.validate_vector_storage()

        # Assertions
        assert result["collection_exists"] is True
        assert result["vector_count"] == 50
        assert result["is_valid"] is True

    def test_validate_vector_storage_collection_not_exists(self):
        """Test vector storage validation when collection doesn't exist"""
        # Mock collection does not exist
        self.validation_service.verify_collection_exists = Mock(return_value=False)

        # Call the method
        result = self.validation_service.validate_vector_storage()

        # Assertions
        assert result["collection_exists"] is False
        assert result["vector_count"] == 0
        assert result["is_valid"] is False
        assert "does not exist" in result["message"]

    def test_validate_vector_storage_error(self):
        """Test vector storage validation when an error occurs"""
        # Mock an error during validation
        self.validation_service.verify_collection_exists = Mock(side_effect=Exception("Validation error"))

        # Call the method
        result = self.validation_service.validate_vector_storage()

        # Assertions
        assert result["collection_exists"] is False
        assert result["vector_count"] == 0
        assert result["is_valid"] is False
        assert "Validation failed" in result["message"]

    def test_generate_validation_report_success(self):
        """Test successful validation report generation"""
        # Mock the methods that are called
        self.validation_service.validate_connection = Mock(return_value=True)
        self.validation_service.validate_vector_storage = Mock(return_value={
            "collection_exists": True,
            "vector_count": 50,
            "is_valid": True,
            "message": "Validation successful"
        })

        # Call the method
        result = self.validation_service.generate_validation_report()

        # Assertions
        assert "timestamp" in result
        assert result["collection_name"] == "test_collection"
        assert result["connection_valid"] is True
        assert "validation_result" in result
        assert result["validation_result"]["collection_exists"] is True

    def test_generate_validation_report_error(self):
        """Test validation report generation when an error occurs"""
        # Mock errors during report generation
        self.validation_service.validate_connection = Mock(side_effect=Exception("Connection error"))

        # Call the method
        result = self.validation_service.generate_validation_report()

        # Assertions
        assert "timestamp" in result
        assert result["collection_name"] == "test_collection"
        assert result["connection_valid"] is False
        assert result["validation_result"]["collection_exists"] is False
        assert result["validation_result"]["vector_count"] == 0
        assert result["validation_result"]["is_valid"] is False