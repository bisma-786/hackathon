"""
Test the agent with a query that might match the available content
"""
from agent import answer_question

def test_specific_query():
    """Test the agent with various queries"""
    print("Testing agent with various queries...")

    # Test 1: Query about content we know exists based on the diagnostic
    queries = [
        "What is in the tutorial extras section?",
        "Tell me about Gazebo physics simulation",
        "What is in the module 3 section?",
        "What is in the tutorial basics section?",
        "What is this book about?"
    ]

    for query in queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        result = answer_question(query=query, session_id=None)

        print(f"Response: {result['response']}")
        print(f"Session ID: {result['session_id']}")
        print(f"Number of source chunks: {len(result['source_chunks'])}")
        print(f"Content quality: {result['content_quality']}")

        print("\nTop 3 source chunks:")
        for i, chunk in enumerate(result['source_chunks'][:3]):
            print(f"  {i+1}. ID: {chunk.id}")
            print(f"     Score: {chunk.score}")
            print(f"     Content preview: {chunk.content[:150]}...")
            print(f"     Metadata: {chunk.metadata}")
            print()

if __name__ == "__main__":
    test_specific_query()