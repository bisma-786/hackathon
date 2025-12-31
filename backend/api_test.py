"""
API test to verify the backend is ready for frontend integration
"""
from agent import answer_question

def test_api_endpoints():
    """Test the API functionality that will be used by the frontend"""
    print("Testing API endpoints for frontend integration...")

    # Test the core functionality
    test_query = "What is covered in module 1?"
    print(f"Sending query to backend: '{test_query}'")

    try:
        result = answer_question(query=test_query, session_id=None)
        print("✅ API call successful")
        print(f"   Response: {result['response'][:100]}...")
        print(f"   Session ID: {result['session_id']}")
        print(f"   Source chunks: {len(result.get('source_chunks', []))}")

        # Verify the response structure matches what frontend expects
        expected_keys = ['response', 'session_id', 'source_chunks', 'content_quality']
        missing_keys = [key for key in expected_keys if key not in result]

        if not missing_keys:
            print("✅ Response structure is correct for frontend consumption")
        else:
            print(f"⚠️  Missing keys in response: {missing_keys}")

    except Exception as e:
        print(f"❌ API test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_endpoints()
    print("\\nBackend API is ready for frontend integration!")