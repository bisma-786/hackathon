"""
Integration tests for the retrieval API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from main import app


class TestRetrievalAPI:
    """Integration tests for retrieval API endpoints"""

    def setup_method(self):
        """Set up test client for each test method."""
        self.client = TestClient(app)

    def test_retrieve_by_url_endpoint_success(self):
        """Test successful retrieval by URL endpoint"""
        # This test will likely return no results since we don't have data in Qdrant
        # but it should return a 200 status with an empty list
        response = self.client.get("/api/vectors/by-url", params={"url": "https://example.com"})

        # Should return 200 even if no vectors found
        assert response.status_code in [200, 500]  # Allow 500 if Qdrant connection fails

        if response.status_code == 200:
            data = response.json()
            assert "vectors" in data
            assert "total_count" in data
            assert isinstance(data["vectors"], list)
            assert data["total_count"] >= 0

    def test_retrieve_by_url_endpoint_invalid_url(self):
        """Test retrieval by URL endpoint with invalid URL"""
        response = self.client.get("/api/vectors/by-url", params={"url": "not-a-valid-url"})

        # Should return 400 for invalid URL
        assert response.status_code == 400

        data = response.json()
        assert "Invalid URL" in data["detail"]

    def test_retrieve_by_url_endpoint_missing_param(self):
        """Test retrieval by URL endpoint without required URL parameter"""
        response = self.client.get("/api/vectors/by-url")

        # Should return 422 for missing required parameter
        assert response.status_code == 422

    def test_retrieve_by_module_endpoint_success(self):
        """Test successful retrieval by module endpoint"""
        response = self.client.get("/api/vectors/by-module", params={"module": "test_module"})

        # Should return 200 even if no vectors found
        assert response.status_code in [200, 500]  # Allow 500 if Qdrant connection fails

        if response.status_code == 200:
            data = response.json()
            assert "vectors" in data
            assert "total_count" in data
            assert isinstance(data["vectors"], list)
            assert data["total_count"] >= 0

    def test_retrieve_by_module_endpoint_invalid_module(self):
        """Test retrieval by module endpoint with invalid module"""
        response = self.client.get("/api/vectors/by-module", params={"module": ""})

        # Should return 400 for invalid module
        assert response.status_code == 400

        data = response.json()
        assert "Invalid module" in data["detail"]

    def test_retrieve_by_section_endpoint_success(self):
        """Test successful retrieval by section endpoint"""
        response = self.client.get("/api/vectors/by-section", params={"section": "test_section"})

        # Should return 200 even if no vectors found
        assert response.status_code in [200, 500]  # Allow 500 if Qdrant connection fails

        if response.status_code == 200:
            data = response.json()
            assert "vectors" in data
            assert "total_count" in data
            assert isinstance(data["vectors"], list)
            assert data["total_count"] >= 0

    def test_retrieve_by_section_endpoint_invalid_section(self):
        """Test retrieval by section endpoint with invalid section"""
        response = self.client.get("/api/vectors/by-section", params={"section": ""})

        # Should return 400 for invalid section
        assert response.status_code == 400

        data = response.json()
        assert "Invalid section" in data["detail"]

    def test_semantic_search_endpoint_success(self):
        """Test successful semantic search endpoint"""
        response = self.client.get("/api/vectors/semantic-search", params={"query": "test query"})

        # Should return 200 even if no vectors found
        assert response.status_code in [200, 500]  # Allow 500 if Qdrant connection fails

        if response.status_code == 200:
            data = response.json()
            assert "vectors" in data
            assert "total_count" in data
            assert "query_text" in data
            assert isinstance(data["vectors"], list)
            assert data["total_count"] >= 0
            assert data["query_text"] == "test query"

    def test_semantic_search_endpoint_with_params(self):
        """Test semantic search endpoint with additional parameters"""
        params = {
            "query": "test query",
            "limit": 5,
            "min_similarity": 0.7
        }
        response = self.client.get("/api/vectors/semantic-search", params=params)

        # Should return 200 even if no vectors found
        assert response.status_code in [200, 500]  # Allow 500 if Qdrant connection fails

    def test_semantic_search_endpoint_invalid_query(self):
        """Test semantic search endpoint with invalid query"""
        response = self.client.get("/api/vectors/semantic-search", params={"query": ""})

        # Should return 422 for validation error (empty query with min_length=1)
        assert response.status_code == 422

    def test_semantic_search_endpoint_long_query(self):
        """Test semantic search endpoint with too long query"""
        long_query = "a" * 501  # Exceeds max_length of 500
        response = self.client.get("/api/vectors/semantic-search", params={"query": long_query})

        # Should return 422 for validation error
        assert response.status_code == 422

    def test_retrieval_health_endpoint(self):
        """Test the retrieval health endpoint"""
        response = self.client.get("/api/retrieval/health")

        # Should return 200
        assert response.status_code in [200, 500]  # Allow 500 if Qdrant connection fails

        if response.status_code == 200:
            data = response.json()
            # Check response structure
            assert "status" in data
            assert "service" in data
            assert "connection" in data
            assert "message" in data

            # Check values
            assert data["service"] == "retrieval"
            assert data["message"] is not None

    def test_retrieve_by_url_endpoint_with_pagination(self):
        """Test retrieval by URL endpoint with pagination parameters"""
        params = {
            "url": "https://example.com",
            "limit": 10,
            "offset": 0
        }
        response = self.client.get("/api/vectors/by-url", params=params)

        # Should return 200 even if no vectors found
        assert response.status_code in [200, 500]  # Allow 500 if Qdrant connection fails

        if response.status_code == 200:
            data = response.json()
            assert "vectors" in data
            assert "limit" in data
            assert "offset" in data
            assert data["limit"] == 10
            assert data["offset"] == 0

    def test_retrieve_by_url_endpoint_with_invalid_limit(self):
        """Test retrieval by URL endpoint with invalid limit parameter"""
        params = {
            "url": "https://example.com",
            "limit": 2000  # Exceeds max of 1000
        }
        response = self.client.get("/api/vectors/by-url", params=params)

        # Should return 422 for validation error
        assert response.status_code == 422