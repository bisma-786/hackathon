"""
Text chunking module for the Book URL Ingestion Pipeline.
"""

import re
from typing import Dict, List
from src.utils.config import Config


class TextChunker:
    """
    Handles text chunking with overlap for the Book URL Ingestion Pipeline.
    """

    def __init__(self, config: Config):
        self.config = config

    def chunk_text_with_overlap(self, text: str, chunk_size: int, overlap: int) -> List[Dict]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text to chunk
            chunk_size: Size of each chunk
            overlap: Overlap between chunks

        Returns:
            List of chunk dictionaries
        """
        if not text:
            return []

        # Tokenize text into sentences or paragraphs
        sentences = self._split_into_sentences(text)

        chunks = []
        current_chunk = ""
        current_length = 0
        chunk_index = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            # If adding this sentence would exceed chunk size
            if current_length + sentence_length > chunk_size:
                # If current chunk is not empty, save it
                if current_chunk.strip():
                    chunks.append({
                        'text': current_chunk.strip(),
                        'chunk_index': chunk_index
                    })
                    chunk_index += 1

                # Start new chunk with overlap if possible
                if overlap > 0:
                    # Find overlap content from the end of current text
                    overlap_text = self._get_overlap_text(current_chunk, overlap)
                    current_chunk = overlap_text + " " + sentence
                    current_length = len(overlap_text) + 1 + sentence_length
                else:
                    current_chunk = sentence
                    current_length = sentence_length
            else:
                # Add sentence to current chunk
                if current_chunk:
                    current_chunk += " " + sentence
                    current_length += 1 + sentence_length
                else:
                    current_chunk = sentence
                    current_length = sentence_length

        # Add the last chunk if it has content
        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'chunk_index': chunk_index
            })

        return chunks

    def implement_sliding_window_chunking(self, text: str, chunk_size: int, overlap: int) -> List[Dict]:
        """
        Implement sliding window chunking with configurable size and overlap.

        Args:
            text: Text to chunk
            chunk_size: Size of each chunk
            overlap: Overlap between chunks

        Returns:
            List of chunk dictionaries
        """
        if not text or chunk_size <= 0:
            return []

        chunks = []
        start_idx = 0
        chunk_index = 0

        while start_idx < len(text):
            # Calculate end index
            end_idx = start_idx + chunk_size

            # If this is the last chunk and it's smaller than chunk_size, include it
            if end_idx >= len(text):
                chunk_text = text[start_idx:]
            else:
                # Try to break at sentence boundary if possible
                chunk_text = text[start_idx:end_idx]

                # Find the last sentence ending within the chunk
                last_sentence_end = -1
                for ending in ['.', '!', '?']:
                    pos = chunk_text.rfind(ending)
                    if pos > last_sentence_end:
                        last_sentence_end = pos

                # If we found a sentence ending and it's not too close to the beginning
                if last_sentence_end > len(chunk_text) // 2:
                    end_idx = start_idx + last_sentence_end + 1
                    chunk_text = text[start_idx:end_idx]

            # Add the chunk if it's not empty
            if chunk_text.strip():
                chunks.append({
                    'text': chunk_text.strip(),
                    'chunk_index': chunk_index
                })
                chunk_index += 1

            # Move to next position with overlap
            if start_idx + chunk_size >= len(text):
                # Last chunk, no more chunks to create
                break

            # Calculate next start position with overlap
            next_start = start_idx + chunk_size - overlap
            start_idx = next_start

        return chunks

    def add_chunk_validation(self, chunks: List[Dict], max_token_count: int = 2000) -> List[Dict]:
        """
        Add validation to ensure consistent token counts in chunks.

        Args:
            chunks: List of chunk dictionaries to validate
            max_token_count: Maximum allowed token count per chunk

        Returns:
            List of validated chunks
        """
        validated_chunks = []
        for chunk in chunks:
            # Simple token estimation (in a real implementation, use proper tokenization)
            estimated_tokens = len(chunk['text'].split())
            if estimated_tokens <= max_token_count:
                validated_chunks.append(chunk)
            else:
                # If chunk is too large, split it further
                sub_chunks = self.chunk_text_with_overlap(
                    chunk['text'],
                    max_token_count,
                    max_token_count // 4  # 25% overlap
                )
                validated_chunks.extend(sub_chunks)

        return validated_chunks

    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.

        Args:
            text: Text to split

        Returns:
            List of sentences
        """
        # Use regex to split on sentence endings (., !, ?) followed by whitespace or end of string
        # This preserves the sentence endings in the result
        sentences = re.split(r'(?<=[.!?])\s+', text)
        # Remove empty strings and strip whitespace
        return [s.strip() for s in sentences if s.strip()]

    def _get_overlap_text(self, text: str, overlap_size: int) -> str:
        """
        Get the last part of text that fits within the overlap size.

        Args:
            text: Text to extract overlap from
            overlap_size: Maximum size of overlap

        Returns:
            Overlap text
        """
        if len(text) <= overlap_size:
            return text

        # Try to break at sentence boundary if possible
        sentences = self._split_into_sentences(text)
        overlap_text = ""

        # Start from the end and add sentences until we exceed overlap_size
        for sentence in reversed(sentences):
            test_text = sentence + " " + overlap_text
            if len(test_text.strip()) <= overlap_size:
                overlap_text = test_text.strip()
            else:
                break

        # If we couldn't fit even one sentence, just take the end portion
        if not overlap_text and len(text) > overlap_size:
            return text[-overlap_size:].strip()

        return overlap_text

    def chunk_text_by_paragraph(self, text: str, chunk_size: int) -> List[Dict]:
        """
        Split text into chunks by paragraphs.

        Args:
            text: Text to chunk
            chunk_size: Maximum size of each chunk

        Returns:
            List of chunk dictionaries
        """
        # Split by paragraphs (double newlines)
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        current_length = 0
        chunk_index = 0

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            paragraph_length = len(paragraph)

            if current_length + paragraph_length <= chunk_size:
                # Add paragraph to current chunk
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                    current_length += 2 + paragraph_length
                else:
                    current_chunk = paragraph
                    current_length = paragraph_length
            else:
                # Save current chunk and start a new one
                if current_chunk.strip():
                    chunks.append({
                        'text': current_chunk.strip(),
                        'chunk_index': chunk_index
                    })
                    chunk_index += 1

                # If paragraph is too large, split it into sentences
                if paragraph_length > chunk_size:
                    sub_chunks = self.chunk_text_with_overlap(paragraph, chunk_size, 0)
                    for sub_chunk in sub_chunks:
                        sub_chunk['chunk_index'] = chunk_index
                        chunks.append(sub_chunk)
                        chunk_index += 1
                else:
                    current_chunk = paragraph
                    current_length = paragraph_length

        # Add the last chunk
        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'chunk_index': chunk_index
            })

        return chunks

    def validate_chunk_size(self, chunk_size: int, overlap: int) -> bool:
        """
        Validate chunk size and overlap parameters.

        Args:
            chunk_size: Size of chunks
            overlap: Overlap between chunks

        Returns:
            True if parameters are valid, False otherwise
        """
        return chunk_size > 0 and overlap >= 0 and overlap < chunk_size


# Example usage and testing
if __name__ == "__main__":
    # This would require actual text content to run
    pass