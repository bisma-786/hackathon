"""
BookPage model for the Book URL Ingestion Pipeline.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from src.utils.validators import validate_book_page, is_valid_url


class BookPage:
    """
    Represents a single book page with URL, module, section title, and heading hierarchy.
    """

    def __init__(
        self,
        url: str,
        module: str,
        section_title: str,
        heading_hierarchy: Optional[List[str]] = None,
        content_length: int = 0,
        word_count: int = 0,
        crawl_status: str = "pending",
        last_crawled: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a BookPage instance.

        Args:
            url: Unique URL identifier for the page
            module: Module identifier
            section_title: Main title of the section
            heading_hierarchy: Complete heading hierarchy of the page (optional)
            content_length: Total character count of page content (optional, default: 0)
            word_count: Total word count of page content (optional, default: 0)
            crawl_status: Status of crawling (pending, success, failed, retry) (default: pending)
            last_crawled: Timestamp of last crawl attempt (optional)
            metadata: Additional metadata from HTML (optional)
        """
        if not is_valid_url(url):
            raise ValueError(f"Invalid URL: {url}")

        if not module or not isinstance(module, str):
            raise ValueError("Module must be a non-empty string")

        if not section_title or not isinstance(section_title, str):
            raise ValueError("Section title must be a non-empty string")

        valid_statuses = ['pending', 'crawling', 'success', 'error', 'retry']
        if crawl_status not in valid_statuses:
            raise ValueError(f"Crawl status must be one of {valid_statuses}")

        self.url = url
        self.module = module
        self.section_title = section_title
        self.heading_hierarchy = heading_hierarchy or []
        self.content_length = content_length
        self.word_count = word_count
        self.crawl_status = crawl_status
        self.last_crawled = last_crawled
        self.metadata = metadata or {}

    def validate(self) -> List[str]:
        """
        Validate the book page according to the data model requirements.

        Returns:
            List of validation errors (empty if valid)
        """
        page_dict = self.to_dict()
        return validate_book_page(page_dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the BookPage instance to a dictionary.

        Returns:
            Dictionary representation of the BookPage
        """
        return {
            'url': self.url,
            'module': self.module,
            'section_title': self.section_title,
            'heading_hierarchy': self.heading_hierarchy,
            'content_length': self.content_length,
            'word_count': self.word_count,
            'crawl_status': self.crawl_status,
            'last_crawled': self.last_crawled.isoformat() if self.last_crawled else None,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BookPage':
        """
        Create a BookPage instance from a dictionary.

        Args:
            data: Dictionary representation of a BookPage

        Returns:
            BookPage instance
        """
        return cls(
            url=data['url'],
            module=data['module'],
            section_title=data['section_title'],
            heading_hierarchy=data.get('heading_hierarchy', []),
            content_length=data.get('content_length', 0),
            word_count=data.get('word_count', 0),
            crawl_status=data.get('crawl_status', 'pending'),
            last_crawled=datetime.fromisoformat(data['last_crawled']) if data.get('last_crawled') else None,
            metadata=data.get('metadata', {})
        )

    def update_status(self, status: str, timestamp: Optional[datetime] = None) -> None:
        """
        Update the crawl status of the book page.

        Args:
            status: New status (pending, crawling, success, error, retry)
            timestamp: Timestamp for the status update (optional, defaults to now)
        """
        valid_statuses = ['pending', 'crawling', 'success', 'error', 'retry']
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")

        self.crawl_status = status
        self.last_crawled = timestamp or datetime.utcnow()

    def update_content_stats(self, content_length: int, word_count: int) -> None:
        """
        Update content statistics for the book page.

        Args:
            content_length: New content length
            word_count: New word count
        """
        self.content_length = content_length
        self.word_count = word_count

    def __repr__(self) -> str:
        """
        String representation of the BookPage.
        """
        return f"BookPage(url={self.url}, module={self.module}, section={self.section_title}, status={self.crawl_status})"

    def __eq__(self, other) -> bool:
        """
        Check equality based on URL.
        """
        if not isinstance(other, BookPage):
            return False
        return self.url == other.url

    def __hash__(self) -> int:
        """
        Hash based on URL.
        """
        return hash(self.url)