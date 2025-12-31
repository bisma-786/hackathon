"""
Tests for the crawler module in the Book URL Ingestion Pipeline.
"""

import pytest
from unittest.mock import Mock, patch
from src.ingestion.crawler import Crawler
from src.utils.config import Config


class TestCrawler:
    """
    Test class for the Crawler module.
    """

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create a mock config object
        self.mock_config = Mock(spec=Config)
        self.mock_config.request_timeout = 30
        self.crawler = Crawler(self.mock_config)

    def test_discover_book_urls(self):
        """Test the discover_book_urls method."""
        # This is a placeholder test - in a real implementation, we would mock the HTTP requests
        # For now, we'll just test that the method exists and returns a list
        base_url = "https://example.com"

        # Mock the internal methods to avoid making real HTTP requests
        with patch.object(self.crawler, '_crawl_site', return_value=[]):
            with patch.object(self.crawler, '_is_content_url', return_value=True):
                result = self.crawler.discover_book_urls(base_url)

        assert isinstance(result, list)
        # The result should at least include the base URL if it's a content URL
        # (This depends on the implementation of _is_book_page)

    def test_fetch_page_content_success(self):
        """Test fetching page content successfully."""
        test_url = "https://example.com/test"
        test_content = "<html><body>Test content</body></html>"

        # Mock the session.get method
        with patch.object(self.crawler.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.text = test_content
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = self.crawler.fetch_page_content(test_url)

            assert result == test_content
            mock_get.assert_called_once_with(test_url, timeout=self.mock_config.request_timeout)

    def test_fetch_page_content_failure(self):
        """Test fetching page content when request fails."""
        test_url = "https://example.com/test"

        # Mock the session.get method to raise an exception
        with patch.object(self.crawler.session, 'get') as mock_get:
            mock_get.side_effect = Exception("Network error")

            result = self.crawler.fetch_page_content(test_url)

            assert result == ""
            mock_get.assert_called_once_with(test_url, timeout=self.mock_config.request_timeout)

    def test_is_same_domain(self):
        """Test the _is_same_domain method."""
        base_url = "https://example.com/path"
        same_domain_url = "https://example.com/other-path"
        diff_domain_url = "https://other.com/path"

        assert self.crawler._is_same_domain(base_url, same_domain_url) is True
        assert self.crawler._is_same_domain(base_url, diff_domain_url) is False

    def test_is_content_url(self):
        """Test the _is_content_url method."""
        # Valid content URLs
        assert self.crawler._is_content_url("https://example.com/page") is True
        assert self.crawler._is_content_url("https://example.com/page.html") is True
        assert self.crawler._is_content_url("https://example.com/page.htm") is True

        # Non-content URLs
        assert self.crawler._is_content_url("https://example.com/style.css") is False
        assert self.crawler._is_content_url("https://example.com/script.js") is False
        assert self.crawler._is_content_url("https://example.com/image.png") is False
        assert self.crawler._is_content_url("https://example.com/search?q=test") is False
        assert self.crawler._is_content_url("https://example.com/#section") is False


if __name__ == "__main__":
    pytest.main([__file__])