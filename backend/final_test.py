"""
Final test to confirm the agent responds properly with updated instructions
"""
from agent import answer_question

def final_test():
    """Test the agent with a query that should trigger the updated instructions"""
    print("=== FINAL TEST: Agent with Updated Instructions ===\n")

    # Test with a query that should match the available content
    query = "What topics are covered in this book?"
    print(f"Query: {query}")

    try:
        result = answer_question(query=query, session_id=None)

        print(f"Response: {result['response']}")
        print(f"Session ID: {result['session_id']}")
        print(f"Source chunks: {len(result['source_chunks'])}")
        print(f"Content quality: {result['content_quality']}")

        # Check if response follows the updated instructions
        response_lower = result['response'].lower()

        if "i couldn't process" in response_lower and result['content_quality']['has_valid_content']:
            print("\n❌ PROBLEM: Still getting default error despite valid content")
            print("   The updated instructions should prevent this when content exists")
        elif result['content_quality']['has_valid_content']:
            print("\n✅ SUCCESS: Agent responded with valid content available")
            print("   The updated instructions are working correctly")

            # Check if it explains what sections cover (based on the updated instructions)
            if any(word in response_lower for word in ["likely", "probably", "covers", "section", "topic", "chapter"]):
                print("   ✅ Agent is explaining what sections likely cover (as per updated instructions)")
        else:
            print("\n⚠️  No valid content was retrieved for this query")

    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    final_test()