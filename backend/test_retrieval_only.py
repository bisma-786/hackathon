"""
Test just the retrieval functionality without the OpenAI API call
"""
from agent import retrieve_chunks, check_retrieved_content_quality

def test_retrieval_functionality():
    """Test just the retrieval functionality"""
    print("[RETRIEVAL TEST] Testing Qdrant retrieval functionality...")

    # Test with a simple query
    query = "What is ROS 2?"

    # Retrieve chunks from Qdrant
    retrieved_chunks = retrieve_chunks(query=query, top_k=3)

    print(f"[SUCCESS] Retrieved {len(retrieved_chunks)} chunks from Qdrant")

    for i, chunk in enumerate(retrieved_chunks):
        print(f"  Chunk {i+1}: Score={chunk.score:.4f}, Content='{chunk.content[:100]}...'")

    # Check the quality of retrieved content
    content_quality = check_retrieved_content_quality(retrieved_chunks, min_score=0.02)

    print(f"[QUALITY] Total chunks: {content_quality['total_chunks']}")
    print(f"[QUALITY] Valid chunks: {content_quality['valid_chunks']}")
    print(f"[QUALITY] Low score chunks: {content_quality['low_score_chunks']}")
    print(f"[QUALITY] Has valid content: {content_quality['has_valid_content']}")
    print(f"[QUALITY] Average score: {content_quality['average_score']:.4f}")

    if content_quality['has_valid_content']:
        print("\n[SUCCESS] [CHECKMARK] Retrieval system is working properly!")
        print("   - Successfully connects to Qdrant")
        print("   - Finds relevant content for queries")
        print("   - Content quality is adequate for RAG system")
        print("   - Ready to provide context to the agent")
    else:
        print("\n[ISSUE] [WARNING] Retrieval system needs attention")

    return len(retrieved_chunks) > 0 and content_quality['has_valid_content']

if __name__ == "__main__":
    success = test_retrieval_functionality()
    if success:
        print("\n[COMPLETE] Retrieval test passed - system is ready!")
    else:
        print("\n[ERROR] Retrieval test failed!")