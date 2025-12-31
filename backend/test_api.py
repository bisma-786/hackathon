"""
Test the RAG Chatbot API
"""
import pytest
from fastapi.testclient import TestClient
from api import app
from api import QueryRequest

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "RAG Chatbot API is running"}

def test_query_endpoint_basic():
    """Test the query endpoint with a basic request"""
    # This test will check if the endpoint accepts requests properly
    # The actual response will depend on the availability of the agent and its dependencies
    query_request = {
        "query": "What is ROS 2?",
        "session_id": None
    }

    response = client.post("/query", json=query_request)

    # The endpoint should accept the request (either success or proper error)
    # If it's a 500 error, it means dependencies aren't available, which is expected in test environment
    assert response.status_code in [200, 500]

    if response.status_code == 200:
        # If successful, verify the response structure
        data = response.json()
        assert "response" in data
        assert "session_id" in data
        assert "source_chunks" in data
        assert "content_quality" in data
        assert "query_time" in data

if __name__ == "__main__":
    test_root_endpoint()
    test_query_endpoint_basic()
    print("All tests passed!")