"""
Logging utilities for the Book URL Ingestion Pipeline.
"""

import logging
import sys
from typing import Optional


def setup_logging(log_level: str = "INFO") -> None:
    """
    Set up logging configuration for the application.

    Args:
        log_level: Logging level as string (DEBUG, INFO, WARNING, ERROR)
    """
    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.addHandler(console_handler)


def get_ingestion_stats() -> dict:
    """
    Get ingestion statistics (placeholder implementation).

    Returns:
        Dictionary with ingestion statistics
    """
    # This is a placeholder - in a real implementation, this would track
    # actual statistics during the ingestion process
    return {
        "pages": 0,
        "chunks": 0,
        "embeddings": 0,
        "errors": 0,
        "start_time": None,
        "end_time": None
    }


class PipelineLogger:
    """
    A specialized logger for the ingestion pipeline that tracks
    progress and statistics.
    """

    def __init__(self, name: str = "ingestion_pipeline"):
        self.logger = logging.getLogger(name)
        self.stats = {
            "pages_processed": 0,
            "chunks_created": 0,
            "embeddings_generated": 0,
            "vectors_stored": 0,
            "errors": 0
        }

    def increment_pages_processed(self) -> None:
        """Increment the count of processed pages."""
        self.stats["pages_processed"] += 1

    def increment_chunks_created(self) -> None:
        """Increment the count of created chunks."""
        self.stats["chunks_created"] += 1

    def increment_embeddings_generated(self) -> None:
        """Increment the count of generated embeddings."""
        self.stats["embeddings_generated"] += 1

    def increment_vectors_stored(self) -> None:
        """Increment the count of stored vectors."""
        self.stats["vectors_stored"] += 1

    def increment_errors(self) -> None:
        """Increment the count of errors."""
        self.stats["errors"] += 1

    def get_stats(self) -> dict:
        """Get current statistics."""
        return self.stats.copy()

    def log_progress(self, message: str) -> None:
        """Log a progress message."""
        self.logger.info(message)

    def log_error(self, message: str, exc: Optional[Exception] = None) -> None:
        """Log an error message."""
        if exc:
            self.logger.error(f"{message}: {str(exc)}", exc_info=True)
        else:
            self.logger.error(message)