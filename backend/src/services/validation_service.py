import logging
from typing import List, Dict, Tuple
from datetime import datetime
import time
from src.models.validation_report import ValidationReport
from src.models.vector_record import VectorRecord
from src.services.qdrant_retrieval_service import QdrantRetrievalService


class ValidationService:
    """
    Service class to handle all validation operations for vector retrieval
    """
    def __init__(self):
        self.retrieval_service = QdrantRetrievalService()
        self.logger = logging.getLogger(__name__)

    def validate_metadata_integrity(
        self,
        url: str = None,
        module: str = None,
        section: str = None
    ) -> ValidationReport:
        """
        Validate that all metadata fields are preserved correctly during ingestion and retrieval
        """
        start_time = time.time()

        # Retrieve vectors based on provided identifier
        if url:
            vectors, count = self.retrieval_service.retrieve_by_url(url)
            identifier = f"URL: {url}"
        elif module:
            vectors, count = self.retrieval_service.retrieve_by_module(module)
            identifier = f"Module: {module}"
        elif section:
            vectors, count = self.retrieval_service.retrieve_by_section(section)
            identifier = f"Section: {section}"
        else:
            raise ValueError("One of url, module, or section must be provided")

        validation_details = []
        validation_errors = []
        successful_validations = 0

        for vector in vectors:
            vector_id = vector.id
            vector_details = {
                'vector_id': vector_id,
                'status': 'success',
                'validation_steps': []
            }

            # Validate metadata fields
            metadata_validations = [
                ('url', 'URL'),
                ('module', 'Module'),
                ('section', 'Section'),
                ('position', 'Position'),
                ('hash', 'Hash')
            ]

            step_results = []
            for field, field_name in metadata_validations:
                if field in vector.metadata:
                    if vector.metadata[field]:
                        step_results.append({
                            'step': f'{field_name} field exists and is not empty',
                            'status': 'success',
                            'details': f'{field_name}: {vector.metadata[field]}'
                        })
                    else:
                        step_results.append({
                            'step': f'{field_name} field is empty',
                            'status': 'failure',
                            'details': f'{field_name} field is empty for vector {vector_id}'
                        })
                        validation_errors.append({
                            'vector_id': vector_id,
                            'error_type': 'metadata_empty',
                            'error_message': f'{field_name} field is empty',
                            'context': {'field': field, 'value': vector.metadata[field]}
                        })
                else:
                    step_results.append({
                        'step': f'{field_name} field missing',
                        'status': 'failure',
                        'details': f'{field_name} field is missing for vector {vector_id}'
                    })
                    validation_errors.append({
                        'vector_id': vector_id,
                        'error_type': 'metadata_missing',
                        'error_message': f'{field_name} field is missing',
                        'context': {'field': field}
                    })

            # Validate position is a valid integer
            try:
                position = int(vector.metadata.get('position', '0'))
                step_results.append({
                    'step': 'Position is valid integer',
                    'status': 'success',
                    'details': f'Position: {position}'
                })
            except ValueError:
                step_results.append({
                    'step': 'Position is not a valid integer',
                    'status': 'failure',
                    'details': f'Position {vector.metadata.get("position")} is not a valid integer for vector {vector_id}'
                })
                validation_errors.append({
                    'vector_id': vector_id,
                    'error_type': 'invalid_position',
                    'error_message': 'Position is not a valid integer',
                    'context': {'position': vector.metadata.get('position')}
                })

            # Check if all steps passed
            all_passed = all(step['status'] == 'success' for step in step_results)
            if all_passed:
                successful_validations += 1

            vector_details['validation_steps'] = step_results
            validation_details.append(vector_details)

        execution_time = time.time() - start_time
        report = ValidationReport.create_report(
            report_id=f"metadata_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            validation_type="metadata_integrity",
            total_vectors=count,
            successful_retrievals=successful_validations,
            failed_retrievals=count - successful_validations,
            validation_details=validation_details,
            validation_errors=validation_errors,
            execution_time=execution_time
        )

        self.logger.info(f"Metadata validation completed for {identifier}. Success: {successful_validations}/{count}")
        return report

    def validate_chunk_sequence(self, vectors: List[VectorRecord]) -> Tuple[int, List[Dict]]:
        """
        Validate that chunk indices are sequential and match original ingestion order
        """
        errors = []
        valid_count = 0

        # Sort vectors by position
        sorted_vectors = sorted(vectors, key=lambda v: int(v.metadata.get('position', 0)))

        expected_position = 0
        for vector in sorted_vectors:
            actual_position = int(vector.metadata.get('position', -1))

            if actual_position == expected_position:
                valid_count += 1
            else:
                errors.append({
                    'vector_id': vector.id,
                    'error_type': 'sequence_mismatch',
                    'error_message': f'Expected position {expected_position}, got {actual_position}',
                    'context': {
                        'expected_position': expected_position,
                        'actual_position': actual_position
                    }
                })

            expected_position += 1

        return valid_count, errors

    def validate_comprehensive(
        self,
        validation_type: str = "comprehensive",
        url: str = None,
        module: str = None,
        section: str = None
    ) -> ValidationReport:
        """
        Perform comprehensive validation of the retrieval pipeline
        """
        start_time = time.time()

        # Retrieve vectors based on provided identifier
        if url:
            vectors, count = self.retrieval_service.retrieve_by_url(url)
            identifier = f"URL: {url}"
        elif module:
            vectors, count = self.retrieval_service.retrieve_by_module(module)
            identifier = f"Module: {module}"
        elif section:
            vectors, count = self.retrieval_service.retrieve_by_section(section)
            identifier = f"Section: {section}"
        else:
            # If no specific identifier, we'll do a general validation
            vectors = []
            count = 0
            identifier = "General"

        validation_details = []
        validation_errors = []
        successful_validations = 0

        # Perform metadata validation
        metadata_report = self.validate_metadata_integrity(url=url, module=module, section=section)
        validation_errors.extend(metadata_report.errors)

        # Validate chunk sequence if we have vectors
        if vectors:
            valid_chunks, sequence_errors = self.validate_chunk_sequence(vectors)
            validation_errors.extend(sequence_errors)
            successful_validations = valid_chunks

        execution_time = time.time() - start_time
        report = ValidationReport.create_report(
            report_id=f"comprehensive_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            validation_type=validation_type,
            total_vectors=count,
            successful_retrievals=successful_validations,
            failed_retrievals=len(validation_errors),
            validation_details=validation_details,
            validation_errors=validation_errors,
            execution_time=execution_time
        )

        self.logger.info(f"Comprehensive validation completed for {identifier}. Total: {count}, Errors: {len(validation_errors)}")
        return report