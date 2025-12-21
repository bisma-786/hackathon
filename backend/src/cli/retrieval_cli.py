import argparse
import sys
import json
from src.services.qdrant_retrieval_service import QdrantRetrievalService
from src.services.validation_service import ValidationService
from src.services.similarity_service import SimilarityService


def create_parser():
    """Create argument parser for the CLI"""
    parser = argparse.ArgumentParser(
        description="RAG Vector Retrieval and Validation CLI"
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # URL retrieval command
    url_parser = subparsers.add_parser('retrieve-by-url', help='Retrieve vectors by URL')
    url_parser.add_argument('--url', required=True, help='URL to retrieve vectors for')
    url_parser.add_argument('--limit', type=int, default=100, help='Maximum number of vectors to retrieve')
    url_parser.add_argument('--offset', type=int, default=0, help='Offset for pagination')

    # Module retrieval command
    module_parser = subparsers.add_parser('retrieve-by-module', help='Retrieve vectors by module')
    module_parser.add_argument('--module', required=True, help='Module name to retrieve vectors for')
    module_parser.add_argument('--limit', type=int, default=100, help='Maximum number of vectors to retrieve')
    module_parser.add_argument('--offset', type=int, default=0, help='Offset for pagination')

    # Section retrieval command
    section_parser = subparsers.add_parser('retrieve-by-section', help='Retrieve vectors by section')
    section_parser.add_argument('--section', required=True, help='Section name to retrieve vectors for')
    section_parser.add_argument('--limit', type=int, default=100, help='Maximum number of vectors to retrieve')
    section_parser.add_argument('--offset', type=int, default=0, help='Offset for pagination')

    # Metadata validation command
    metadata_parser = subparsers.add_parser('validate-metadata', help='Validate metadata integrity')
    metadata_parser.add_argument('--url', help='URL to validate metadata for')
    metadata_parser.add_argument('--module', help='Module to validate metadata for')
    metadata_parser.add_argument('--section', help='Section to validate metadata for')

    # Similarity validation command
    similarity_parser = subparsers.add_parser('validate-similarity', help='Validate embedding similarity')
    similarity_parser.add_argument('--url', help='URL to validate similarity for')
    similarity_parser.add_argument('--module', help='Module to validate similarity for')
    similarity_parser.add_argument('--section', help='Section to validate similarity for')
    similarity_parser.add_argument('--count', type=int, default=10, help='Number of random vectors to test')

    # Comprehensive validation command
    comprehensive_parser = subparsers.add_parser('validate-comprehensive', help='Run comprehensive validation')
    comprehensive_parser.add_argument('--url', help='URL to validate')
    comprehensive_parser.add_argument('--module', help='Module to validate')
    comprehensive_parser.add_argument('--section', help='Section to validate')

    return parser


def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command.startswith('retrieve-'):
            service = QdrantRetrievalService()

            if args.command == 'retrieve-by-url':
                vectors, count = service.retrieve_by_url(
                    url=args.url,
                    limit=args.limit,
                    offset=args.offset
                )
                result = {
                    'vectors': [v.to_dict() for v in vectors],
                    'count': count
                }
                print(json.dumps(result, indent=2))

            elif args.command == 'retrieve-by-module':
                vectors, count = service.retrieve_by_module(
                    module=args.module,
                    limit=args.limit,
                    offset=args.offset
                )
                result = {
                    'vectors': [v.to_dict() for v in vectors],
                    'count': count
                }
                print(json.dumps(result, indent=2))

            elif args.command == 'retrieve-by-section':
                vectors, count = service.retrieve_by_section(
                    section=args.section,
                    limit=args.limit,
                    offset=args.offset
                )
                result = {
                    'vectors': [v.to_dict() for v in vectors],
                    'count': count
                }
                print(json.dumps(result, indent=2))

        elif args.command.startswith('validate-'):
            if args.command == 'validate-metadata':
                service = ValidationService()
                report = service.validate_metadata_integrity(
                    url=args.url,
                    module=args.module,
                    section=args.section
                )
                print(json.dumps(report.to_dict(), indent=2))

            elif args.command == 'validate-similarity':
                # First retrieve vectors, then run similarity validation
                retrieval_service = QdrantRetrievalService()

                if args.url:
                    vectors, _ = retrieval_service.retrieve_by_url(args.url)
                elif args.module:
                    vectors, _ = retrieval_service.retrieve_by_module(args.module)
                elif args.section:
                    vectors, _ = retrieval_service.retrieve_by_section(args.section)
                else:
                    print("Error: One of --url, --module, or --section must be provided", file=sys.stderr)
                    sys.exit(1)

                # Select random vectors for testing
                similarity_service = SimilarityService()
                selected_vectors = similarity_service.select_random_vectors_for_testing(vectors, args.count)

                # Run similarity validation
                results = similarity_service.run_similarity_validation(selected_vectors)
                print(json.dumps(results, indent=2))

            elif args.command == 'validate-comprehensive':
                service = ValidationService()
                report = service.validate_comprehensive(
                    url=args.url,
                    module=args.module,
                    section=args.section
                )
                print(json.dumps(report.to_dict(), indent=2))

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()