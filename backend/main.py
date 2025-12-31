#!/usr/bin/env python3
"""
Book URL Ingestion & Vector Indexing Pipeline

This script implements a pipeline that discovers book URLs, extracts content,
chunks text with overlap, generates Cohere embeddings, and stores vectors
with metadata in Qdrant Cloud. The pipeline is designed to be re-runnable
and idempotent, supporting ≥10,000 content chunks with 100% metadata accuracy.
"""

import argparse
import logging
import sys
from typing import Optional

from src.ingestion.crawler import Crawler
from src.ingestion.parser import ContentParser
from src.ingestion.chunker import TextChunker
from src.embedding.generator import EmbeddingGenerator
from src.storage.vector_store import VectorStore
from src.utils.config import Config
from src.utils.logger import setup_logging


def main(
    base_url: Optional[str] = None,
    collection_name: str = "book_content_chunks",
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    rebuild: bool = False,
    batch_size: int = 10,
    log_level: str = "INFO"
) -> bool:
    """
    Main entry point for the ingestion pipeline.

    Args:
        base_url: Base URL of the book site (optional, defaults to env var)
        collection_name: Qdrant collection name (optional, defaults to env var)
        chunk_size: Size of text chunks in tokens (default: 1000)
        chunk_overlap: Overlap between chunks in tokens (default: 200)
        rebuild: Whether to rebuild the entire index (default: False)
        batch_size: Size of batches for embedding generation (default: 10)
        log_level: Logging level (default: "INFO")

    Returns:
        True if pipeline completed successfully, False otherwise
    """
    # Setup logging
    setup_logging(log_level)
    logger = logging.getLogger(__name__)
    logger.info("Starting Book URL Ingestion Pipeline")

    try:
        # Load configuration
        config = Config()
        if base_url:
            config.book_base_url = base_url
        if collection_name:
            config.qdrant_collection_name = collection_name

        # Initialize components
        crawler = Crawler(config)
        parser = ContentParser(config)
        chunker = TextChunker(config)
        embedding_gen = EmbeddingGenerator(config)
        vector_store = VectorStore(config)

        # Phase 1: URL Discovery
        logger.info("Starting URL discovery...")
        urls = crawler.discover_book_urls(config.book_base_url)
        logger.info(f"Discovered {len(urls)} URLs")

        # Phase 2: Content Extraction and Processing
        logger.info("Starting content extraction and processing...")
        all_chunks = []
        for i, url in enumerate(urls):
            logger.info(f"Processing {i+1}/{len(urls)}: {url}")

            # Fetch and parse content
            html_content = crawler.fetch_page_content(url)
            parsed_content = parser.extract_readable_content(html_content, url)

            # Chunk the content
            chunks = chunker.chunk_text_with_overlap(
                parsed_content['text'],
                chunk_size,
                chunk_overlap
            )

            # Add metadata to chunks
            for chunk in chunks:
                chunk['url'] = url
                chunk['module'] = parsed_content.get('module', 'unknown')
                chunk['section'] = parsed_content.get('section', 'unknown')
                chunk['heading_hierarchy'] = parsed_content.get('heading_hierarchy', [])

            all_chunks.extend(chunks)

        logger.info(f"Created {len(all_chunks)} content chunks")

        # Phase 3: Embedding Generation
        logger.info("Starting embedding generation...")
        texts = [chunk['text'] for chunk in all_chunks]
        embeddings = embedding_gen.generate_embeddings(texts, batch_size=batch_size)

        # Attach embeddings to chunks
        for chunk, embedding in zip(all_chunks, embeddings):
            chunk['embedding'] = embedding

        # Phase 4: Vector Storage
        logger.info("Starting vector storage...")
        stored_count = vector_store.upsert_chunks(all_chunks, rebuild=rebuild)
        logger.info(f"Successfully stored {stored_count} vectors in Qdrant")

        logger.info("Book URL Ingestion Pipeline completed successfully")
        return True

    except Exception as e:
        logger.error(f"Pipeline failed with error: {str(e)}", exc_info=True)
        return False


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Book URL Ingestion & Vector Indexing Pipeline"
    )
    parser.add_argument(
        "--base-url",
        type=str,
        help="Base URL of the book site (overrides .env setting)"
    )
    parser.add_argument(
        "--collection",
        type=str,
        default="book_content_chunks",
        help="Qdrant collection name (default: book_content_chunks)"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="Size of text chunks in tokens (default: 1000)"
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=200,
        help="Overlap between chunks in tokens (default: 200)"
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Rebuild the entire index (default: False)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Size of batches for embedding generation (default: 10)"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)"
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    success = main(
        base_url=args.base_url,
        collection_name=args.collection,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        rebuild=args.rebuild,
        batch_size=args.batch_size,
        log_level=args.log_level
    )
    sys.exit(0 if success else 1)