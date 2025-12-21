import unittest
from unittest.mock import Mock, patch, MagicMock
from src.services.qdrant_retrieval_service import QdrantRetrievalService
from src.services.validation_service import ValidationService
from src.services.similarity_service import SimilarityService
from src.models.vector_record import VectorRecord


class TestRetrievalPipelineIntegration(unittest.TestCase):
    def setUp(self):
        # Create mock services to avoid needing actual Qdrant connection
        self.mock_retrieval_service = QdrantRetrievalService()
        self.validation_service = ValidationService()
        self.similarity_service = SimilarityService()

    @patch.object(QdrantRetrievalService, 'client', create=True)
    def test_full_retrieval_validation_pipeline(self, mock_client):
        """
        Test the integration between retrieval, validation, and similarity services
        """
        # Mock the Qdrant client response
        mock_vector_payload = {
            "url": "https://example.com/test",
            "module": "test_module",
            "section": "test_section",
            "position": "0",
            "hash": "test_hash",
            "source_text": "This is a test text for similarity validation."
        }

        mock_point = Mock()
        mock_point.id = "test_id_1"
        mock_point.vector = [0.1, 0.2, 0.3, 0.4, 0.5]
        mock_point.payload = mock_vector_payload

        # Configure the mock client to return our test data
        mock_client.scroll.return_value = ([mock_point], None)

        # Test retrieval
        vectors, count = self.mock_retrieval_service.retrieve_by_url("https://example.com/test")

        # Verify retrieval worked
        self.assertEqual(count, 1)
        self.assertEqual(len(vectors), 1)
        retrieved_vector = vectors[0]
        self.assertIsInstance(retrieved_vector, VectorRecord)
        self.assertEqual(retrieved_vector.metadata['url'], "https://example.com/test")

        # Test validation
        validation_report = self.validation_service.validate_metadata_integrity(
            url="https://example.com/test"
        )

        # Verify validation worked
        self.assertIsNotNone(validation_report)
        self.assertEqual(validation_report.summary['validation_type'], "metadata_integrity")
        self.assertEqual(validation_report.summary['total_vectors'], 1)

        # Test similarity validation
        similarity_results = self.similarity_service.run_similarity_validation(vectors)

        # Verify similarity validation worked
        self.assertIsNotNone(similarity_results)
        self.assertEqual(similarity_results['total_records'], 1)
        self.assertIn('success_rate', similarity_results)
        self.assertIn('execution_time', similarity_results)

    def test_comprehensive_validation_pipeline(self):
        """
        Test the comprehensive validation workflow
        """
        # Create test vectors
        test_vectors = [
            VectorRecord(
                id="test_1",
                embedding=[0.1, 0.2, 0.3],
                metadata={
                    "url": "https://example.com/test",
                    "module": "test_module",
                    "section": "test_section",
                    "position": "0",
                    "hash": "hash1",
                    "source_text": "Test text 1"
                },
                timestamps={"ingestion": "2023-01-01", "retrieval": "2023-01-01"}
            ),
            VectorRecord(
                id="test_2",
                embedding=[0.4, 0.5, 0.6],
                metadata={
                    "url": "https://example.com/test",
                    "module": "test_module",
                    "section": "test_section",
                    "position": "1",
                    "hash": "hash2",
                    "source_text": "Test text 2"
                },
                timestamps={"ingestion": "2023-01-01", "retrieval": "2023-01-01"}
            )
        ]

        # Test chunk sequence validation
        valid_count, errors = self.validation_service.validate_chunk_sequence(test_vectors)
        self.assertEqual(valid_count, 2)  # Both should be valid
        self.assertEqual(len(errors), 0)

        # Test similarity validation
        similarity_results = self.similarity_service.run_similarity_validation(test_vectors)
        self.assertIsNotNone(similarity_results)
        self.assertEqual(similarity_results['total_records'], 2)

        # Test comprehensive validation report creation
        validation_report = self.validation_service.validate_comprehensive(validation_type="integration_test")
        self.assertIsNotNone(validation_report)
        self.assertIn('validation_type', validation_report.summary)


if __name__ == '__main__':
    unittest.main()