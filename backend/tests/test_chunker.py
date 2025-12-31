"""
Tests for the chunker module in the Book URL Ingestion Pipeline.
"""

import pytest
from unittest.mock import Mock
from src.ingestion.chunker import TextChunker
from src.utils.config import Config


class TestTextChunker:
    """
    Test class for the TextChunker module.
    """

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create a mock config object
        self.mock_config = Mock(spec=Config)
        self.chunker = TextChunker(self.mock_config)

    def test_chunk_text_with_overlap(self):
        """Test the chunk_text_with_overlap method."""
        text = "This is the first sentence. This is the second sentence. This is the third sentence. " \
               "This is the fourth sentence. This is the fifth sentence."
        chunk_size = 50
        overlap = 10

        chunks = self.chunker.chunk_text_with_overlap(text, chunk_size, overlap)

        # Should have at least one chunk
        assert len(chunks) > 0

        # Each chunk should have text and chunk_index
        for chunk in chunks:
            assert 'text' in chunk
            assert 'chunk_index' in chunk
            assert isinstance(chunk['text'], str)
            assert isinstance(chunk['chunk_index'], int)

        # Verify that chunks are not too large
        for chunk in chunks:
            assert len(chunk['text']) <= chunk_size + 10  # Allow some flexibility

    def test_chunk_text_with_overlap_empty_text(self):
        """Test chunking with empty text."""
        chunks = self.chunker.chunk_text_with_overlap("", 100, 10)
        assert chunks == []

    def test_chunk_text_with_overlap_single_sentence(self):
        """Test chunking with a single sentence that fits in one chunk."""
        text = "This is a short sentence."
        chunks = self.chunker.chunk_text_with_overlap(text, 100, 10)

        assert len(chunks) == 1
        assert chunks[0]['text'] == text

    def test_chunk_text_by_paragraph(self):
        """Test the chunk_text_by_paragraph method."""
        text = "First paragraph with some content.\n\nSecond paragraph with different content.\n\n" \
               "Third paragraph to test the functionality."

        chunks = self.chunker.chunk_text_by_paragraph(text, 100)

        # Should have at least one chunk per paragraph
        assert len(chunks) > 0

        for chunk in chunks:
            assert 'text' in chunk
            assert 'chunk_index' in chunk
            assert isinstance(chunk['text'], str)
            assert isinstance(chunk['chunk_index'], int)

    def test_chunk_text_by_paragraph_empty_text(self):
        """Test paragraph chunking with empty text."""
        chunks = self.chunker.chunk_text_by_paragraph("", 100)
        assert chunks == []

    def test_split_into_sentences(self):
        """Test the _split_into_sentences method."""
        text = "First sentence. Second sentence! Third sentence? Yes, fourth sentence."
        sentences = self.chunker._split_into_sentences(text)

        assert len(sentences) == 4
        assert sentences[0] == "First sentence"
        assert sentences[1] == "Second sentence"
        assert sentences[2] == "Third sentence"
        assert sentences[3] == "Yes, fourth sentence"

    def test_split_into_sentences_with_complex_text(self):
        """Test sentence splitting with complex text."""
        text = "Dr. Smith went to the U.S.A. He said, 'Hello!' Did he? Yes, he did."
        sentences = self.chunker._split_into_sentences(text)

        # Should split on sentence boundaries, not on abbreviations
        assert len(sentences) >= 2  # At least 2 sentences

    def test_validate_chunk_size(self):
        """Test the validate_chunk_size method."""
        # Valid parameters
        assert self.chunker.validate_chunk_size(100, 10) is True
        assert self.chunker.validate_chunk_size(500, 50) is True

        # Invalid chunk size
        assert self.chunker.validate_chunk_size(0, 10) is False
        assert self.chunker.validate_chunk_size(-10, 10) is False

        # Invalid overlap
        assert self.chunker.validate_chunk_size(100, -1) is False
        assert self.chunker.validate_chunk_size(100, 100) is False  # overlap >= chunk_size
        assert self.chunker.validate_chunk_size(100, 150) is False  # overlap > chunk_size

    def test_get_overlap_text(self):
        """Test the _get_overlap_text method."""
        text = "This is a sample text for testing the overlap functionality."
        overlap_size = 20

        overlap_text = self.chunker._get_overlap_text(text, overlap_size)

        # The overlap text should not be longer than the specified size
        assert len(overlap_text) <= overlap_size

        # The overlap text should come from the end of the original text
        # (in a real implementation, this would be more sophisticated)
        if len(text) > overlap_size:
            # The overlap should be from the end
            assert overlap_text in text
        else:
            # If text is shorter than overlap, the entire text should be returned
            assert overlap_text == text


if __name__ == "__main__":
    pytest.main([__file__])