"""
Tests for the parser module in the Book URL Ingestion Pipeline.
"""

import pytest
from unittest.mock import Mock
from src.ingestion.parser import ContentParser
from src.utils.config import Config


class TestContentParser:
    """
    Test class for the ContentParser module.
    """

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create a mock config object
        self.mock_config = Mock(spec=Config)
        self.parser = ContentParser(self.mock_config)

    def test_extract_readable_content(self):
        """Test the extract_readable_content method."""
        html_content = """
        <html>
            <head>
                <title>Test Page</title>
            </head>
            <body>
                <nav>Navigation content</nav>
                <header>Header content</header>
                <main>
                    <h1>Main Title</h1>
                    <p>This is the main content of the page.</p>
                    <p>Here's another paragraph with more content.</p>
                    <pre><code>def example():
    print("Hello, World!")
</code></pre>
                </main>
                <footer>Footer content</footer>
            </body>
        </html>
        """
        url = "https://example.com/test-page"

        result = self.parser.extract_readable_content(html_content, url)

        # Check that the result has the expected keys
        assert 'text' in result
        assert 'title' in result
        assert 'headings' in result
        assert 'code_blocks' in result
        assert 'heading_hierarchy' in result
        assert 'url' in result
        assert 'module' in result
        assert 'section' in result

        # Check that boilerplate content was removed
        assert 'Navigation content' not in result['text']
        assert 'Header content' not in result['text']
        assert 'Footer content' not in result['text']

        # Check that main content was preserved
        assert 'main content of the page' in result['text']
        assert 'another paragraph' in result['text']

        # Check that title was extracted
        assert result['title'] == 'Test Page'

        # Check that headings were extracted
        assert len(result['headings']) > 0
        assert any(h['text'] == 'Main Title' for h in result['headings'])

        # Check that code blocks were extracted
        assert len(result['code_blocks']) > 0
        assert any('def example()' in code for code in result['code_blocks'])

        # Check that URL was preserved
        assert result['url'] == url

    def test_remove_boilerplate(self):
        """Test the _remove_boilerplate method."""
        from bs4 import BeautifulSoup
        html_content = """
        <html>
            <body>
                <nav>Navigation</nav>
                <header>Header</header>
                <aside>Sidebar</aside>
                <main>Main content</main>
                <footer>Footer</footer>
            </body>
        </html>
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # Count elements before removal
        initial_count = len(soup.find_all(['nav', 'header', 'aside', 'footer']))
        assert initial_count > 0

        self.parser._remove_boilerplate(soup)

        # Count elements after removal
        remaining_count = len(soup.find_all(['nav', 'header', 'aside', 'footer']))
        assert remaining_count == 0

        # Main content should still be there
        main_content = soup.find('main')
        assert main_content is not None
        assert main_content.get_text(strip=True) == 'Main content'

    def test_extract_title(self):
        """Test the _extract_title method."""
        from bs4 import BeautifulSoup

        # Test with title tag
        html_with_title = '<html><head><title>Test Title</title></head><body></body></html>'
        soup = BeautifulSoup(html_with_title, 'html.parser')
        title = self.parser._extract_title(soup)
        assert title == 'Test Title'

        # Test with h1 fallback
        html_with_h1 = '<html><body><h1>Main Heading</h1></body></html>'
        soup = BeautifulSoup(html_with_h1, 'html.parser')
        title = self.parser._extract_title(soup)
        assert title == 'Main Heading'

        # Test with no title or h1
        html_no_title = '<html><body>No title here</body></html>'
        soup = BeautifulSoup(html_no_title, 'html.parser')
        title = self.parser._extract_title(soup)
        assert title == ''

    def test_extract_module_section_from_url(self):
        """Test the _extract_module_section_from_url method."""
        # Test with multiple path segments
        url1 = "https://example.com/module1/section1/page"
        module, section = self.parser._extract_module_section_from_url(url1)
        assert module == "module1"
        assert section == "section1"

        # Test with single path segment
        url2 = "https://example.com/intro"
        module, section = self.parser._extract_module_section_from_url(url2)
        assert module == "main"
        assert section == "intro"

        # Test with root URL
        url3 = "https://example.com/"
        module, section = self.parser._extract_module_section_from_url(url3)
        assert module == "main"
        assert section == "index"

    def test_is_likely_boilerplate(self):
        """Test the _is_likely_boilerplate method."""
        from bs4 import BeautifulSoup

        # Test with navigation class
        nav_element = BeautifulSoup('<div class="navigation">content</div>', 'html.parser').div
        assert self.parser._is_likely_boilerplate(nav_element) is True

        # Test with sidebar class
        sidebar_element = BeautifulSoup('<div class="sidebar">content</div>', 'html.parser').div
        assert self.parser._is_likely_boilerplate(sidebar_element) is True

        # Test with main content class
        main_element = BeautifulSoup('<div class="main-content">content</div>', 'html.parser').div
        assert self.parser._is_likely_boilerplate(main_element) is False

        # Test with footer id
        footer_element = BeautifulSoup('<div id="footer">content</div>', 'html.parser').div
        assert self.parser._is_likely_boilerplate(footer_element) is True


if __name__ == "__main__":
    pytest.main([__file__])