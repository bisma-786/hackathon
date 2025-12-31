"""
Basic tests for the RAG agent functionality.
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add backend directory to path to import agent module
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from agent import answer_question, health_check, validate_input, check_retrieved_content_quality


class TestAgentFunctionality(unittest.TestCase):
    """Test cases for the RAG agent functionality."""

    def test_validate_input_valid_query(self):
        """Test that valid input queries are accepted."""
        result = validate_input("What is ROS 2?")
        self.assertTrue(result["is_valid"])
        self.assertEqual(len(result["errors"]), 0)

    def test_validate_input_empty_query(self):
        """Test that empty queries are rejected."""
        result = validate_input("")
        self.assertFalse(result["is_valid"])
        self.assertIn("Query cannot be empty", result["errors"])

    def test_validate_input_whitespace_query(self):
        """Test that whitespace-only queries are rejected."""
        result = validate_input("   ")
        self.assertFalse(result["is_valid"])
        self.assertIn("Query cannot be empty or contain only whitespace", result["errors"])

    def test_validate_input_long_query(self):
        """Test that very long queries are rejected."""
        long_query = "x" * 10001  # More than 10000 characters
        result = validate_input(long_query)
        self.assertFalse(result["is_valid"])
        self.assertIn("Query is too long", result["errors"][0])

    def test_check_retrieved_content_quality(self):
        """Test content quality checking functionality."""
        # Mock RetrievedChunk objects
        class MockChunk:
            def __init__(self, score):
                self.score = score

        high_score_chunks = [MockChunk(0.8), MockChunk(0.9)]
        low_score_chunks = [MockChunk(0.05), MockChunk(0.02)]
        mixed_chunks = [MockChunk(0.8), MockChunk(0.05)]

        # Test high quality chunks
        result = check_retrieved_content_quality(high_score_chunks, min_score=0.1)
        self.assertTrue(result["has_valid_content"])
        self.assertEqual(result["valid_chunks"], 2)
        self.assertEqual(result["low_score_chunks"], 0)

        # Test low quality chunks
        result = check_retrieved_content_quality(low_score_chunks, min_score=0.1)
        self.assertFalse(result["has_valid_content"])
        self.assertEqual(result["valid_chunks"], 0)
        self.assertEqual(result["low_score_chunks"], 2)

        # Test mixed quality chunks
        result = check_retrieved_content_quality(mixed_chunks, min_score=0.1)
        self.assertTrue(result["has_valid_content"])
        self.assertEqual(result["valid_chunks"], 1)
        self.assertEqual(result["low_score_chunks"], 1)

    @patch('backend.agent.retrieve_chunks')
    @patch('agents.Runner.run_sync')
    def test_answer_question_with_mocked_retrieval(self, mock_runner_run_sync, mock_retrieve_chunks):
        """Test answer_question function with mocked external dependencies."""
        # Mock the retrieve_chunks function to return some dummy chunks
        class MockChunk:
            def __init__(self, id, content, score):
                self.id = id
                self.content = content
                self.score = score

        mock_retrieve_chunks.return_value = [
            MockChunk("chunk1", "This is some relevant content about ROS 2.", 0.85),
            MockChunk("chunk2", "ROS 2 is a robotics framework.", 0.72)
        ]

        # Mock the Agents SDK result
        mock_result = MagicMock()
        mock_result.final_output = "ROS 2 is a flexible framework for robotics development."
        mock_runner_run_sync.return_value = mock_result

        # Test the function
        result = answer_question("What is ROS 2?")

        # Check that the result has the expected structure
        self.assertIn("response", result)
        self.assertIn("source_chunks", result)
        self.assertIn("content_quality", result)
        self.assertTrue(result["content_quality"]["has_valid_content"])

    def test_health_check(self):
        """Test health check functionality."""
        result = health_check()
        self.assertIn("status", result)
        self.assertIn("dependencies", result)
        self.assertIn("timestamp", result)


if __name__ == "__main__":
    unittest.main()