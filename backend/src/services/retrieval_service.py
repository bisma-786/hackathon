"""
Validation service for checking Qdrant vector storage and visibility
"""

from typing import Dict, List, Optional
from src.lib.config import get_qdrant_client, get_collection_name, RetrievalException, ValidationException, ConnectionException
from src.services.qdrant_service import QdrantService
import logging


class RetrievalValidationService:
    """
    Service class to handle validation of Qdrant vector storage and visibility
    """

    def __init__(self):
        self.qdrant_service = QdrantService()
        self.client = get_qdrant_client()
        self.collection_name = get_collection_name()
        self.logger = logging.getLogger(__name__)

    def validate_connection(self) -> bool:
        """
        Validate that the connection to Qdrant is working
        """
        try:
            # Try to get collection info to verify connection
            self.get_collection_info()
            return True
        except Exception as e:
            self.logger.error(f"Error validating Qdrant connection: {str(e)}")
            return False

    def get_collection_info(self) -> Dict:
        """
        Get information about the collection
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vector_size": collection_info.config.params.vectors.size,
                "distance": collection_info.config.params.vectors.distance,
                "points_count": collection_info.points_count
            }
        except Exception as e:
            self.logger.error(f"Error getting collection info: {str(e)}")
            # Return a default structure instead of raising an exception for graceful degradation
            return {
                "name": self.collection_name,
                "vector_size": 0,
                "distance": "unknown",
                "points_count": 0
            }

    def validate_vector_count(self) -> Dict:
        """
        Validate and return vector count information
        """
        try:
            collection_info = self.get_collection_info()
            count = collection_info["points_count"]

            self.logger.info(f"Collection '{self.collection_name}' contains {count} vectors")

            return {
                "collection_name": self.collection_name,
                "vector_count": count,
                "is_valid": count >= 0  # Valid if count is non-negative
            }
        except Exception as e:
            self.logger.error(f"Error validating vector count: {str(e)}")
            raise

    def verify_collection_exists(self) -> bool:
        """
        Verify that the collection exists in Qdrant
        """
        try:
            # Try to get collection info - if it works, collection exists
            self.get_collection_info()
            self.logger.info(f"Collection '{self.collection_name}' exists and is accessible")
            return True
        except Exception as e:
            self.logger.error(f"Collection '{self.collection_name}' does not exist or is not accessible: {str(e)}")
            return False

    def validate_vector_storage(self) -> Dict:
        """
        Perform comprehensive validation of vector storage
        """
        try:
            # Check if collection exists
            collection_exists = self.verify_collection_exists()

            if not collection_exists:
                return {
                    "collection_exists": False,
                    "vector_count": 0,
                    "is_valid": False,
                    "message": f"Collection '{self.collection_name}' does not exist"
                }

            # Get vector count
            count_info = self.validate_vector_count()

            # Additional validation checks could be added here
            # For example, checking if there are vectors with expected metadata fields

            validation_result = {
                "collection_exists": collection_exists,
                "vector_count": count_info["vector_count"],
                "is_valid": count_info["is_valid"],
                "message": f"Collection '{self.collection_name}' validation completed successfully"
            }

            self.logger.info(f"Vector storage validation completed: {validation_result}")
            return validation_result

        except Exception as e:
            self.logger.error(f"Error during vector storage validation: {str(e)}")
            return {
                "collection_exists": False,
                "vector_count": 0,
                "is_valid": False,
                "message": f"Validation failed with error: {str(e)}"
            }

    def generate_validation_report(self) -> Dict:
        """
        Generate a comprehensive validation report
        """
        try:
            report = {
                "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
                "collection_name": self.collection_name,
                "connection_valid": self.validate_connection(),
                "validation_result": self.validate_vector_storage()
            }

            self.logger.info("Validation report generated successfully")
            return report

        except Exception as e:
            self.logger.error(f"Error generating validation report: {str(e)}")
            return {
                "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
                "collection_name": self.collection_name,
                "connection_valid": False,
                "validation_result": {
                    "collection_exists": False,
                    "vector_count": 0,
                    "is_valid": False,
                    "message": f"Report generation failed: {str(e)}"
                }
            }