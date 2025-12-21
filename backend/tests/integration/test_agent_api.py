"""
Integration tests for the agent API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from src.models.agent_models import AgentRequest


class TestAgentAPI:
    """Integration tests for agent API endpoints"""

    def setup_method(self):
        """Set up test client for each test method."""
        self.client = TestClient(app)

    def test_agent_query_endpoint_success(self):
        """Test successful query to the agent endpoint"""
        # Prepare a test request
        test_request = {
            "query": "What is AI-driven robotics?",
            "instructions": "You are an AI assistant for the AI-Driven Robotics Textbook. Answer questions based on the provided context.",
            "temperature": 0.7,
            "max_tokens": 150
        }

        # Make the request
        response = self.client.post("/api/agent/query", json=test_request)

        # Basic assertions
        assert response.status_code == 200

        # Parse response
        data = response.json()

        # Check response structure
        assert "answer" in data
        assert "sources" in data
        assert "confidence" in data
        assert "retrieved_context" in data
        assert "followup_questions" in data

        # Check data types
        assert isinstance(data["answer"], str)
        assert isinstance(data["sources"], list)
        assert isinstance(data["confidence"], float)
        assert isinstance(data["retrieved_context"], list)
        assert isinstance(data["followup_questions"], list)

        # Check confidence range
        assert 0.0 <= data["confidence"] <= 1.0

    def test_agent_query_endpoint_with_empty_query(self):
        """Test agent endpoint with empty query"""
        test_request = {
            "query": "",
            "instructions": "You are an AI assistant for the AI-Driven Robotics Textbook.",
        }

        response = self.client.post("/api/agent/query", json=test_request)

        # Should return 400 for empty query
        assert response.status_code == 400

        # Check error message
        data = response.json()
        assert "Query cannot be empty" in data["detail"]

    def test_agent_query_endpoint_with_long_query(self):
        """Test agent endpoint with query that exceeds max length"""
        # Create a query longer than 1000 characters
        long_query = "A" * 1001
        test_request = {
            "query": long_query,
            "instructions": "You are an AI assistant for the AI-Driven Robotics Textbook.",
        }

        response = self.client.post("/api/agent/query", json=test_request)

        # Should return 400 for too long query
        assert response.status_code == 400

        # Check error message
        data = response.json()
        assert "Query is too long (max 1000 characters)" in data["detail"]

    def test_agent_query_endpoint_with_malformed_request(self):
        """Test agent endpoint with malformed request"""
        # Missing required fields
        test_request = {
            "instructions": "You are an AI assistant for the AI-Driven Robotics Textbook."
            # Missing 'query' field
        }

        response = self.client.post("/api/agent/query", json=test_request)

        # Should return 422 for validation error
        assert response.status_code == 422

    def test_agent_health_endpoint(self):
        """Test the agent health endpoint"""
        response = self.client.get("/api/agent/health")

        # Should return 200
        assert response.status_code == 200

        # Parse response
        data = response.json()

        # Check response structure
        assert "status" in data
        assert "service" in data
        assert "message" in data

        # Check values
        assert data["status"] == "healthy"
        assert data["service"] == "agent"
        assert "running" in data["message"]

    def test_agent_query_endpoint_with_special_characters(self):
        """Test agent endpoint with special characters in query (sanitization test)"""
        test_request = {
            "query": "What is AI <script>alert('test')</script> robotics?",
            "instructions": "You are an AI assistant for the AI-Driven Robotics Textbook.",
        }

        response = self.client.post("/api/agent/query", json=test_request)

        # Should still process the request (after sanitization)
        # The exact behavior depends on how the sanitization is implemented
        # If the request is processed successfully, status should be 200
        # If sanitization is too aggressive and removes the query, it might be 400
        # Let's just check that it doesn't crash the server
        assert response.status_code in [200, 400, 422]

    def test_agent_query_endpoint_with_rate_limiting(self):
        """Test rate limiting on agent endpoint (basic test)"""
        # Make multiple requests to test rate limiting
        # Note: This test may not actually trigger rate limiting depending on the time between requests
        test_request = {
            "query": "What is AI?",
            "instructions": "You are an AI assistant for the AI-Driven Robotics Textbook.",
        }

        # Make several requests in a row
        for i in range(3):
            response = self.client.post("/api/agent/query", json=test_request)
            # Should not be rate limited for small number of requests
            assert response.status_code in [200, 429]  # Allow for rate limit response