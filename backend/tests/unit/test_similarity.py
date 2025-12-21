import unittest
import math
from src.services.similarity_service import SimilarityService
from src.models.vector_record import VectorRecord


class TestSimilarityService(unittest.TestCase):
    def setUp(self):
        self.service = SimilarityService()

    def test_calculate_cosine_similarity_identical_vectors(self):
        # Arrange
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]

        # Act
        similarity = self.service.calculate_cosine_similarity(vec1, vec2)

        # Assert
        self.assertEqual(similarity, 1.0)

    def test_calculate_cosine_similarity_orthogonal_vectors(self):
        # Arrange
        vec1 = [1.0, 0.0]
        vec2 = [0.0, 1.0]

        # Act
        similarity = self.service.calculate_cosine_similarity(vec1, vec2)

        # Assert
        self.assertAlmostEqual(similarity, 0.0, places=7)

    def test_calculate_cosine_similarity_opposite_vectors(self):
        # Arrange
        vec1 = [1.0, 0.0]
        vec2 = [-1.0, 0.0]

        # Act
        similarity = self.service.calculate_cosine_similarity(vec1, vec2)

        # Assert
        self.assertEqual(similarity, -1.0)

    def test_calculate_cosine_similarity_different_lengths(self):
        # Arrange
        vec1 = [1.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]

        # Act & Assert
        with self.assertRaises(ValueError):
            self.service.calculate_cosine_similarity(vec1, vec2)

    def test_select_random_vectors_for_testing(self):
        # Arrange
        mock_vectors = [
            VectorRecord(
                id=str(i),
                embedding=[float(i), float(i+1), float(i+2)],
                metadata={"position": str(i), "url": "test", "module": "test", "section": "test", "hash": "test", "source_text": f"test text {i}"},
                timestamps={"ingestion": "2023-01-01", "retrieval": "2023-01-01"}
            ) for i in range(20)
        ]

        # Act
        selected = self.service.select_random_vectors_for_testing(mock_vectors, 5)

        # Assert
        self.assertEqual(len(selected), 5)
        # All selected vectors should be from the original list
        for vector in selected:
            self.assertIn(vector, mock_vectors)

    def test_select_random_vectors_for_testing_fewer_than_requested(self):
        # Arrange
        mock_vectors = [
            VectorRecord(
                id=str(i),
                embedding=[float(i), float(i+1), float(i+2)],
                metadata={"position": str(i), "url": "test", "module": "test", "section": "test", "hash": "test", "source_text": f"test text {i}"},
                timestamps={"ingestion": "2023-01-01", "retrieval": "2023-01-01"}
            ) for i in range(3)
        ]

        # Act
        selected = self.service.select_random_vectors_for_testing(mock_vectors, 10)

        # Assert
        self.assertEqual(len(selected), 3)  # Should return all available vectors
        for vector in selected:
            self.assertIn(vector, mock_vectors)


if __name__ == '__main__':
    unittest.main()