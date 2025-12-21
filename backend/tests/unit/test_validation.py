import unittest
from unittest.mock import Mock, patch
from src.services.validation_service import ValidationService
from src.models.vector_record import VectorRecord


class TestValidationService(unittest.TestCase):
    def setUp(self):
        self.service = ValidationService()

    def test_validate_chunk_sequence_valid(self):
        # Arrange
        mock_vectors = [
            VectorRecord(
                id="1",
                embedding=[0.1, 0.2, 0.3],
                metadata={"position": "0", "url": "test", "module": "test", "section": "test", "hash": "test", "source_text": "test"},
                timestamps={"ingestion": "2023-01-01", "retrieval": "2023-01-01"}
            ),
            VectorRecord(
                id="2",
                embedding=[0.4, 0.5, 0.6],
                metadata={"position": "1", "url": "test", "module": "test", "section": "test", "hash": "test", "source_text": "test"},
                timestamps={"ingestion": "2023-01-01", "retrieval": "2023-01-01"}
            ),
            VectorRecord(
                id="3",
                embedding=[0.7, 0.8, 0.9],
                metadata={"position": "2", "url": "test", "module": "test", "section": "test", "hash": "test", "source_text": "test"},
                timestamps={"ingestion": "2023-01-01", "retrieval": "2023-01-01"}
            )
        ]

        # Act
        valid_count, errors = self.service.validate_chunk_sequence(mock_vectors)

        # Assert
        self.assertEqual(valid_count, 3)
        self.assertEqual(len(errors), 0)

    def test_validate_chunk_sequence_invalid(self):
        # Arrange
        mock_vectors = [
            VectorRecord(
                id="1",
                embedding=[0.1, 0.2, 0.3],
                metadata={"position": "0", "url": "test", "module": "test", "section": "test", "hash": "test", "source_text": "test"},
                timestamps={"ingestion": "2023-01-01", "retrieval": "2023-01-01"}
            ),
            VectorRecord(
                id="2",
                embedding=[0.4, 0.5, 0.6],
                metadata={"position": "5", "url": "test", "module": "test", "section": "test", "hash": "test", "source_text": "test"},
                timestamps={"ingestion": "2023-01-01", "retrieval": "2023-01-01"}
            ),
            VectorRecord(
                id="3",
                embedding=[0.7, 0.8, 0.9],
                metadata={"position": "2", "url": "test", "module": "test", "section": "test", "hash": "test", "source_text": "test"},
                timestamps={"ingestion": "2023-01-01", "retrieval": "2023-01-01"}
            )
        ]

        # Act
        valid_count, errors = self.service.validate_chunk_sequence(mock_vectors)

        # Assert
        self.assertEqual(valid_count, 1)  # Only first vector is valid
        self.assertEqual(len(errors), 2)  # Two errors for positions 5 and 2 (expected 1 and 2 respectively)

    @patch.object(ValidationService, 'retrieval_service')
    def test_validate_metadata_integrity(self, mock_retrieval_service):
        # Arrange
        mock_vectors = [
            VectorRecord(
                id="1",
                embedding=[0.1, 0.2, 0.3],
                metadata={"url": "https://example.com", "module": "test", "section": "intro", "position": "0", "hash": "abc123", "source_text": "test text"},
                timestamps={"ingestion": "2023-01-01", "retrieval": "2023-01-01"}
            )
        ]
        mock_retrieval_service.retrieve_by_url.return_value = (mock_vectors, 1)

        # Act
        report = self.service.validate_metadata_integrity(url="https://example.com")

        # Assert
        self.assertIsNotNone(report)
        self.assertEqual(report.summary['total_vectors'], 1)
        self.assertEqual(report.summary['validation_type'], "metadata_integrity")


if __name__ == '__main__':
    unittest.main()