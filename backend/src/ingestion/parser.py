"""
HTML content extraction and cleaning module for the Book URL Ingestion Pipeline.
"""

from typing import Any, Dict, List
from bs4 import BeautifulSoup
from bs4.element import Tag
from src.utils.config import Config


class ContentParser:
    """
    Handles HTML content extraction and cleaning for the Book URL Ingestion Pipeline.
    """

    def __init__(self, config: Config):
        self.config = config

    def extract_readable_content(self, html: str, url: str) -> Dict:
        """
        Extract readable content from HTML with metadata.

        Args:
            html: HTML content to extract from
            url: URL of the source page

        Returns:
            Dictionary with extracted content and metadata
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Remove navigation, footer, and boilerplate content
        self._remove_boilerplate(soup)

        # Extract text content
        text = self._extract_text_content(soup)

        # If text extraction failed or returned minimal content, try alternative approach
        if not text or len(text.strip()) < 50:
            # Fallback to getting all text content, but clean it more carefully
            text = self._extract_fallback_content(soup)

        # Extract headings and preserve hierarchy
        headings = self._extract_headings(soup)

        # Extract code blocks
        code_blocks = self._extract_code_blocks(soup)

        # Get page title
        title = self._extract_title(soup)

        # Extract module and section from URL
        module, section = self._extract_module_section_from_url(url)

        return {
            'text': text,
            'title': title,
            'headings': headings,
            'code_blocks': code_blocks,
            'heading_hierarchy': self._build_heading_hierarchy(headings),
            'url': url,
            'module': module,
            'section': section
        }

    def _remove_boilerplate(self, soup: BeautifulSoup) -> None:
        """
        Remove navigation, footer, and other boilerplate content from the soup.

        Args:
            soup: BeautifulSoup object to modify
        """
        # Common selectors for navigation and boilerplate elements
        # Be more careful not to remove content containers
        boilerplate_selectors = [
            'nav', 'aside',  # Navigation and side elements
            '[class*="nav "]', '[class*="nav-"]', '[class*="menu"]', '[class*="sidebar"]',
            '[id*="nav"]', '[id*="menu"]', '[id*="sidebar"]',
            '.advertisement', '.ads', '.cookie-consent',
            '.social-share', '.share-buttons'
        ]

        for selector in boilerplate_selectors:
            elements = soup.select(selector)
            for element in elements:
                element.decompose()

    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """
        Extract main text content from the soup.

        Args:
            soup: BeautifulSoup object

        Returns:
            Extracted text content
        """
        # Remove script and style elements that don't contain meaningful content
        for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
            script.decompose()

        # Look for Docusaurus-specific content containers first
        docusaurus_selectors = [
            '.theme-doc-markdown.markdown',  # Docusaurus markdown content container
            'article .theme-doc-markdown',   # Article with markdown content
            '.theme-doc-markdown',           # Docusaurus markdown class
            'article',                       # Main article content
            '.markdown',                     # Markdown content class
            '.doc-content',                  # Documentation content
            '.docs-content',                 # Documentation content
            '.main-content',                 # Main content area
            '.content'                       # General content area
        ]

        text_parts = []

        # Try to find content in Docusaurus-specific containers first
        content_found = False
        for selector in docusaurus_selectors:
            content_elements = soup.select(selector)
            if content_elements:
                for element in content_elements:
                    # For content containers like markdown and article, we want to extract the content
                    # regardless of boilerplate detection, since these are specifically content areas
                    is_content_container = any(cls in selector for cls in ['.markdown', '.theme-doc-markdown', 'article'])
                    if is_content_container or not self._is_likely_boilerplate(element):
                        text = element.get_text(separator=' ', strip=True)
                        if text and len(text) > 50:  # Require more substantial content
                            text_parts.append(text)
                            content_found = True
                            break  # Use first substantial content found

        # If no specific content containers found, extract from the entire body
        if not content_found:
            # Get the article content specifically if it exists
            article = soup.find('article')
            if article:
                # Remove any remaining boilerplate elements inside article
                for elem in article.find_all(['nav', 'footer', 'header', 'aside']):
                    elem.decompose()
                text = article.get_text(separator=' ', strip=True)
                if text and len(text) > 50:  # Only add if substantial
                    text_parts.append(text)
                    content_found = True

        # If still no content found, try main content area
        if not content_found:
            main_content = soup.find('main')
            if main_content:
                # Remove boilerplate from main content
                for elem in main_content.find_all(['nav', 'footer', 'header', 'aside']):
                    elem.decompose()
                text = main_content.get_text(separator=' ', strip=True)
                if text and len(text) > 50:
                    text_parts.append(text)
                    content_found = True

        # Fallback: get all text if no specific content found
        if not text_parts:
            all_text = soup.get_text(separator=' ', strip=True)
            if all_text and len(all_text) > 50:
                text_parts.append(all_text)

        # Clean up the text by removing extra whitespace
        cleaned_parts = []
        for part in text_parts:
            # Remove extra whitespace and empty strings
            cleaned = ' '.join(part.split())
            if cleaned and len(cleaned) > 20:  # Only keep substantial text
                cleaned_parts.append(cleaned)

        return ' '.join(cleaned_parts) if cleaned_parts else ""

    def _extract_fallback_content(self, soup: BeautifulSoup) -> str:
        """
        Fallback method to extract content when primary method fails.

        Args:
            soup: BeautifulSoup object

        Returns:
            Extracted text content
        """
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Try to get content from the most likely content areas
        # Look for content in the main article or content area
        content_selectors = [
            'article',
            '.theme-doc-markdown',
            '.markdown',
            'main',
            '.main-content',
            '.docs-content',
            '.container'
        ]

        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                content = []
                for elem in elements:
                    # Get text from this element
                    text = elem.get_text(separator=' ', strip=True)
                    if len(text) > 50:  # Substantial content
                        content.append(text)

                if content:
                    full_content = ' '.join(content)
                    # Clean up the content
                    cleaned = ' '.join(full_content.split())
                    if len(cleaned) > 50:
                        return cleaned

        # If specific selectors don't work, try to extract from body
        body = soup.find('body')
        if body:
            # Remove common navigation elements
            for elem in body.find_all(['nav', 'header', 'footer', 'aside']):
                elem.decompose()

            text = body.get_text(separator=' ', strip=True)
            cleaned = ' '.join(text.split())
            if len(cleaned) > 50:
                return cleaned

        # Final fallback: extract all text
        all_text = soup.get_text(separator=' ', strip=True)
        cleaned = ' '.join(all_text.split())
        return cleaned if len(cleaned) > 20 else ""

    def _extract_headings(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """
        Extract all headings from the soup.

        Args:
            soup: BeautifulSoup object

        Returns:
            List of heading dictionaries with level and text
        """
        headings = []
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            headings.append({
                'level': int(heading.name[1]),  # Extract number from h1, h2, etc.
                'text': heading.get_text(strip=True)
            })
        return headings

    def _extract_code_blocks(self, soup: BeautifulSoup) -> List[str]:
        """
        Extract code blocks from the soup.

        Args:
            soup: BeautifulSoup object

        Returns:
            List of code block text
        """
        code_blocks = []

        # Find all pre and code elements
        code_elements = soup.find_all(['pre', 'code'])

        for code_element in code_elements:
            # Get the text content
            code_text = code_element.get_text(strip=True)

            # Only add if it's substantial code content
            if code_text and len(code_text) > 10:  # At least 10 characters
                code_blocks.append(code_text)

        return code_blocks

    def extract_content_with_heading_hierarchy(self, html: str, url: str) -> Dict:
        """
        Enhanced content extraction that preserves heading hierarchy.

        Args:
            html: HTML content to extract from
            url: URL of the source page

        Returns:
            Dictionary with extracted content and preserved heading hierarchy
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Remove navigation, footer, and boilerplate content
        self._remove_boilerplate(soup)

        # Extract text content
        text = self._extract_text_content(soup)

        # Extract headings with proper hierarchy
        headings = self._extract_headings(soup)

        # Extract code blocks
        code_blocks = self._extract_code_blocks(soup)

        # Get page title
        title = self._extract_title(soup)

        # Extract module and section from URL
        module, section = self._extract_module_section_from_url(url)

        # Build heading hierarchy with proper nesting
        heading_hierarchy = self._build_heading_hierarchy_with_nesting(headings)

        return {
            'text': text,
            'title': title,
            'headings': headings,
            'code_blocks': code_blocks,
            'heading_hierarchy': heading_hierarchy,
            'url': url,
            'module': module,
            'section': section
        }

    def _build_heading_hierarchy_with_nesting(self, headings: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Build a proper heading hierarchy with nesting information.

        Args:
            headings: List of heading dictionaries

        Returns:
            List of heading dictionaries with nesting information
        """
        if not headings:
            return []

        # Create a hierarchy structure with parent-child relationships
        hierarchy = []
        stack = []  # Stack to track the current hierarchy path

        for heading in headings:
            current_level = heading['level']
            current_text = heading['text']

            # Pop from stack until we find the right parent level
            while stack and stack[-1]['level'] >= current_level:
                stack.pop()

            # Create the hierarchy entry
            hierarchy_entry = {
                'level': current_level,
                'text': current_text,
                'parent': stack[-1]['text'] if stack else None
            }

            hierarchy.append(hierarchy_entry)
            stack.append(hierarchy_entry)

        return hierarchy

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """
        Extract page title from the soup.

        Args:
            soup: BeautifulSoup object

        Returns:
            Page title or empty string
        """
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text(strip=True)

        # Fallback: look for h1
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)

        return ""

    def _extract_module_section_from_url(self, url: str) -> tuple[str, str]:
        """
        Extract module and section information from the URL.

        Args:
            url: URL to extract from

        Returns:
            Tuple of (module, section)
        """
        from urllib.parse import urlparse
        parsed = urlparse(url)
        path_parts = [part for part in parsed.path.split('/') if part]

        if len(path_parts) >= 2:
            module = path_parts[0] if path_parts[0] else 'main'
            section = path_parts[1] if len(path_parts) > 1 else path_parts[0]
        elif len(path_parts) == 1:
            module = 'main'
            section = path_parts[0]
        else:
            module = 'main'
            section = 'index'

        return module, section

    def _build_heading_hierarchy(self, headings: List[Dict[str, str]]) -> List[str]:
        """
        Build a heading hierarchy from the list of headings.

        Args:
            headings: List of heading dictionaries

        Returns:
            List of heading texts in hierarchical order
        """
        if not headings:
            return []

        # Sort headings by level to maintain hierarchy
        sorted_headings = sorted(headings, key=lambda x: x['level'])
        return [h['text'] for h in sorted_headings]

    def _is_likely_boilerplate(self, element: Tag) -> bool:
        """
        Determine if an element is likely boilerplate content.

        Args:
            element: BeautifulSoup element to check

        Returns:
            True if likely boilerplate, False otherwise
        """
        # Check class and id attributes for common boilerplate patterns
        class_attr = element.get('class', [])
        id_attr = element.get('id', '')

        if isinstance(class_attr, list):
            class_text = ' '.join(class_attr).lower()
        else:
            class_text = str(class_attr).lower()

        boilerplate_patterns = [
            'nav', 'menu', 'sidebar', 'footer', 'header',
            'advertisement', 'ads', 'cookie', 'social', 'share'
        ]

        for pattern in boilerplate_patterns:
            if pattern in class_text or pattern in id_attr.lower():
                return True

        return False


# Example usage and testing
if __name__ == "__main__":
    # This would require actual HTML content to run
    pass