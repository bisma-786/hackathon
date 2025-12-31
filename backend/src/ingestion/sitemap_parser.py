"""
Sitemap parser module for the Book URL Ingestion Pipeline.
"""

import requests
from typing import List
from xml.etree import ElementTree as ET
from urllib.parse import urljoin
from src.utils.config import Config


class SitemapParser:
    """
    Handles parsing of sitemap.xml files to discover URLs for the Book URL Ingestion Pipeline.
    """

    def __init__(self, config: Config):
        self.config = config

    def parse_sitemap(self, base_url: str) -> List[str]:
        """
        Parse the sitemap.xml file to extract URLs.

        Args:
            base_url: Base URL of the site (used to construct sitemap URL)

        Returns:
            List of URLs extracted from the sitemap
        """
        # Construct sitemap URL
        sitemap_url = urljoin(base_url, 'sitemap.xml')

        try:
            response = requests.get(sitemap_url, timeout=self.config.request_timeout)
            response.raise_for_status()

            # Parse the XML content
            root = ET.fromstring(response.content)

            # Handle different namespaces
            namespaces = {
                'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9',
                '': 'http://www.sitemaps.org/schemas/sitemap/0.9'
            }

            urls = []
            # Look for <url><loc> elements
            for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                loc_elem = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc_elem is not None and loc_elem.text:
                    urls.append(loc_elem.text.strip())

            # If namespace didn't work, try without namespace
            if not urls:
                for url_elem in root.findall('.//url'):
                    loc_elem = url_elem.find('loc')
                    if loc_elem is not None and loc_elem.text:
                        urls.append(loc_elem.text.strip())

            # Filter URLs that belong to the same domain
            filtered_urls = []
            for url in urls:
                if self._is_same_domain(base_url, url):
                    filtered_urls.append(url)

            return filtered_urls

        except Exception as e:
            print(f"Error parsing sitemap {sitemap_url}: {str(e)}")
            return []

    def _is_same_domain(self, base_url: str, url: str) -> bool:
        """
        Check if the URL is within the same domain as the base URL.

        Args:
            base_url: Base URL for comparison
            url: URL to check

        Returns:
            True if URLs are in the same domain, False otherwise
        """
        from urllib.parse import urlparse

        base_domain = urlparse(base_url).netloc
        url_domain = urlparse(url).netloc
        return base_domain == url_domain

    def get_urls_from_sitemap(self, base_url: str) -> List[str]:
        """
        Get all URLs from the sitemap.xml file.

        Args:
            base_url: Base URL of the site

        Returns:
            List of URLs from the sitemap
        """
        return self.parse_sitemap(base_url)