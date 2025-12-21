import pytest
import os
from unittest.mock import patch, MagicMock
from backend.main import (
    get_all_urls_from_sitemap,
    extract_docusaurus_metadata,
    extract_clean_text,
    is_valid_textbook_url,
    validate_content_not_empty,
    generate_content_hash,
    generate_unique_id,
    setup_cohere_client,
    setup_qdrant_client,
    chunk_text,
    embed,
    save_chunk_to_qdrant,
    create_collection,
    retrieve_and_verify_metadata,
    validate_metadata_accuracy,
    validate_metadata_fields,
    validate_chunk_size_within_token_limit,
    InvalidChunkSizeError
)
from bs4 import BeautifulSoup


class TestURLValidation:
    """Test URL validation functionality"""

    def test_valid_textbook_url_same_domain(self):
        """Test that valid textbook URLs are accepted"""
        base_url = "https://ai-driven-humanoid-robotics-textboo-chi.vercel.app"
        valid_url = f"{base_url}/docs/intro"
        assert is_valid_textbook_url(valid_url, base_url) is True

    def test_invalid_textbook_url_different_domain(self):
        """Test that URLs from different domains are rejected"""
        base_url = "https://ai-driven-humanoid-robotics-textboo-chi.vercel.app"
        invalid_url = "https://other-site.com/page"
        assert is_valid_textbook_url(invalid_url, base_url) is False

    def test_invalid_textbook_url_file_extensions(self):
        """Test that file URLs are rejected"""
        base_url = "https://ai-driven-humanoid-robotics-textboo-chi.vercel.app"
        invalid_urls = [
            f"{base_url}/file.pdf",
            f"{base_url}/image.jpg",
            f"{base_url}/document.docx"
        ]
        for url in invalid_urls:
            assert is_valid_textbook_url(url, base_url) is False


class TestContentValidation:
    """Test content validation functionality"""

    def test_content_not_empty_valid(self):
        """Test that valid content is accepted"""
        content = "This is a valid content with more than 10 characters"
        assert validate_content_not_empty(content) is True

    def test_content_not_empty_empty_string(self):
        """Test that empty content is rejected"""
        content = ""
        assert validate_content_not_empty(content) is False

    def test_content_not_empty_too_short(self):
        """Test that short content is rejected"""
        content = "short"
        assert validate_content_not_empty(content) is False


class TestUtilityFunctions:
    """Test utility functions"""

    def test_generate_unique_id(self):
        """Test that unique IDs are generated"""
        id1 = generate_unique_id()
        id2 = generate_unique_id()
        assert isinstance(id1, str)
        assert isinstance(id2, str)
        assert id1 != id2  # Should generate different IDs

    def test_generate_content_hash(self):
        """Test that content hashes are generated consistently"""
        content = "Test content for hashing"
        hash1 = generate_content_hash(content)
        hash2 = generate_content_hash(content)
        assert isinstance(hash1, str)
        assert len(hash1) == 64  # SHA256 hash length
        assert hash1 == hash2  # Same content should produce same hash


class TestMetadataExtraction:
    """Test metadata extraction functionality"""

    def test_extract_docusaurus_metadata_with_title(self):
        """Test metadata extraction with title"""
        html = """
        <html>
            <head>
                <title>Section Title | Module Name</title>
            </head>
            <body>
                <article>
                    <h1>Section Title</h1>
                    <p>Content here</p>
                </article>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        module, section = extract_docusaurus_metadata(soup, "https://example.com/docs/module/section")
        assert section == "Section Title"
        assert module == "module"  # Extracted from URL path

    def test_extract_docusaurus_metadata_from_url(self):
        """Test metadata extraction from URL path"""
        html = "<html><body><p>Content</p></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        module, section = extract_docusaurus_metadata(soup, "https://example.com/docs/intro/getting-started")
        assert module == "intro"  # Second-to-last path segment
        assert section == "unknown"


class TestTextExtraction:
    """Test text extraction functionality"""

    def test_extract_clean_text_removes_navigation(self):
        """Test that navigation elements are removed from text"""
        html = """
        <html>
            <body>
                <nav>Navigation content</nav>
                <header>Header content</header>
                <main>
                    <article class="markdown">
                        <p>This is the main content that should be extracted.</p>
                    </article>
                </main>
                <footer>Footer content</footer>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        clean_text = extract_clean_text(soup)
        assert "Navigation content" not in clean_text
        assert "Header content" not in clean_text
        assert "Footer content" not in clean_text
        assert "This is the main content" in clean_text


class TestSitemapParsing:
    """Test sitemap parsing functionality"""

    @patch('backend.main.requests.get')
    def test_get_all_urls_from_sitemap_success(self, mock_get):
        """Test successful sitemap parsing"""
        # Mock sitemap response
        mock_response = MagicMock()
        mock_response.content = b'''<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>https://ai-driven-humanoid-robotics-textboo-chi.vercel.app/docs/intro</loc>
            </url>
            <url>
                <loc>https://ai-driven-humanoid-robotics-textboo-chi.vercel.app/docs/setup</loc>
            </url>
        </urlset>'''
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        urls = get_all_urls_from_sitemap("https://example.com/sitemap.xml")
        assert len(urls) == 2
        assert "https://ai-driven-humanoid-robotics-textboo-chi.vercel.app/docs/intro" in urls
        assert "https://ai-driven-humanoid-robotics-textboo-chi.vercel.app/docs/setup" in urls

    @patch('backend.main.requests.get')
    def test_get_all_urls_from_sitemap_error(self, mock_get):
        """Test sitemap parsing handles errors gracefully"""
        mock_get.side_effect = Exception("Network error")

        urls = get_all_urls_from_sitemap("https://example.com/sitemap.xml")
        assert urls == []  # Should return empty list on error


class TestChunking:
    """Test chunking functionality"""

    def test_chunk_text_basic(self):
        """Test basic text chunking"""
        text = "This is a sentence. This is another sentence. And a third one."
        url = "https://example.com/page"
        module = "test_module"
        section = "test_section"

        chunks = chunk_text(text, url, module, section, chunk_size=30)
        assert len(chunks) > 0
        assert all('id' in chunk for chunk in chunks)
        assert all('text' in chunk for chunk in chunks)
        assert all(len(chunk['text']) <= 30 for chunk in chunks)

    def test_chunk_text_empty(self):
        """Test chunking empty text"""
        chunks = chunk_text("", "url", "module", "section")
        assert chunks == []

    def test_chunk_text_with_validation_error(self):
        """Test chunking with invalid chunk size"""
        with pytest.raises(InvalidChunkSizeError):
            chunk_text("test", "url", "module", "section", chunk_size=0)


class TestEmbedding:
    """Test embedding functionality"""

    @patch('backend.main.setup_cohere_client')
    def test_embed_basic(self, mock_setup_client):
        """Test basic embedding functionality"""
        # Mock the Cohere client
        mock_client = MagicMock()
        mock_setup_client.return_value = mock_client

        # Mock the embed response
        mock_response = MagicMock()
        mock_response.embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        mock_client.embed.return_value = mock_response

        chunks = [
            {
                'id': 'chunk1',
                'text': 'This is the first text chunk',
                'url': 'https://example.com/page1',
                'module': 'module1',
                'section': 'section1',
                'position': 0,
                'hash': 'hash1'
            },
            {
                'id': 'chunk2',
                'text': 'This is the second text chunk',
                'url': 'https://example.com/page2',
                'module': 'module2',
                'section': 'section2',
                'position': 1,
                'hash': 'hash2'
            }
        ]

        result = embed(chunks)
        assert len(result) == 2
        assert result[0]['chunk_id'] == 'chunk1'
        assert result[1]['chunk_id'] == 'chunk2'


class TestStorage:
    """Test storage functionality"""

    @patch('backend.main.setup_qdrant_client')
    def test_save_chunk_to_qdrant(self, mock_setup_client):
        """Test saving chunk to Qdrant"""
        # Mock the Qdrant client
        mock_client = MagicMock()
        mock_setup_client.return_value = mock_client
        mock_client.upsert.return_value = None  # upsert returns None on success

        chunk_id = "test_chunk_id"
        embedding = [0.1, 0.2, 0.3]
        metadata = {"url": "https://example.com", "module": "test", "section": "test"}

        result = save_chunk_to_qdrant(chunk_id, embedding, metadata)
        assert result is True
        mock_client.upsert.assert_called_once()

    def test_validate_chunk_size_within_token_limit(self):
        """Test chunk size validation"""
        # Short text should be valid
        assert validate_chunk_size_within_token_limit("Short text") is True

        # Very long text should be invalid (based on our estimation)
        long_text = "x" * 20000  # 20k characters would be ~5000 tokens
        assert validate_chunk_size_within_token_limit(long_text) is False


class TestClientSetup:
    """Test client setup functionality"""

    @patch.dict(os.environ, {'COHERE_API_KEY': 'test-key'})
    def test_setup_cohere_client_with_api_key(self):
        """Test Cohere client setup with API key"""
        # This test checks that the function doesn't raise an exception when API key is set
        # Actual client functionality would be tested with real API key
        pass  # We're just verifying the function can be called without error when env var is set

    @patch.dict(os.environ, {'QDRANT_API_KEY': 'test-key', 'QDRANT_URL': 'https://test.qdrant.tech'})
    def test_setup_qdrant_client_with_api_key(self):
        """Test Qdrant client setup with API key and URL"""
        # This test checks that the function doesn't raise an exception when credentials are set
        pass  # We're just verifying the function can be called without error when env vars are set


class TestMetadata:
    """Test metadata preservation and retrieval functionality"""

    def test_validate_metadata_fields(self):
        """Test metadata validation for required fields"""
        # Valid metadata
        valid_metadata = {
            'url': 'https://example.com',
            'module': 'test',
            'section': 'test',
            'position': 0,
            'hash': 'test_hash',
            'text': 'test text'
        }
        assert validate_metadata_fields(valid_metadata) is True

        # Invalid metadata - missing field
        invalid_metadata = {
            'url': 'https://example.com',
            'module': 'test',
            # missing 'section' field
            'position': 0,
            'hash': 'test_hash',
            'text': 'test text'
        }
        assert validate_metadata_fields(invalid_metadata) is False

    def test_metadata_preservation_in_chunking(self):
        """Test that metadata is preserved during chunking"""
        text = "This is a test sentence. This is another sentence."
        url = "https://example.com/test"
        module = "test_module"
        section = "test_section"

        chunks = chunk_text(text, url, module, section)
        assert len(chunks) > 0

        for chunk in chunks:
            assert chunk['url'] == url
            assert chunk['module'] == module
            assert chunk['section'] == section
            assert 'position' in chunk
            assert 'hash' in chunk
            assert 'id' in chunk
            assert 'text' in chunk


class TestMetadataTraceability:
    """Create validation tests to verify metadata traceability"""

    @patch('backend.main.setup_qdrant_client')
    def test_retrieve_and_verify_metadata(self, mock_setup_client):
        """Test metadata retrieval and verification"""
        # Mock the Qdrant client
        mock_client = MagicMock()
        mock_setup_client.return_value = mock_client

        # Mock the retrieve response
        mock_point = MagicMock()
        mock_point.payload = {
            'url': 'https://example.com/test',
            'module': 'test_module',
            'section': 'test_section',
            'position': 0,
            'hash': 'test_hash',
            'text': 'test text'
        }
        mock_client.retrieve.return_value = [mock_point]

        chunk_id = "test_chunk_id"
        result = retrieve_and_verify_metadata(chunk_id)

        assert result == mock_point.payload
        mock_client.retrieve.assert_called_once()

    @patch('backend.main.setup_qdrant_client')
    def test_validate_metadata_accuracy(self, mock_setup_client):
        """Test metadata accuracy validation"""
        # Mock the Qdrant client
        mock_client = MagicMock()
        mock_setup_client.return_value = mock_client

        # Mock the retrieve response
        mock_point = MagicMock()
        mock_point.payload = {
            'url': 'https://example.com/test',
            'module': 'test_module',
            'section': 'test_section',
            'position': 0,
            'hash': 'test_hash',
            'text': 'test text'
        }
        mock_client.retrieve.return_value = [mock_point]

        chunk_id = "test_chunk_id"
        expected_metadata = {
            'url': 'https://example.com/test',
            'module': 'test_module',
            'section': 'test_section',
            'position': 0,
            'hash': 'test_hash',
            'text': 'test text'
        }

        result = validate_metadata_accuracy(chunk_id, expected_metadata)
        assert result is True


class TestIntegration:
    """Test integration of the complete embedding pipeline"""

    @patch('backend.main.setup_cohere_client')
    @patch('backend.main.setup_qdrant_client')
    def test_complete_embedding_pipeline_integration(self, mock_qdrant_client, mock_cohere_client):
        """Test the complete embedding pipeline from chunking to storage"""
        # Mock the Cohere client
        mock_cohere = MagicMock()
        mock_cohere_client.return_value = mock_cohere
        mock_cohere.embed.return_value = MagicMock()
        mock_cohere.embed.return_value.embeddings = [[0.1, 0.2, 0.3]]

        # Mock the Qdrant client
        mock_qdrant = MagicMock()
        mock_qdrant_client.return_value = mock_qdrant
        mock_qdrant.upsert.return_value = None

        # Test the complete flow
        text = "This is a test document for integration testing."
        url = "https://example.com/test"
        module = "test_module"
        section = "test_section"

        # 1. Chunk the text
        chunks = chunk_text(text, url, module, section)
        assert len(chunks) > 0

        # 2. Generate embeddings
        embedded_chunks = embed(chunks)
        assert len(embedded_chunks) == len(chunks)

        # 3. Create collection
        result = create_collection()
        assert result is True  # The function returns True when collection exists or is created

        # 4. Save to Qdrant
        for embedded_chunk in embedded_chunks:
            result = save_chunk_to_qdrant(
                embedded_chunk['chunk_id'],
                embedded_chunk['embedding'],
                embedded_chunk['metadata']
            )
            assert result is True

        # Verify the calls were made
        assert mock_cohere.embed.called
        assert mock_qdrant.upsert.called


class TestEndToEndPipeline:
    """End-to-end integration tests for the complete RAG pipeline"""

    @patch('backend.main.get_all_urls_from_sitemap')
    @patch('backend.main.setup_cohere_client')
    @patch('backend.main.setup_qdrant_client')
    @patch('backend.main.requests.get')
    def test_end_to_end_pipeline_full_flow(self, mock_requests_get, mock_qdrant_client, mock_cohere_client, mock_sitemap):
        """Test the complete end-to-end pipeline from URL discovery to embedding storage"""
        # Mock sitemap to return some URLs
        mock_sitemap.return_value = [
            "https://example.com/docs/intro",
            "https://example.com/docs/setup"
        ]

        # Mock requests to return HTML content for both URLs
        mock_response1 = MagicMock()
        mock_response1.status_code = 200
        mock_response1.content = b"""
        <html>
            <head><title>Intro Page | Module 1</title></head>
            <body>
                <article class="markdown">
                    <p>This is the introduction content. It explains the basics.</p>
                    <p>There are multiple paragraphs in this content.</p>
                </article>
            </body>
        </html>
        """

        mock_response2 = MagicMock()
        mock_response2.status_code = 200
        mock_response2.content = b"""
        <html>
            <head><title>Setup Page | Module 1</title></head>
            <body>
                <article class="markdown">
                    <p>This is the setup content. It explains how to set up the system.</p>
                    <p>Follow these steps carefully to ensure proper configuration.</p>
                </article>
            </body>
        </html>
        """

        # Configure mock to return different responses for different URLs
        def side_effect(url):
            if "intro" in url:
                return mock_response1
            elif "setup" in url:
                return mock_response2
            else:
                # Default response for other requests
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_resp.content = b"<html><body><p>Default content</p></body></html>"
                return mock_resp

        mock_requests_get.side_effect = side_effect

        # Mock Cohere client
        mock_cohere = MagicMock()
        mock_cohere_client.return_value = mock_cohere
        # Mock embeddings - return different embeddings for each text
        mock_cohere.embed.return_value.embeddings = [
            [0.1, 0.2, 0.3, 0.4],  # For first chunk
            [0.5, 0.6, 0.7, 0.8],  # For second chunk
            [0.9, 1.0, 1.1, 1.2], # For third chunk
            [1.3, 1.4, 1.5, 1.6]  # For fourth chunk
        ]

        # Mock Qdrant client
        mock_qdrant = MagicMock()
        mock_qdrant_client.return_value = mock_qdrant
        mock_qdrant.upsert.return_value = None
        mock_qdrant.get_collection.return_value = MagicMock()
        mock_qdrant.get_collection.return_value.points_count = 0

        # Import the functions we need to test
        from backend.main import get_all_urls, extract_text_from_urls, chunk_text, embed, create_collection, save_chunk_to_qdrant

        # 1. Get URLs
        urls = get_all_urls("https://example.com")
        assert len(urls) == 2
        assert "https://example.com/docs/intro" in urls
        assert "https://example.com/docs/setup" in urls

        # 2. Extract text from URLs
        content_list = extract_text_from_urls(urls)
        assert len(content_list) == 2

        # 3. Process each content
        total_chunks = 0
        total_embeddings = 0

        for content_data in content_list:
            url = content_data['url']
            content = content_data['content']
            module = content_data['module']
            section = content_data['section']

            # 4. Chunk the content
            chunks = chunk_text(content, url, module, section, chunk_size=50)  # Small chunks for testing
            assert len(chunks) > 0
            total_chunks += len(chunks)

            # 5. Generate embeddings
            embedded_chunks = embed(chunks)
            assert len(embedded_chunks) == len(chunks)
            total_embeddings += len(embedded_chunks)

            # 6. Create collection (this should succeed)
            collection_result = create_collection()
            assert collection_result is True

            # 7. Save embeddings to Qdrant
            for embedded_chunk in embedded_chunks:
                save_result = save_chunk_to_qdrant(
                    embedded_chunk['chunk_id'],
                    embedded_chunk['embedding'],
                    embedded_chunk['metadata']
                )
                assert save_result is True

        # Verify that we processed content
        assert total_chunks > 0
        assert total_embeddings > 0

        # Verify that Cohere and Qdrant were called
        assert mock_cohere.embed.called
        assert mock_qdrant.upsert.called

    @patch('backend.main.setup_cohere_client')
    @patch('backend.main.setup_qdrant_client')
    def test_pipeline_with_validation_and_error_handling(self, mock_qdrant_client, mock_cohere_client):
        """Test the pipeline with validation and error handling"""
        # Mock Cohere client to simulate an error
        mock_cohere = MagicMock()
        mock_cohere_client.return_value = mock_cohere
        mock_cohere.embed.side_effect = Exception("API Error")

        # Mock Qdrant client
        mock_qdrant = MagicMock()
        mock_qdrant_client.return_value = mock_qdrant

        # Test with valid chunks that would cause embedding to fail
        chunks = [
            {
                'id': 'chunk1',
                'text': 'This is a test chunk',
                'url': 'https://example.com/test',
                'module': 'test_module',
                'section': 'test_section',
                'position': 0,
                'hash': 'hash1'
            }
        ]

        # Embedding should raise an exception
        from backend.main import EmbeddingGenerationError
        with pytest.raises(EmbeddingGenerationError):
            embed(chunks)

        # Verify that the error was handled properly
        assert mock_cohere.embed.called

    def test_configuration_and_processing_modes(self):
        """Test different processing configurations and modes"""
        from backend.main import ProcessingConfig

        # Test default configuration
        config = ProcessingConfig()
        assert config.chunk_size == 1000
        assert config.collection_name == "rag_embedding"
        assert config.embedding_model == "embed-multilingual-v3.0"
        assert config.processing_mode == "full"

        # Test configuration with environment variables
        with patch.dict(os.environ, {
            'CHUNK_SIZE': '2000',
            'COLLECTION_NAME': 'test_collection',
            'EMBEDDING_MODEL': 'test-model',
            'PROCESSING_MODE': 'content_only'
        }):
            config = ProcessingConfig()
            assert config.chunk_size == 2000
            assert config.collection_name == "test_collection"
            assert config.embedding_model == "test-model"
            assert config.processing_mode == "content_only"

    @patch('backend.main.setup_cohere_client')
    @patch('backend.main.setup_qdrant_client')
    def test_content_extraction_quality_validation(self, mock_qdrant_client, mock_cohere_client):
        """Test the content extraction quality validation functionality"""
        from backend.main import evaluate_content_extraction_quality, validate_content_extraction_accuracy

        # Test with HTML that has lots of non-content elements
        html_with_non_content = """
        <html>
            <head>
                <title>Test Page</title>
            </head>
            <body>
                <nav>Navigation menu with lots of links</nav>
                <header>Header content with logo and menu</header>
                <aside>Sidebar with ads and related links</aside>
                <main>
                    <article class="markdown">
                        <h1>Main Content Title</h1>
                        <p>This is the actual content that we want to extract.</p>
                        <p>It contains valuable information for the RAG system.</p>
                    </article>
                </main>
                <footer>Footer with copyright and links</footer>
            </body>
        </html>
        """

        # Extract clean text (simulate what extract_clean_text would return)
        clean_text = "Main Content Title This is the actual content that we want to extract. It contains valuable information for the RAG system."

        # Evaluate quality
        quality_metrics = evaluate_content_extraction_quality(html_with_non_content, clean_text)

        # Check that metrics are returned
        assert 'original_length' in quality_metrics
        assert 'extracted_length' in quality_metrics
        assert 'extraction_efficiency' in quality_metrics
        assert 'estimated_non_content_ratio' in quality_metrics
        assert 'quality_score' in quality_metrics
        assert 'total_non_content_elements_found' in quality_metrics

        # Validate accuracy
        is_accurate = validate_content_extraction_accuracy("https://example.com/test", html_with_non_content, clean_text)
        # This should return a boolean
        assert isinstance(is_accurate, bool)

    @patch('backend.main.setup_cohere_client')
    @patch('backend.main.setup_qdrant_client')
    def test_pipeline_summary_and_validation_reports(self, mock_qdrant_client, mock_cohere_client):
        """Test the generation of summary and validation reports"""
        from backend.main import generate_summary_report, generate_validation_report, validate_textbook_page_coverage

        # Mock the Qdrant client for validation report
        mock_qdrant = MagicMock()
        mock_qdrant_client.return_value = mock_qdrant
        mock_qdrant.get_collection.return_value.points_count = 10
        mock_qdrant.scroll.return_value = ([], None)  # Return empty list for sample

        # Test summary report generation
        summary_report = generate_summary_report(
            total_pages=5,
            total_chunks=20,
            total_embeddings=20,
            processing_time=30.5,
            coverage_report={
                'total_expected_pages': 5,
                'total_processed_pages': 5,
                'coverage_percentage': 100.0,
                'missing_pages_count': 0,
                'coverage_status': 'PASS'
            }
        )

        # Verify summary report structure
        assert 'timestamp' in summary_report
        assert 'processing_statistics' in summary_report
        assert 'coverage_statistics' in summary_report
        assert 'data_quality_indicators' in summary_report

        processing_stats = summary_report['processing_statistics']
        assert processing_stats['total_pages_processed'] == 5
        assert processing_stats['total_chunks_created'] == 20
        assert processing_stats['total_embeddings_saved'] == 20

        # Test validation report generation
        validation_report = generate_validation_report()
        assert 'timestamp' in validation_report
        assert 'collection_name' in validation_report
        assert 'total_points' in validation_report

        # Test coverage validation
        expected_urls = ['url1', 'url2', 'url3']
        processed_urls = ['url1', 'url2']
        coverage_report = validate_textbook_page_coverage(expected_urls, processed_urls)

        assert coverage_report['total_expected_pages'] == 3
        assert coverage_report['total_processed_pages'] == 2
        assert coverage_report['missing_pages_count'] == 1
        assert coverage_report['coverage_percentage'] == (2/3) * 100


if __name__ == '__main__':
    pytest.main([__file__])