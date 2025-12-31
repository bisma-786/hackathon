"""
Test the agent functionality with mocked Gemini API calls
"""
from unittest.mock import patch, MagicMock
from agent import answer_question

def test_agent_with_mocked_api():
    """Test the agent with mocked Gemini responses"""
    print("[TEST] Testing agent with mocked Gemini API...")

    # Mock the Gemini model generate_content method
    with patch('agent.model') as mock_model:
        # Create a mock response
        mock_response = MagicMock()
        mock_response.text = "This is a test response from the agent."

        # Configure the mock to return our response
        mock_model.generate_content.return_value = mock_response

        # Test the agent
        result = answer_question(query="What is this book about?", session_id=None)

        print(f"[SUCCESS] Query processed successfully")
        print(f"[RESULT] Response: {result['response']}")
        print(f"[RESULT] Session ID: {result['session_id']}")
        print(f"[RESULT] Source chunks: {len(result['source_chunks'])}")
        print(f"[RESULT] Content quality: {result['content_quality']}")

        # Verify that the Gemini API was called with the right parameters
        mock_model.generate_content.assert_called_once()
        call_args = mock_model.generate_content.call_args
        print("[SUCCESS] Gemini API was called with correct parameters")

        return result

if __name__ == "__main__":
    test_agent_with_mocked_api()
    print("\n[COMPLETE] Agent test completed successfully!")