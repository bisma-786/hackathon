"""
Diagnostic script to check what's in the Qdrant collection
"""
import os
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def diagnose_qdrant():
    """Diagnose what's in the Qdrant collection"""
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    collection_name = os.getenv("QDRANT_COLLECTION_NAME", "book_content_chunks")

    print(f"Connecting to Qdrant at: {qdrant_url}")
    print(f"Using collection: {collection_name}")

    # Initialize client
    client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key, timeout=30)

    # Get collection info
    try:
        collection_info = client.get_collection(collection_name)
        print(f"\nCollection Info: {collection_info}")

        # Get a sample of points to see the payload structure
        sample_points, next_offset = client.scroll(
            collection_name=collection_name,
            limit=3,  # Get first 3 points
            with_payload=True,
            with_vectors=False
        )

        print(f"\nSample Points Payload Structure:")
        for i, point in enumerate(sample_points):
            print(f"\nPoint {i+1}:")
            print(f"  ID: {point.id}")
            print(f"  Payload keys: {list(point.payload.keys()) if point.payload else 'No payload'}")
            if point.payload:
                for key, value in point.payload.items():
                    if key == 'content' or key == 'text' or 'content' in key.lower() or 'text' in key.lower():
                        print(f"  {key}: {str(value)[:100]}...")  # Show first 100 chars
                    else:
                        print(f"  {key}: {value}")

    except Exception as e:
        print(f"Error accessing Qdrant: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_qdrant()