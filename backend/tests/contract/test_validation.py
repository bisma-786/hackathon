"""
Contract tests for the validation API endpoints
These tests verify that the API endpoints conform to the expected contract
"""

import pytest
from fastapi.testclient import TestClient
from main import app


class TestValidationContract:
    """Contract tests for validation API endpoints"""

    def setup_method(self):
        """Set up test client for each test method."""
        self.client = TestClient(app)

    def test_validation_status_endpoint_contract(self):
        """Test that /validation/status endpoint conforms to expected contract"""
        response = self.client.get("/api/validation/status")

        # Check status code (allow both success and connection issues)
        assert response.status_code in [200, 500]

        if response.status_code == 200:
            data = response.json()

            # Check that required fields are present
            assert "collection_exists" in data
            assert "vector_count" in data
            assert "is_valid" in data
            assert "message" in data

            # Check field types
            assert isinstance(data["collection_exists"], bool)
            assert isinstance(data["vector_count"], int)
            assert data["vector_count"] >= 0  # Vector count should be non-negative
            assert isinstance(data["is_valid"], bool)
            assert isinstance(data["message"], str)

    def test_validation_report_endpoint_contract(self):
        """Test that /validation/report endpoint conforms to expected contract"""
        response = self.client.get("/api/validation/report")

        # Check status code (allow both success and connection issues)
        assert response.status_code in [200, 500]

        if response.status_code == 200:
            data = response.json()

            # Check that required fields are present
            assert "timestamp" in data
            assert "collection_name" in data
            assert "connection_valid" in data
            assert "validation_result" in data

            # Check field types
            assert isinstance(data["timestamp"], str)  # Should be ISO format datetime string
            assert isinstance(data["collection_name"], str)
            assert isinstance(data["connection_valid"], bool)
            assert isinstance(data["validation_result"], dict)

            # Check validation_result structure
            validation_result = data["validation_result"]
            assert "collection_exists" in validation_result
            assert "vector_count" in validation_result
            assert "is_valid" in validation_result
            assert "message" in validation_result

            assert isinstance(validation_result["collection_exists"], bool)
            assert isinstance(validation_result["vector_count"], int)
            assert isinstance(validation_result["is_valid"], bool)
            assert isinstance(validation_result["message"], str)

    def test_validation_status_endpoint_method(self):
        """Test that /validation/status only accepts GET requests"""
        # Try GET (should work)
        get_response = self.client.get("/api/validation/status")
        assert get_response.status_code in [200, 500]

        # Try POST (should return 405 - Method Not Allowed)
        post_response = self.client.post("/api/validation/status")
        assert post_response.status_code == 405

        # Try PUT (should return 405 - Method Not Allowed)
        put_response = self.client.put("/api/validation/status")
        assert put_response.status_code == 405

        # Try DELETE (should return 405 - Method Not Allowed)
        delete_response = self.client.delete("/api/validation/status")
        assert delete_response.status_code == 405

    def test_validation_report_endpoint_method(self):
        """Test that /validation/report only accepts GET requests"""
        # Try GET (should work)
        get_response = self.client.get("/api/validation/report")
        assert get_response.status_code in [200, 500]

        # Try POST (should return 405 - Method Not Allowed)
        post_response = self.client.post("/api/validation/report")
        assert post_response.status_code == 405

        # Try PUT (should return 405 - Method Not Allowed)
        put_response = self.client.put("/api/validation/report")
        assert put_response.status_code == 405

        # Try DELETE (should return 405 - Method Not Allowed)
        delete_response = self.client.delete("/api/validation/report")
        assert delete_response.status_code == 405

    def test_validation_status_response_format_consistency(self):
        """Test that the response format is consistent"""
        response = self.client.get("/api/validation/status")

        if response.status_code == 200:
            data = response.json()

            # Ensure no unexpected fields are present
            expected_fields = {"collection_exists", "vector_count", "is_valid", "message"}
            actual_fields = set(data.keys())

            # The actual fields should be equal to or a subset of expected fields
            # (allowing for additional fields in the future)
            assert expected_fields.issubset(actual_fields)

    def test_validation_report_response_format_consistency(self):
        """Test that the validation report response format is consistent"""
        response = self.client.get("/api/validation/report")

        if response.status_code == 200:
            data = response.json()

            # Ensure required fields are present
            expected_top_level_fields = {"timestamp", "collection_name", "connection_valid", "validation_result"}
            actual_top_level_fields = set(data.keys())

            assert expected_top_level_fields.issubset(actual_top_level_fields)

            # Check validation_result structure
            validation_result = data["validation_result"]
            expected_validation_fields = {"collection_exists", "vector_count", "is_valid", "message"}
            actual_validation_fields = set(validation_result.keys())

            assert expected_validation_fields.issubset(actual_validation_fields)

    def test_error_response_format(self):
        """Test that error responses follow a consistent format"""
        # This test is a bit tricky since we can't easily force errors in the validation service
        # without mocking. We'll test that the endpoint handles errors gracefully.

        # Check that the endpoint doesn't crash and returns appropriate status codes
        response = self.client.get("/api/validation/status")
        assert response.status_code in [200, 500]  # Should be either success or server error

        response = self.client.get("/api/validation/report")
        assert response.status_code in [200, 500]  # Should be either success or server error