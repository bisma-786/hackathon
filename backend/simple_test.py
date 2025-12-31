"""
Simple test to verify the agent responds with the updated instructions using Gemini API
"""
from agent import answer_question

def simple_test():
    """Simple test to see if agent responds with basic setup"""
    print("Testing basic agent response...")

    # Test the agent with a simple query
    result = answer_question(
        query="What is this book about?",
        session_id=None
    )

    print(f"Agent response: {result['response']}")
    print(f"Session ID: {result['session_id']}")
    print(f"Source chunks used: {len(result['source_chunks'])}")
    print(f"Content quality: {result['content_quality']['has_valid_content']}")

if __name__ == "__main__":
    simple_test()