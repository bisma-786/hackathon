"""
Direct test of the agent functionality without API layer
"""
from agent import answer_question

def test_direct_agent():
    """Test the agent directly without API wrapper"""
    print("Testing agent directly...")

    query = "What is ROS 2?"
    result = answer_question(query=query, session_id=None)

    print(f"Query: {query}")
    print(f"Response: {result['response']}")
    print(f"Session ID: {result['session_id']}")
    print(f"Number of source chunks: {len(result['source_chunks'])}")
    print(f"Content quality: {result['content_quality']}")

    print("\nTop 3 source chunks:")
    for i, chunk in enumerate(result['source_chunks'][:3]):
        print(f"  {i+1}. ID: {chunk['id']}")
        print(f"     Score: {chunk['score']}")
        print(f"     Content preview: {chunk['content'][:100]}...")
        print()

if __name__ == "__main__":
    test_direct_agent()