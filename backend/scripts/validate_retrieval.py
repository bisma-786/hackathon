#!/usr/bin/env python3
"""
Script to run comprehensive validation of the RAG retrieval system
"""
import argparse
import json
import os
from datetime import datetime
from src.services.validation_service import ValidationService
from src.services.qdrant_retrieval_service import QdrantRetrievalService


def main():
    parser = argparse.ArgumentParser(description="Run comprehensive validation of RAG retrieval system")
    parser.add_argument("--url", help="URL to validate")
    parser.add_argument("--module", help="Module to validate")
    parser.add_argument("--section", help="Section to validate")
    parser.add_argument("--output", help="Output file for validation report", default=None)
    parser.add_argument("--validation-type", choices=["metadata_integrity", "comprehensive"],
                       default="comprehensive", help="Type of validation to run")

    args = parser.parse_args()

    # Initialize validation service
    validation_service = ValidationService()

    print(f"Starting {args.validation_type} validation...")

    if args.validation_type == "metadata_integrity":
        report = validation_service.validate_metadata_integrity(
            url=args.url,
            module=args.module,
            section=args.section
        )
    else:  # comprehensive
        report = validation_service.validate_comprehensive(
            url=args.url,
            module=args.module,
            section=args.section
        )

    # Print results
    print("\nValidation Summary:")
    print(f"  Total Vectors: {report.summary['total_vectors']}")
    print(f"  Successful Retrievals: {report.summary['successful_retrievals']}")
    print(f"  Failed Retrievals: {report.summary['failed_retrievals']}")
    print(f"  Success Rate: {report.summary['success_rate']:.2f}%")
    print(f"  Validation Type: {report.summary['validation_type']}")
    print(f"  Execution Time: {report.metrics['execution_time']:.2f}s")

    if report.errors:
        print(f"\nErrors found: {len(report.errors)}")
        for error in report.errors[:5]:  # Show first 5 errors
            print(f"  - Vector {error['vector_id']}: {error['error_message']}")
        if len(report.errors) > 5:
            print(f"  ... and {len(report.errors) - 5} more errors")

    # Save report to file if requested
    if args.output:
        # Ensure output directory exists
        output_dir = os.path.dirname(args.output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        with open(args.output, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)
        print(f"\nValidation report saved to: {args.output}")

    # Return exit code based on validation results
    if report.summary['failed_retrievals'] > 0:
        print(f"\nValidation completed with {report.summary['failed_retrievals']} errors.")
        exit(1)
    else:
        print("\nAll validations passed!")
        exit(0)


if __name__ == "__main__":
    main()