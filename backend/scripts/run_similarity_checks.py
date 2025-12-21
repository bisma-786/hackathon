#!/usr/bin/env python3
"""
Script to run embedding similarity validation checks
"""
import argparse
import json
import os
from datetime import datetime
from src.services.qdrant_retrieval_service import QdrantRetrievalService
from src.services.similarity_service import SimilarityService


def main():
    parser = argparse.ArgumentParser(description="Run embedding similarity validation checks")
    parser.add_argument("--url", help="URL to validate similarity for")
    parser.add_argument("--module", help="Module to validate similarity for")
    parser.add_argument("--section", help="Section to validate similarity for")
    parser.add_argument("--count", type=int, default=10, help="Number of random vectors to test")
    parser.add_argument("--output", help="Output file for similarity report", default=None)

    args = parser.parse_args()

    # Initialize services
    retrieval_service = QdrantRetrievalService()
    similarity_service = SimilarityService()

    print(f"Starting similarity validation for {'all vectors' if not any([args.url, args.module, args.section]) else 'specified vectors'}...")

    # Retrieve vectors based on provided identifier
    if args.url:
        vectors, count = retrieval_service.retrieve_by_url(args.url)
        identifier = f"URL: {args.url}"
    elif args.module:
        vectors, count = retrieval_service.retrieve_by_module(args.module)
        identifier = f"Module: {args.module}"
    elif args.section:
        vectors, count = retrieval_service.retrieve_by_section(args.section)
        identifier = f"Section: {args.section}"
    else:
        print("Error: One of --url, --module, or --section must be provided")
        exit(1)

    print(f"Retrieved {len(vectors)} vectors for {identifier}")

    if not vectors:
        print(f"No vectors found for {identifier}")
        exit(0)

    # Select random vectors for testing
    selected_vectors = similarity_service.select_random_vectors_for_testing(vectors, args.count)
    print(f"Selected {len(selected_vectors)} random vectors for similarity testing...")

    # Run similarity validation
    results = similarity_service.run_similarity_validation(selected_vectors)

    # Print results
    print("\nSimilarity Validation Results:")
    print(f"  Total Records Tested: {results['total_records']}")
    print(f"  Valid Records: {results['valid_records']}")
    print(f"  Invalid Records: {results['invalid_records']}")
    print(f"  Success Rate: {results['success_rate']:.2f}%")
    print(f"  Average Similarity Score: {results['average_similarity_score']:.4f}")
    print(f"  Execution Time: {results['execution_time']:.2f}s")

    if results['low_quality_embeddings']:
        print(f"\nLow quality embeddings found: {len(results['low_quality_embeddings'])}")
        for embedding in results['low_quality_embeddings'][:5]:  # Show first 5
            print(f"  - Vector {embedding['vector_id']}: {embedding['similarity_score']:.4f} (threshold: {embedding['threshold']})")
        if len(results['low_quality_embeddings']) > 5:
            print(f"  ... and {len(results['low_quality_embeddings']) - 5} more low quality embeddings")

    # Save report to file if requested
    if args.output:
        # Ensure output directory exists
        output_dir = os.path.dirname(args.output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nSimilarity report saved to: {args.output}")

    # Return exit code based on validation results
    if results['invalid_records'] > 0:
        print(f"\nSimilarity validation completed with {results['invalid_records']} low quality embeddings.")
        exit(1)
    else:
        print("\nAll similarity validations passed!")
        exit(0)


if __name__ == "__main__":
    main()