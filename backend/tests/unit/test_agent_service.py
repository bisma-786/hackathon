"""
Unit tests for the AgentService class
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from src.services.agent_service import AgentService
from src.models.agent_models import AgentRequest
from src.services.qdrant_service import QdrantService


class TestAgentService:
    """Test suite for AgentService"""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Mock the OpenAI client and Qdrant service to avoid external dependencies
        with patch('src.services.agent_service.get_openai_client'):
            with patch('src.services.agent_service.get_qdrant_client'):
                with patch('src.services.agent_service.get_collection_name'):
                    self.agent_service = AgentService()

    def test_process_agent_query_success(self):
        """Test successful processing of an agent query"""
        # Mock the dependencies
        mock_request = AgentRequest(
            query="What is AI-driven robotics?",
            context=["test context"]
        )

        # Mock the _retrieve_context method
        self.agent_service._retrieve_context = Mock(return_value=[
            {
                'id': 'test_id',
                'content': 'AI-driven robotics combines artificial intelligence with robotics.',
                'url': 'http://example.com',
                'module': 'Introduction',
                'section': 'Basics',
                'similarity_score': 0.85
            }
        ])

        # Mock the _generate_response method
        self.agent_service._generate_response = Mock(return_value="AI-driven robotics is a field that combines AI with robotics.")

        # Mock other helper methods
        self.agent_service._calculate_confidence = Mock(return_value=0.85)
        self.agent_service._extract_sources = Mock(return_value=['http://example.com'])
        self.agent_service._generate_followup_questions = Mock(return_value=['What are the applications?'])

        # Call the method
        result = self.agent_service.process_agent_query(mock_request)

        # Assertions
        assert result.answer == "AI-driven robotics is a field that combines AI with robotics."
        assert result.confidence == 0.85
        assert 'http://example.com' in result.sources
        assert len(result.followup_questions) == 1
        assert 'What are the applications?' in result.followup_questions

    def test_process_agent_query_with_empty_context(self):
        """Test processing agent query when no context is retrieved"""
        # Mock the dependencies
        mock_request = AgentRequest(
            query="What is AI?",
            context=[]
        )

        # Mock the _retrieve_context method to return empty
        self.agent_service._retrieve_context = Mock(return_value=[])

        # Mock the _generate_response method
        self.agent_service._generate_response = Mock(return_value="I couldn't find relevant information.")

        # Mock other helper methods
        self.agent_service._calculate_confidence = Mock(return_value=0.1)
        self.agent_service._extract_sources = Mock(return_value=[])
        self.agent_service._generate_followup_questions = Mock(return_value=[])

        # Call the method
        result = self.agent_service.process_agent_query(mock_request)

        # Assertions
        assert result.answer == "I couldn't find relevant information."
        assert result.confidence == 0.1
        assert len(result.sources) == 0
        assert len(result.followup_questions) == 0

    def test_retrieve_context(self):
        """Test the _retrieve_context method"""
        # Mock the Qdrant service
        mock_qdrant_service = Mock(spec=QdrantService)
        self.agent_service.qdrant_service = mock_qdrant_service

        # Mock search results
        mock_search_result = Mock()
        mock_search_result.vectors = []
        mock_qdrant_service.semantic_search.return_value = mock_search_result

        # Call the method
        result = self.agent_service._retrieve_context("test query")

        # Assertions
        mock_qdrant_service.semantic_search.assert_called_once_with("test query", limit=5)
        assert result == []

    def test_format_context_for_agent_with_content(self):
        """Test formatting context for agent with content"""
        context_chunks = [
            {
                'id': 'test_id',
                'content': 'This is a test content',
                'url': 'http://example.com',
                'module': 'Test Module',
                'section': 'Test Section',
                'similarity_score': 0.85
            }
        ]

        result = self.agent_service._format_context_for_agent(context_chunks)

        assert "Relevant context from the AI-Driven Robotics Textbook:" in result
        assert "This is a test content" in result
        assert "Module: Test Module" in result
        assert "Section: Test Section" in result
        assert "URL: http://example.com" in result

    def test_format_context_for_agent_empty(self):
        """Test formatting context for agent with no content"""
        result = self.agent_service._format_context_for_agent([])

        assert result == "No relevant context found in the textbook."

    def test_calculate_confidence_with_scores(self):
        """Test confidence calculation with similarity scores"""
        context_chunks = [
            {
                'id': 'test_id1',
                'content': 'test content 1',
                'similarity_score': 0.8
            },
            {
                'id': 'test_id2',
                'content': 'test content 2 with more text',
                'similarity_score': 0.9
            }
        ]

        result = self.agent_service._calculate_confidence(context_chunks)

        # Should be higher than 0.1 (the minimum) and based on similarity scores
        assert result > 0.1
        assert result <= 0.95  # Max confidence cap

    def test_calculate_confidence_empty(self):
        """Test confidence calculation with no context"""
        result = self.agent_service._calculate_confidence([])

        assert result == 0.1  # Default low confidence

    def test_extract_sources(self):
        """Test extracting sources from context chunks"""
        context_chunks = [
            {'url': 'http://example1.com'},
            {'url': 'http://example2.com'},
            {'url': 'http://example1.com'},  # Duplicate
            {}  # No URL
        ]

        result = self.agent_service._extract_sources(context_chunks)

        assert len(result) == 2  # Should have unique URLs only
        assert 'http://example1.com' in result
        assert 'http://example2.com' in result

    def test_generate_followup_questions(self):
        """Test generating follow-up questions"""
        # For now, this method returns an empty list
        result = self.agent_service._generate_followup_questions("original query", "response")

        assert result == []