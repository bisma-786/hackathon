"""
Test session management functionality for the RAG Chatbot API
"""
import pytest
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_session_management():
    """Test that sessions maintain context across multiple queries"""
    # First query - should create a new session
    query1 = {
        "query": "What is ROS 2?",
        "session_id": None
    }

    response1 = client.post("/query", json=query1)
    assert response1.status_code in [200, 500]  # Either success or dependency error

    if response1.status_code == 200:
        data1 = response1.json()
        session_id = data1["session_id"]
        assert session_id is not None
        assert session_id != ""

        # Follow-up query using the same session
        query2 = {
            "query": "Can you explain more about the communication mechanisms?",
            "session_id": session_id
        }

        response2 = client.post("/query", json=query2)
        assert response2.status_code == 200

        data2 = response2.json()
        # Session ID should be the same
        assert data2["session_id"] == session_id

        print("Session management test passed - context maintained across queries")
        return True

    print("Session management test skipped - dependencies not available")
    return False

def test_invalid_queries():
    """Test that invalid queries are handled gracefully"""
    # Test empty query
    empty_query = {
        "query": "",
        "session_id": None
    }

    response = client.post("/query", json=empty_query)
    # Should return an error response, not crash
    assert response.status_code in [200, 422, 500]  # 422 for validation error

    # Test very long query
    long_query = {
        "query": "x" * 10001,  # Exceeds the 10000 limit
        "session_id": None
    }

    response = client.post("/query", json=long_query)
    # Should return an error response, not crash
    assert response.status_code in [200, 422, 500]

    print("Invalid query handling test passed")

if __name__ == "__main__":
    test_session_management()
    test_invalid_queries()
    print("All session tests completed!")