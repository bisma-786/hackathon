"""
VectorRecord model for the Book URL Ingestion Pipeline.
"""

from typing import Any, Dict, List, Optional
from src.utils.validators import validate_vector_record


class VectorRecord:
    """
    Represents an indexed item in Qdrant with embedding vector and associated metadata.
    """

    def __init__(
        self,
        point_id: str,
        vector: List[float],
        payload: Dict[str, Any],
        collection_name: str
    ):
        """
        Initialize a VectorRecord instance.

        Args:
            point_id: Unique identifier in Qdrant (same as ContentChunk.id)
            vector: The embedding vector
            payload: Metadata payload containing URL, module, section, etc.
            collection_name: Name of the Qdrant collection
        """
        if not point_id or not isinstance(point_id, str):
            raise ValueError("Point ID must be a non-empty string")

        if not vector or not isinstance(vector, list):
            raise ValueError("Vector must be a non-empty list")

        if not payload or not isinstance(payload, dict):
            raise ValueError("Payload must be a non-empty dictionary")

        if not collection_name or not isinstance(collection_name, str):
            raise ValueError("Collection name must be a non-empty string")

        # Validate required payload fields
        required_payload_fields = ['url', 'module', 'section']
        for field in required_payload_fields:
            if field not in payload:
                raise ValueError(f"Payload must contain '{field}' field")

        self.point_id = point_id
        self.vector = vector
        self.payload = payload
        self.collection_name = collection_name

    def validate(self) -> List[str]:
        """
        Validate the vector record according to the data model requirements.

        Returns:
            List of validation errors (empty if valid)
        """
        record_dict = self.to_dict()
        return validate_vector_record(record_dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the VectorRecord instance to a dictionary.

        Returns:
            Dictionary representation of the VectorRecord
        """
        return {
            'point_id': self.point_id,
            'vector': self.vector,
            'payload': self.payload,
            'collection_name': self.collection_name
        }

    def to_dict_with_complete_metadata(self) -> Dict[str, Any]:
        """
        Convert the VectorRecord instance to a dictionary with complete metadata for storage.

        Returns:
            Dictionary representation of the VectorRecord with complete metadata
        """
        return {
            'point_id': self.point_id,
            'vector': self.vector,
            'payload': self.payload,
            'collection_name': self.collection_name
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VectorRecord':
        """
        Create a VectorRecord instance from a dictionary.

        Args:
            data: Dictionary representation of a VectorRecord

        Returns:
            VectorRecord instance
        """
        return cls(
            point_id=data['point_id'],
            vector=data['vector'],
            payload=data['payload'],
            collection_name=data['collection_name']
        )

    def update_payload(self, new_payload: Dict[str, Any]) -> None:
        """
        Update the payload of the vector record.

        Args:
            new_payload: New payload dictionary
        """
        # Validate required fields in new payload
        required_fields = ['url', 'module', 'section']
        for field in required_fields:
            if field not in new_payload:
                raise ValueError(f"New payload must contain '{field}' field")

        self.payload = new_payload

    def update_vector(self, new_vector: List[float]) -> None:
        """
        Update the embedding vector of the record.

        Args:
            new_vector: New embedding vector
        """
        if not new_vector or not isinstance(new_vector, list):
            raise ValueError("Vector must be a non-empty list")

        self.vector = new_vector

    def __repr__(self) -> str:
        """
        String representation of the VectorRecord.
        """
        return f"VectorRecord(point_id={self.point_id}, collection={self.collection_name}, vector_size={len(self.vector)})"

    def __eq__(self, other) -> bool:
        """
        Check equality based on point_id and collection_name.
        """
        if not isinstance(other, VectorRecord):
            return False
        return self.point_id == other.point_id and self.collection_name == other.collection_name

    def __hash__(self) -> int:
        """
        Hash based on point_id and collection_name.
        """
        return hash((self.point_id, self.collection_name))