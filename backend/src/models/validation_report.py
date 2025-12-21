from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class ValidationReport:
    """
    Represents the results of a validation run, including statistics, details, and errors.
    """
    id: str
    timestamp: datetime
    summary: Dict  # Overall validation statistics and success rates
    details: List[Dict]  # Individual record validation results
    errors: List[Dict]  # List of failed validations with error details
    metrics: Dict  # Performance and quality metrics

    @classmethod
    def create_report(
        cls,
        report_id: str,
        validation_type: str,
        total_vectors: int,
        successful_retrievals: int,
        failed_retrievals: int,
        validation_details: List[Dict],
        validation_errors: List[Dict],
        execution_time: float,
        **additional_metrics
    ) -> 'ValidationReport':
        """
        Create a ValidationReport with computed summary statistics
        """
        success_rate = (successful_retrievals / total_vectors * 100) if total_vectors > 0 else 0

        summary = {
            'total_vectors': total_vectors,
            'successful_retrievals': successful_retrievals,
            'failed_retrievals': failed_retrievals,
            'success_rate': success_rate,
            'validation_type': validation_type
        }

        metrics = {
            'execution_time': execution_time,
            'queries_per_second': total_vectors / execution_time if execution_time > 0 else 0,
            **additional_metrics
        }

        return cls(
            id=report_id,
            timestamp=datetime.now(),
            summary=summary,
            details=validation_details,
            errors=validation_errors,
            metrics=metrics
        )

    def to_dict(self) -> Dict:
        """
        Convert ValidationReport to dictionary format for API responses
        """
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'summary': self.summary,
            'details': self.details,
            'errors': self.errors,
            'metrics': self.metrics
        }