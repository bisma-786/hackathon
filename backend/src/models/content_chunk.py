"""
ContentChunk model for the Book URL Ingestion Pipeline.
"""

import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional
from src.utils.validators import validate_content_chunk, is_valid_content_length, normalize_text


class ContentChunk:
    """
    Represents a segment of book content with text, embedding vector, and metadata.
    """

    def __init__(
        self,
        text: str,
        url: str,
        module: str,
        section: str,
        embedding: Optional[List[float]] = None,
        id: Optional[str] = None,
        heading_hierarchy: Optional[List[str]] = None,
        chunk_index: int = 0,
        source_length: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Initialize a ContentChunk instance.

        Args:
            text: The actual text content of the chunk
            url: Original URL of the source page
            module: Book module identifier
            section: Section title from the source page
            embedding: Vector embedding representation (optional)
            id: Unique identifier (SHA256 hash of content + URL) - will be generated if not provided
            heading_hierarchy: Array of parent headings in order (optional)
            chunk_index: Sequential index of this chunk within the source document
            source_length: Original length of the source content (optional, will be calculated)
            created_at: Timestamp when chunk was created (optional, defaults to now)
            updated_at: Timestamp when chunk was last updated (optional, defaults to now)
        """
        self.text = normalize_text(text) if text else ""
        self.url = url
        self.module = module
        self.section = section
        self.embedding = embedding or []
        self.heading_hierarchy = heading_hierarchy or []
        self.chunk_index = chunk_index
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

        # Generate ID if not provided
        if id:
            self.id = id
        else:
            self.id = self._generate_id()

        # Calculate source length if not provided
        if source_length is not None:
            self.source_length = source_length
        else:
            self.source_length = len(self.text)

    def _generate_id(self) -> str:
        """
        Generate a unique identifier based on content and URL.

        Returns:
            SHA256 hash string
        """
        content_to_hash = f"{self.url}|{self.text}".encode('utf-8')
        return hashlib.sha256(content_to_hash).hexdigest()

    def validate(self) -> List[str]:
        """
        Validate the content chunk according to the data model requirements.

        Returns:
            List of validation errors (empty if valid)
        """
        chunk_dict = self.to_dict()
        return validate_content_chunk(chunk_dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the ContentChunk instance to a dictionary.

        Returns:
            Dictionary representation of the ContentChunk
        """
        return {
            'id': self.id,
            'text': self.text,
            'embedding': self.embedding,
            'url': self.url,
            'module': self.module,
            'section': self.section,
            'heading_hierarchy': self.heading_hierarchy,
            'chunk_index': self.chunk_index,
            'source_length': self.source_length,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def to_dict_with_complete_metadata(self) -> Dict[str, Any]:
        """
        Convert the ContentChunk instance to a dictionary with complete metadata for storage.

        Returns:
            Dictionary representation of the ContentChunk with complete metadata
        """
        return {
            'id': self.id,
            'text': self.text,
            'embedding': self.embedding,
            'url': self.url,
            'module': self.module,
            'section': self.section,
            'heading_hierarchy': self.heading_hierarchy,
            'chunk_index': self.chunk_index,
            'source_length': self.source_length,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentChunk':
        """
        Create a ContentChunk instance from a dictionary.

        Args:
            data: Dictionary representation of a ContentChunk

        Returns:
            ContentChunk instance
        """
        return cls(
            text=data['text'],
            url=data['url'],
            module=data['module'],
            section=data['section'],
            embedding=data.get('embedding', []),
            id=data.get('id'),
            heading_hierarchy=data.get('heading_hierarchy', []),
            chunk_index=data.get('chunk_index', 0),
            source_length=data.get('source_length'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )

    def is_valid_length(self, max_tokens: int = 2000) -> bool:
        """
        Check if the content length is within acceptable limits.

        Args:
            max_tokens: Maximum allowed token count (default: 2000)

        Returns:
            True if within limits, False otherwise
        """
        return is_valid_content_length(self.text, max_tokens)

    def update_embedding(self, embedding: List[float]) -> None:
        """
        Update the embedding vector for this chunk.

        Args:
            embedding: New embedding vector
        """
        self.embedding = embedding
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        """
        String representation of the ContentChunk.
        """
        return f"ContentChunk(id={self.id[:8]}..., url={self.url}, module={self.module}, section={self.section})"

    def __eq__(self, other) -> bool:
        """
        Check equality based on ID.
        """
        if not isinstance(other, ContentChunk):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """
        Hash based on ID.
        """
        return hash(self.id)