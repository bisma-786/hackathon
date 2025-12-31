"""
Data validation utilities for the Book URL Ingestion Pipeline.
"""

import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    """
    Validate if a string is a valid URL.

    Args:
        url: URL string to validate

    Returns:
        True if valid URL, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_content_chunk(chunk: Dict[str, Any]) -> List[str]:
    """
    Validate a content chunk according to the data model requirements.

    Args:
        chunk: Content chunk dictionary to validate

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Check required fields
    required_fields = ['id', 'text', 'embedding', 'url', 'module', 'section']
    for field in required_fields:
        if field not in chunk:
            errors.append(f"Missing required field: {field}")

    # Validate field types and constraints
    if 'id' in chunk and not isinstance(chunk['id'], str):
        errors.append("Field 'id' must be a string")

    if 'text' in chunk:
        if not isinstance(chunk['text'], str):
            errors.append("Field 'text' must be a string")
        elif len(chunk['text']) == 0:
            errors.append("Field 'text' cannot be empty")

    if 'embedding' in chunk:
        if not isinstance(chunk['embedding'], list):
            errors.append("Field 'embedding' must be a list")
        elif len(chunk['embedding']) == 0:
            errors.append("Field 'embedding' cannot be empty")

    if 'url' in chunk:
        if not isinstance(chunk['url'], str) or not is_valid_url(chunk['url']):
            errors.append("Field 'url' must be a valid URL string")

    if 'module' in chunk:
        if not isinstance(chunk['module'], str) or len(chunk['module']) == 0:
            errors.append("Field 'module' must be a non-empty string")

    if 'section' in chunk:
        if not isinstance(chunk['section'], str) or len(chunk['section']) == 0:
            errors.append("Field 'section' must be a non-empty string")

    if 'heading_hierarchy' in chunk:
        if not isinstance(chunk['heading_hierarchy'], list):
            errors.append("Field 'heading_hierarchy' must be a list")
        else:
            for i, heading in enumerate(chunk['heading_hierarchy']):
                if not isinstance(heading, str):
                    errors.append(f"Item {i} in 'heading_hierarchy' must be a string")

    if 'chunk_index' in chunk:
        if not isinstance(chunk['chunk_index'], int) or chunk['chunk_index'] < 0:
            errors.append("Field 'chunk_index' must be a non-negative integer")

    if 'source_length' in chunk:
        if not isinstance(chunk['source_length'], int) or chunk['source_length'] < 0:
            errors.append("Field 'source_length' must be a non-negative integer")

    return errors


def validate_book_page(page: Dict[str, Any]) -> List[str]:
    """
    Validate a book page according to the data model requirements.

    Args:
        page: Book page dictionary to validate

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Check required fields
    required_fields = ['url']
    for field in required_fields:
        if field not in page:
            errors.append(f"Missing required field: {field}")

    # Validate field types and constraints
    if 'url' in page:
        if not isinstance(page['url'], str) or not is_valid_url(page['url']):
            errors.append("Field 'url' must be a valid URL string")

    if 'module' in page:
        if not isinstance(page['module'], str) or len(page['module']) == 0:
            errors.append("Field 'module' must be a non-empty string")

    if 'section_title' in page:
        if not isinstance(page['section_title'], str) or len(page['section_title']) == 0:
            errors.append("Field 'section_title' must be a non-empty string")

    if 'heading_hierarchy' in page:
        if not isinstance(page['heading_hierarchy'], list):
            errors.append("Field 'heading_hierarchy' must be a list")
        else:
            for i, heading in enumerate(page['heading_hierarchy']):
                if not isinstance(heading, str):
                    errors.append(f"Item {i} in 'heading_hierarchy' must be a string")

    if 'crawl_status' in page:
        valid_statuses = ['pending', 'crawling', 'success', 'failed', 'retry']
        if page['crawl_status'] not in valid_statuses:
            errors.append(f"Field 'crawl_status' must be one of {valid_statuses}")

    if 'content_length' in page:
        if not isinstance(page['content_length'], int) or page['content_length'] < 0:
            errors.append("Field 'content_length' must be a non-negative integer")

    if 'word_count' in page:
        if not isinstance(page['word_count'], int) or page['word_count'] < 0:
            errors.append("Field 'word_count' must be a non-negative integer")

    return errors


def validate_vector_record(record: Dict[str, Any]) -> List[str]:
    """
    Validate a vector record according to the data model requirements.

    Args:
        record: Vector record dictionary to validate

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Check required fields
    required_fields = ['point_id', 'vector', 'payload']
    for field in required_fields:
        if field not in record:
            errors.append(f"Missing required field: {field}")

    # Validate field types and constraints
    if 'point_id' in record:
        if not isinstance(record['point_id'], str):
            errors.append("Field 'point_id' must be a string")

    if 'vector' in record:
        if not isinstance(record['vector'], list):
            errors.append("Field 'vector' must be a list")
        elif len(record['vector']) == 0:
            errors.append("Field 'vector' cannot be empty")
        else:
            for i, value in enumerate(record['vector']):
                if not isinstance(value, (int, float)):
                    errors.append(f"Item {i} in 'vector' must be a number")

    if 'payload' in record:
        if not isinstance(record['payload'], dict):
            errors.append("Field 'payload' must be a dictionary")
        else:
            # Validate required payload fields
            payload = record['payload']
            required_payload_fields = ['url', 'module', 'section']
            for field in required_payload_fields:
                if field not in payload:
                    errors.append(f"Missing required payload field: {field}")

    if 'collection_name' in record:
        if not isinstance(record['collection_name'], str):
            errors.append("Field 'collection_name' must be a string")

    return errors


def is_valid_content_length(text: str, max_tokens: int = 2000) -> bool:
    """
    Check if content length is within acceptable limits.

    Args:
        text: Text content to check
        max_tokens: Maximum allowed token count (default: 2000)

    Returns:
        True if within limits, False otherwise
    """
    # Simple token estimation (in a real implementation, use proper tokenization)
    estimated_tokens = len(text.split())
    return estimated_tokens <= max_tokens


def normalize_text(text: str) -> str:
    """
    Normalize text by removing extra whitespace and standardizing formatting.

    Args:
        text: Text to normalize

    Returns:
        Normalized text
    """
    if not text:
        return ""

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Strip leading/trailing whitespace
    text = text.strip()
    return text