#!/usr/bin/env python3
"""
Test script to verify the retrieval and content quality in Qdrant.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from src.utils.config import Config
from src.storage.qdrant_client import QdrantClient
from src.embedding.generator import EmbeddingGenerator

def test_retrieval():
    config = Config()
    qdrant_client = QdrantClient(config)
    embedding_generator = EmbeddingGenerator(config)

    print("Testing retrieval with meaningful queries...")

    # Test query 1: "Explain Gazebo Physics Simulation"
    query = "Explain Gazebo Physics Simulation"
    print(f"\nQuery: {query}")

    # Generate embedding for the query
    query_embedding = embedding_generator.generate_single_embedding(query)

    # Search for similar content in Qdrant
    results = qdrant_client.search_similar(
        collection_name=config.qdrant_collection_name,
        query_vector=query_embedding,
        limit=3
    )

    print(f"Found {len(results)} results:")
    for i, result in enumerate(results):
        print(f"\nResult {i+1} (score: {result['score']:.3f}):")
        print(f"URL: {result['payload'].get('url', 'N/A')}")
        print(f"Module: {result['payload'].get('module', 'N/A')}")
        print(f"Section: {result['payload'].get('section', 'N/A')}")
        print(f"Text preview: {result['payload'].get('text_preview', 'N/A')[:200]}...")
        print(f"Full text length: {len(result['payload'].get('text', ''))} characters")

    # Test query 2: "ROS2 fundamentals"
    query2 = "ROS2 fundamentals"
    print(f"\nQuery: {query2}")

    query_embedding2 = embedding_generator.generate_single_embedding(query2)
    results2 = qdrant_client.search_similar(
        collection_name=config.qdrant_collection_name,
        query_vector=query_embedding2,
        limit=3
    )

    print(f"Found {len(results2)} results:")
    for i, result in enumerate(results2):
        print(f"\nResult {i+1} (score: {result['score']:.3f}):")
        print(f"URL: {result['payload'].get('url', 'N/A')}")
        print(f"Module: {result['payload'].get('module', 'N/A')}")
        print(f"Section: {result['payload'].get('section', 'N/A')}")
        print(f"Text preview: {result['payload'].get('text_preview', 'N/A')[:200]}...")
        print(f"Full text length: {len(result['payload'].get('text', ''))} characters")

    # Check total vector count
    count = qdrant_client.get_vector_count(config.qdrant_collection_name)
    print(f"\nTotal vectors in collection: {count}")

if __name__ == "__main__":
    test_retrieval()