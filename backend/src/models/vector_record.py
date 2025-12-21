from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class VectorRecord:
    """
    Represents a single vector chunk with its associated metadata and embedding data.
    """
    id: str
    embedding: List[float]
    metadata: Dict[str, str]  # Contains URL, module, section, position, hash, source_text
    timestamps: Dict[str, datetime]  # ingestion and retrieval timestamps

    @classmethod
    def create_from_qdrant_payload(
        cls,
        vector_id: str,
        embedding: List[float],
        payload: Dict
    ) -> 'VectorRecord':
        """
        Create a VectorRecord from Qdrant payload data
        """
        metadata = {
            'url': payload.get('url', ''),
            'module': payload.get('module', ''),
            'section': payload.get('section', ''),
            'position': str(payload.get('position', 0)),
            'hash': payload.get('hash', ''),
            'source_text': payload.get('source_text', '')
        }

        timestamps = {
            'ingestion': datetime.fromisoformat(payload.get('ingestion_timestamp', datetime.now().isoformat())),
            'retrieval': datetime.now()  # Set current time as retrieval time
        }

        return cls(
            id=vector_id,
            embedding=embedding,
            metadata=metadata,
            timestamps=timestamps
        )

    def to_dict(self) -> Dict:
        """
        Convert VectorRecord to dictionary format for API responses
        """
        return {
            'id': self.id,
            'embedding': self.embedding,
            'metadata': self.metadata,
            'timestamps': {
                'ingestion': self.timestamps['ingestion'].isoformat(),
                'retrieval': self.timestamps['retrieval'].isoformat()
            }
        }