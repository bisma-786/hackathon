#!/usr/bin/env python3
"""
Script to check the progress of the Qdrant vector store.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from src.utils.config import Config
from src.storage.qdrant_client import QdrantClient

def check_vector_count():
    config = Config()
    client = QdrantClient(config)
    count = client.get_vector_count(config.qdrant_collection_name)
    print(f'Current vector count: {count}')
    return count

if __name__ == "__main__":
    check_vector_count()