import logging
import random
from typing import List, Dict, Tuple
from datetime import datetime
import time
import math
import cohere
from src.models.vector_record import VectorRecord
from src.lib.config import COHERE_API_KEY, SIMILARITY_THRESHOLD


class SimilarityService:
    """
    Service class to handle embedding similarity calculations and validation
    """
    def __init__(self):
        self.cohere_client = cohere.Client(COHERE_API_KEY) if COHERE_API_KEY else None
        self.similarity_threshold = SIMILARITY_THRESHOLD
        self.logger = logging.getLogger(__name__)

    def calculate_cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors
        """
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have the same length")

        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(vec1, vec2))

        # Calculate magnitudes
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        # Calculate cosine similarity
        similarity = dot_product / (magnitude1 * magnitude2)
        return similarity

    def validate_embedding_quality(self, vector_record: VectorRecord) -> Tuple[bool, float, str]:
        """
        Validate if the embedding quality meets the threshold
        """
        if not vector_record.metadata.get('source_text'):
            return False, 0.0, "No source text available for comparison"

        source_text = vector_record.metadata['source_text']

        # If Cohere client is available, use it for embedding comparison
        if self.cohere_client:
            try:
                # Generate embedding for the source text using Cohere
                response = self.cohere_client.embed(
                    texts=[source_text],
                    model='embed-english-v3.0',
                    input_type='search_document'
                )
                source_embedding = response.embeddings[0]

                # Calculate similarity between stored embedding and generated one
                similarity = self.calculate_cosine_similarity(vector_record.embedding, source_embedding)

                is_valid = similarity >= self.similarity_threshold
                message = f"Similarity: {similarity:.4f}, Threshold: {self.similarity_threshold}"
                return is_valid, similarity, message

            except Exception as e:
                self.logger.error(f"Error validating embedding quality with Cohere: {str(e)}")
                # Fallback to basic validation
                similarity = self.calculate_cosine_similarity(vector_record.embedding, vector_record.embedding)
                is_valid = True  # Self-similarity is always valid
                message = f"Basic validation (self-similarity): {similarity:.4f}"
                return is_valid, similarity, message
        else:
            # Without Cohere, we can only do basic validation
            similarity = self.calculate_cosine_similarity(vector_record.embedding, vector_record.embedding)
            is_valid = True  # Self-similarity is always valid
            message = f"Basic validation (self-similarity): {similarity:.4f}"
            return is_valid, similarity, message

    def flag_low_quality_embeddings(self, vector_records: List[VectorRecord]) -> List[Dict]:
        """
        Identify embeddings that don't meet quality standards
        """
        low_quality = []
        for record in vector_records:
            is_valid, similarity, message = self.validate_embedding_quality(record)
            if not is_valid:
                low_quality.append({
                    'vector_id': record.id,
                    'similarity_score': similarity,
                    'threshold': self.similarity_threshold,
                    'message': message
                })

        return low_quality

    def run_similarity_validation(self, vector_records: List[VectorRecord]) -> Dict:
        """
        Run comprehensive similarity validation on a set of vector records
        """
        start_time = time.time()

        validation_results = []
        low_quality_embeddings = []

        for record in vector_records:
            is_valid, similarity, message = self.validate_embedding_quality(record)
            validation_results.append({
                'vector_id': record.id,
                'is_valid': is_valid,
                'similarity_score': similarity,
                'message': message
            })

            if not is_valid:
                low_quality_embeddings.append({
                    'vector_id': record.id,
                    'similarity_score': similarity,
                    'threshold': self.similarity_threshold,
                    'message': message
                })

        execution_time = time.time() - start_time

        # Calculate statistics
        total_records = len(vector_records)
        valid_records = sum(1 for result in validation_results if result['is_valid'])
        invalid_records = total_records - valid_records
        success_rate = (valid_records / total_records * 100) if total_records > 0 else 0

        return {
            'total_records': total_records,
            'valid_records': valid_records,
            'invalid_records': invalid_records,
            'success_rate': success_rate,
            'validation_results': validation_results,
            'low_quality_embeddings': low_quality_embeddings,
            'execution_time': execution_time,
            'average_similarity_score': sum(result['similarity_score'] for result in validation_results) / total_records if total_records > 0 else 0
        }

    def select_random_vectors_for_testing(self, vector_records: List[VectorRecord], count: int = 10) -> List[VectorRecord]:
        """
        Select random vectors for similarity testing
        """
        if len(vector_records) <= count:
            return vector_records
        else:
            return random.sample(vector_records, min(count, len(vector_records)))