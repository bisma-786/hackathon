"""
URL discovery and fetching module for the Book URL Ingestion Pipeline.
"""

import requests
from typing import List, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from src.utils.config import Config
from src.models.book_page import BookPage
from src.ingestion.sitemap_parser import SitemapParser


class Crawler:
    """
    Handles URL discovery and fetching for the Book URL Ingestion Pipeline.
    """

    def __init__(self, config: Config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BookURLIngestionBot/1.0'
        })

    def discover_book_urls(self, base_url: str) -> List[str]:
        """
        Discover all book page URLs from the base URL using both sitemap and crawling.

        Args:
            base_url: Base URL of the book site

        Returns:
            List of discovered URLs
        """
        urls = set()

        # First, try to get URLs from sitemap.xml
        sitemap_parser = SitemapParser(self.config)
        sitemap_urls = sitemap_parser.get_urls_from_sitemap(base_url)
        urls.update(sitemap_urls)
        print(f"Discovered {len(sitemap_urls)} URLs from sitemap.xml")

        # Then, add the base URL itself if it's a valid book page
        if self._is_book_page(base_url):
            urls.add(base_url)

        # Finally, discover additional URLs by crawling the site
        crawled_urls = self._crawl_site(base_url)
        urls.update(crawled_urls)
        print(f"Discovered {len(crawled_urls)} URLs through crawling")

        # Filter out non-content URLs (assets, search, etc.)
        filtered_urls = []
        for url in urls:
            if self._is_content_url(url):
                filtered_urls.append(url)

        print(f"Total unique URLs after filtering: {len(filtered_urls)}")
        return filtered_urls

    def _crawl_site(self, base_url: str) -> List[str]:
        """
        Crawl the site to discover all book page URLs.

        Args:
            base_url: Base URL of the book site

        Returns:
            List of discovered URLs
        """
        discovered_urls = set()
        to_visit = [base_url]
        visited = set()

        while to_visit:
            current_url = to_visit.pop(0)

            if current_url in visited:
                continue

            visited.add(current_url)

            try:
                # Fetch the page content
                response = self.session.get(
                    current_url,
                    timeout=self.config.request_timeout
                )

                if response.status_code != 200:
                    continue

                # Parse the HTML to find links
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find all links in the page
                for link in soup.find_all('a', href=True):
                    href = link['href']

                    # Convert relative URLs to absolute
                    absolute_url = urljoin(current_url, href)

                    # Check if it's within the same domain
                    if self._is_same_domain(base_url, absolute_url):
                        if absolute_url not in visited and absolute_url not in to_visit:
                            to_visit.append(absolute_url)
                            discovered_urls.add(absolute_url)

            except Exception as e:
                print(f"Error crawling {current_url}: {str(e)}")
                continue

        return list(discovered_urls)

    def _is_same_domain(self, base_url: str, url: str) -> bool:
        """
        Check if the URL is within the same domain as the base URL.

        Args:
            base_url: Base URL for comparison
            url: URL to check

        Returns:
            True if URLs are in the same domain, False otherwise
        """
        base_domain = urlparse(base_url).netloc
        url_domain = urlparse(url).netloc
        return base_domain == url_domain

    def _is_content_url(self, url: str) -> bool:
        """
        Check if the URL is a content URL (not an asset, search, etc.).

        Args:
            url: URL to check

        Returns:
            True if it's a content URL, False otherwise
        """
        # List of patterns that indicate non-content URLs
        non_content_patterns = [
            '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
            '.pdf', '.zip', '.tar', '.gz', '.exe', '.dmg',
            '/search', '?q=', '&q=', 'search=', 'query=',
            '/assets/', '/static/', '/images/', '/img/',
            '/api/', '/admin/', '/login/', '/logout/',
            '/register/', '/signup/', '/download/',
            '#', 'mailto:', 'tel:'
        ]

        url_lower = url.lower()

        for pattern in non_content_patterns:
            if pattern in url_lower:
                return False

        # Check if it's a valid page (has .html extension or no extension)
        path = urlparse(url).path
        if path.endswith(('.html', '.htm')):
            return True

        # If no extension, assume it's a page
        if '.' not in path.split('/')[-1]:
            return True

        return False

    def _is_book_page(self, url: str) -> bool:
        """
        Check if the URL is likely a book page.

        Args:
            url: URL to check

        Returns:
            True if it's likely a book page, False otherwise
        """
        # For now, just check if it's a content URL
        return self._is_content_url(url)

    def fetch_page_content(self, url: str) -> str:
        """
        Fetch and return the HTML content of a single page.

        Args:
            url: URL of the page to fetch

        Returns:
            HTML content as string
        """
        try:
            response = self.session.get(
                url,
                timeout=self.config.request_timeout
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {str(e)}")
            return ""


# Example usage and testing
if __name__ == "__main__":
    # This would require actual configuration to run
    pass