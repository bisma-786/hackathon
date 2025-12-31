"""
Test the agent with the updated instructions to see if it responds correctly
"""
from agent import answer_question

def test_agent_with_updated_instructions():
    """Test the agent with the new instructions"""
    print("Testing agent with updated instructions...")

    # Test with a query that should trigger the new instructions
    query = "What is this book about?"
    print(f"\nQuery: {query}")

    result = answer_question(query=query, session_id=None)

    print(f"Response: {result['response']}")
    print(f"Session ID: {result['session_id']}")
    print(f"Number of source chunks: {len(result['source_chunks'])}")
    print(f"Content quality: {result['content_quality']}")

    # Check if the response follows the new instructions
    response = result['response'].lower()

    if "couldn't process your request" in response:
        print("\n❌ ISSUE: Still getting the old error message despite updated instructions")
        print("   The new instructions should prevent this response when content is available")
    elif result['content_quality']['has_valid_content']:
        print("\n✅ SUCCESS: Agent responded without the default error message")
        print("   The updated instructions are taking effect")
    else:
        print("\n⚠️  CONTENT QUALITY ISSUE: No valid content was retrieved")

if __name__ == "__main__":
    test_agent_with_updated_instructions()