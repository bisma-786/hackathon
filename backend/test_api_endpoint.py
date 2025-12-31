"""
Test the FastAPI endpoint directly
"""
import asyncio
import json
from api import app
from fastapi.testclient import TestClient

def test_api_endpoint():
    """Test the API endpoint directly"""
    print("[API TEST] Testing FastAPI endpoint...")

    # Create a test client
    client = TestClient(app)

    # Test the root endpoint
    response = client.get("/")
    print(f"[API] Root endpoint status: {response.status_code}")
    print(f"[API] Root endpoint response: {response.json()}")

    # Test the query endpoint with a sample query
    query_data = {
        "query": "What topics are covered in this book?",
        "session_id": None
    }

    response = client.post("/query", json=query_data)
    print(f"[API] Query endpoint status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"[SUCCESS] Query processed successfully")
        print(f"[RESULT] Response preview: {result['response'][:100]}...")
        print(f"[RESULT] Session ID: {result['session_id']}")
        print(f"[RESULT] Source chunks: {len(result['source_chunks'])}")
    else:
        print(f"[ERROR] Query endpoint returned error: {response.status_code}")
        print(f"[ERROR] Error details: {response.text}")

    return response.status_code == 200

if __name__ == "__main__":
    success = test_api_endpoint()
    if success:
        print("\n[COMPLETE] API endpoint test completed successfully!")
    else:
        print("\n[ERROR] API endpoint test failed!")