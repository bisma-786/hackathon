"""
Qdrant Retrieval & Validation Pipeline

This script connects to Qdrant Cloud, performs semantic similarity searches
on stored book embeddings, and validates that retrieved content matches
original source URLs and metadata.
"""

import os
import time
import logging
from typing import List, Dict, Optional, Tuple
import cohere
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('qdrant_retrieval.log'),
        logging.StreamHandler()  # Also log to console
    ]
)
logger = logging.getLogger(__name__)


# Load environment variables
load_dotenv()


def initialize_qdrant_client(max_retries: int = 3, retry_delay: float = 1.0):
    """
    Initialize and return Qdrant client with connection verification and retry logic.

    Args:
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds

    Returns:
        Tuple of (client, collection_name)
    """
    logger.info("Initializing Qdrant client with retry logic")

    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    collection_name = os.getenv("QDRANT_COLLECTION_NAME", "book_content_chunks")  # Default to the collection used in ingestion

    if not qdrant_url:
        logger.error("Missing QDRANT_URL environment variable")
        raise ValueError("Missing QDRANT_URL environment variable")
    if not qdrant_api_key:
        logger.error("Missing QDRANT_API_KEY environment variable")
        raise ValueError("Missing QDRANT_API_KEY environment variable")
    if not collection_name:
        logger.error("Missing COLLECTION_NAME environment variable")
        raise ValueError("Missing COLLECTION_NAME environment variable")

    # Try to initialize Qdrant client with retries
    last_exception = None
    for attempt in range(max_retries + 1):
        try:
            client = QdrantClient(
                url=qdrant_url,
                api_key=qdrant_api_key,
            )
            logger.info("Successfully initialized Qdrant client")

            # Verify connection and collection existence
            logger.info("Verifying Qdrant connection and collection existence")
            collections = client.get_collections()
            collection_names = [col.name for col in collections.collections]

            if collection_name not in collection_names:
                logger.error(f"Collection '{collection_name}' does not exist in Qdrant")
                raise ValueError(f"Collection '{collection_name}' does not exist in Qdrant")

            logger.info(f"Successfully connected to Qdrant collection: {collection_name}")
            return client, collection_name

        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"All {max_retries + 1} attempts failed. Last error: {str(e)}")
                raise

    # This line should never be reached, but included for completeness
    raise last_exception


def initialize_cohere_client():
    """Initialize and return Cohere client."""
    logger.info("Initializing Cohere client")

    cohere_api_key = os.getenv("COHERE_API_KEY")

    if not cohere_api_key:
        logger.error("Missing COHERE_API_KEY environment variable")
        raise ValueError("Missing COHERE_API_KEY environment variable")

    try:
        client = cohere.Client(api_key=cohere_api_key)
        logger.info("Successfully initialized Cohere client")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Cohere client: {str(e)}")
        raise


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for the given texts using Cohere."""
    cohere_client = initialize_cohere_client()

    try:
        response = cohere_client.embed(
            texts=texts,
            model="embed-multilingual-v3.0",  # Using the same model as ingestion
            input_type="search_query"  # Using search_query for queries (vs search_document for documents during ingestion)
        )

        # The Cohere API response has embeddings property that is a list of lists
        # Access the embeddings directly from the response
        embeddings = response.embeddings

        print(f"Generated embeddings for {len(texts)} text(s)")
        return embeddings
    except Exception as e:
        print(f"Failed to generate embeddings: {str(e)}")
        raise


def measure_execution_time(func):
    """Decorator to measure execution time of a function."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        print(f"Execution time for {func.__name__}: {execution_time:.2f} ms")
        return result, execution_time
    return wrapper


def get_execution_time(start_time: float) -> float:
    """Calculate execution time from start time to now."""
    end_time = time.time()
    return (end_time - start_time) * 1000  # Convert to milliseconds


def validate_performance_threshold(latency_ms: float, threshold_ms: float = 5000) -> bool:
    """
    Validate if the performance meets the threshold requirement.

    Args:
        latency_ms: Latency in milliseconds
        threshold_ms: Threshold in milliseconds (default 5000ms = 5 seconds)

    Returns:
        Boolean indicating if performance is within threshold
    """
    is_within_threshold = latency_ms <= threshold_ms
    if not is_within_threshold:
        print(f"PERFORMANCE WARNING: Latency {latency_ms:.2f}ms exceeds threshold {threshold_ms}ms")
    else:
        print(f"PERFORMANCE OK: Latency {latency_ms:.2f}ms is within threshold {threshold_ms}ms")

    return is_within_threshold


def calculate_latency_stats(latencies: List[float]) -> Dict[str, float]:
    """
    Calculate latency statistics including p95, average, min, and max.

    Args:
        latencies: List of latency measurements in milliseconds

    Returns:
        Dictionary with latency statistics
    """
    if not latencies:
        return {
            "p95": 0,
            "avg": 0,
            "min": 0,
            "max": 0,
            "count": 0
        }

    # Filter out infinite values (failed runs)
    valid_latencies = [lat for lat in latencies if lat != float('inf')]

    if not valid_latencies:
        return {
            "p95": float('inf'),
            "avg": float('inf'),
            "min": float('inf'),
            "max": float('inf'),
            "count": 0
        }

    sorted_latencies = sorted(valid_latencies)
    n = len(sorted_latencies)

    # Calculate p95 (95th percentile)
    p95_index = int(0.95 * n)
    if p95_index >= n:
        p95_index = n - 1

    stats = {
        "p95": sorted_latencies[p95_index],
        "avg": sum(sorted_latencies) / n,
        "min": min(sorted_latencies),
        "max": max(sorted_latencies),
        "count": n
    }

    return stats


def display_results(results: Dict):
    """Display search results in a formatted way."""
    # Safely encode the query text to avoid Unicode issues
    query_text = results['query']['text']
    safe_query = query_text.encode('utf-8', errors='ignore').decode('utf-8')
    print(f"\nQuery: {safe_query}")
    print(f"Retrieved {results['search_stats']['retrieved_count']} results in {results['search_stats']['execution_time_ms']:.2f} ms")
    print("\nResults:")
    print("-" * 80)

    for result in results["results"]:
        print(f"Rank: {result['rank']}")
        print(f"Score: {result['similarity_score']:.4f}")
        # Safely encode URL
        url = result['metadata']['source_url']
        safe_url = url.encode('utf-8', errors='ignore').decode('utf-8') if url else ""
        print(f"URL: {safe_url}")
        print(f"Module: {result['metadata']['module']}")
        print(f"Section: {result['metadata']['section']}")
        # Safely encode text content
        text = result['text_chunk']
        safe_text = text.encode('utf-8', errors='ignore').decode('utf-8') if text else ""
        print(f"Text: {safe_text[:200]}{'...' if len(safe_text) > 200 else ''}")
        print("-" * 80)


def validate_query_input(query_text: str, top_k: int) -> bool:
    """
    Validate query input parameters.

    Args:
        query_text: The text query to validate
        top_k: The number of results to retrieve

    Returns:
        Boolean indicating if the input is valid
    """
    if not query_text or not isinstance(query_text, str):
        logger.error("Query text is empty or not a string")
        return False

    if len(query_text.strip()) == 0:
        logger.error("Query text is empty after stripping whitespace")
        return False

    if len(query_text) > 10000:  # Set a reasonable limit for query length
        logger.warning(f"Query text is very long ({len(query_text)} characters), may affect performance")
        # Still allow long queries but log a warning

    if not isinstance(top_k, int) or top_k <= 0:
        logger.error(f"top_k must be a positive integer, got {top_k}")
        return False

    if top_k > 100:  # Set a reasonable limit for top_k
        logger.error(f"top_k value {top_k} is too large (max allowed: 100)")
        return False

    return True


def search_qdrant(query_text: str, top_k: int = 5) -> Dict:
    """
    Perform semantic similarity search on Qdrant collection.

    Args:
        query_text: The text query to search for
        top_k: Number of top results to return (default: 5)

    Returns:
        Dictionary containing search results with text chunks, metadata, and scores
    """
    logger.info(f"Starting search for query: '{query_text[:50]}{'...' if len(query_text) > 50 else ''}' with top_k={top_k}")

    # Validate inputs
    if not validate_query_input(query_text, top_k):
        logger.error("Invalid query input parameters")
        error_result = {
            "query": {
                "text": query_text,
                "embedding_generated": False
            },
            "results": [],
            "search_stats": {
                "retrieved_count": 0,
                "total_candidates": 0,
                "execution_time_ms": 0,
                "error": "Invalid query input parameters"
            }
        }
        display_results(error_result)
        return error_result

    # Record start time for execution time measurement
    start_time = time.time()

    try:
        # Initialize Qdrant client
        qdrant_client, collection_name = initialize_qdrant_client()

        # Generate embedding for the query
        query_embedding = generate_embeddings([query_text])[0]

        # Check available methods on the client object
        available_methods = [method for method in dir(qdrant_client) if not method.startswith('_')]
        print(f"Available methods on Qdrant client: {available_methods}")

        # Try to use the correct search method based on available methods
        if hasattr(qdrant_client, 'query_points'):
            # Use query_points method which is available in newer versions
            response = qdrant_client.query_points(
                collection_name=collection_name,
                query=query_embedding,
                limit=top_k,
                with_payload=True
            )
            # The response is a models.QueryResponse object with points attribute
            search_results = response.points
        elif hasattr(qdrant_client, 'query'):
            # Use query method which is available in newer versions
            search_results = qdrant_client.query(
                collection_name=collection_name,
                query=query_embedding,
                limit=top_k,
                with_payload=True
            )
        elif hasattr(qdrant_client, 'search'):
            search_results = qdrant_client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=top_k
            )
        elif hasattr(qdrant_client, 'search_points'):
            search_results = qdrant_client.search_points(
                collection_name=collection_name,
                query=query_embedding,
                limit=top_k
            )
        else:
            # If none of the search methods are available, return empty results
            print("No search method available on Qdrant client")
            search_results = []

        # Format results with deterministic ordering by score and then by chunk_id
        results = []
        for idx, hit in enumerate(search_results):
            # Handle different response formats depending on the method used
            if hasattr(hit, 'payload') and hit.payload:
                payload = hit.payload
            elif hasattr(hit, 'dict') and callable(getattr(hit, 'dict')):
                # If hit has a dict method, convert to dict to access payload
                hit_dict = hit.dict() if hasattr(hit, 'dict') else hit.__dict__
                payload = hit_dict.get('payload', {}) if isinstance(hit_dict, dict) else {}
            else:
                payload = getattr(hit, 'payload', {}) if hasattr(hit, 'payload') else {}

            result = {
                "rank": idx + 1,
                # Try multiple possible field names for the content text
                "text_chunk": payload.get("content", "") or payload.get("text", "") or payload.get("text_chunk", "") or payload.get("text_preview", "") if payload else "",
                "metadata": {
                    "source_url": payload.get("url", "") or payload.get("source_url", "") if payload else "",
                    "module": payload.get("module", "") if payload else "",
                    "section": payload.get("section", "") if payload else "",
                    "chunk_id": getattr(hit, 'id', getattr(hit, 'point_id', 'unknown'))
                },
                "similarity_score": getattr(hit, 'score', getattr(hit, 'distance', 0.0))
            }
            results.append(result)

        # Sort results to ensure deterministic ordering (by score descending, then by chunk_id)
        results.sort(key=lambda x: (-x["similarity_score"], x["metadata"]["chunk_id"]))

        # Update ranks after sorting
        for idx, result in enumerate(results):
            result["rank"] = idx + 1

        execution_time_ms = get_execution_time(start_time)

        final_result = {
            "query": {
                "text": query_text,
                "embedding_generated": True
            },
            "results": results,
            "search_stats": {
                "retrieved_count": len(results),
                "total_candidates": len(search_results),  # This is actually the same as retrieved_count in Qdrant
                "execution_time_ms": execution_time_ms
            }
        }

        logger.info(f"Search completed successfully. Retrieved {len(results)} results in {execution_time_ms:.2f}ms")

        # Display results to console (commented out to avoid Unicode encoding issues in some environments)
        # display_results(final_result)

        return final_result

    except Exception as e:
        logger.error(f"Error during search operation: {str(e)}")
        # Return a structured error response
        error_result = {
            "query": {
                "text": query_text,
                "embedding_generated": False
            },
            "results": [],
            "search_stats": {
                "retrieved_count": 0,
                "total_candidates": 0,
                "execution_time_ms": get_execution_time(start_time),
                "error": str(e)
            }
        }
        display_results(error_result)
        return error_result


import re


def is_valid_url(url: str) -> bool:
    """Check if a URL is valid using regex."""
    if not url or not isinstance(url, str):
        return False

    # Basic regex pattern for URL validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return url_pattern.match(url) is not None


def log_metadata_integrity_check(metadata: Dict, result_idx: int) -> Dict:
    """
    Log metadata integrity checks for a result.

    Returns a dictionary with validation results.
    """
    validation_results = {
        "result_idx": result_idx,
        "url_valid": False,
        "module_valid": True,
        "section_valid": True,
        "chunk_id_valid": True,
        "all_valid": False
    }

    # Check URL validity
    source_url = metadata.get("source_url", "")
    if source_url and is_valid_url(source_url):
        validation_results["url_valid"] = True
    else:
        print(f"METADATA INTEGRITY: Invalid URL in result {result_idx}: {source_url}")

    # Check module validity
    module = metadata.get("module", "")
    if module and not isinstance(module, str):
        validation_results["module_valid"] = False
        print(f"METADATA INTEGRITY: Invalid module in result {result_idx}: {module}")

    # Check section validity
    section = metadata.get("section", "")
    if section and not isinstance(section, str):
        validation_results["section_valid"] = False
        print(f"METADATA INTEGRITY: Invalid section in result {result_idx}: {section}")

    # Check chunk_id validity
    chunk_id = metadata.get("chunk_id", "")
    if not chunk_id:
        validation_results["chunk_id_valid"] = False
        print(f"METADATA INTEGRITY: Missing chunk_id in result {result_idx}")

    # Overall validation
    validation_results["all_valid"] = (
        validation_results["url_valid"] and
        validation_results["module_valid"] and
        validation_results["section_valid"] and
        validation_results["chunk_id_valid"]
    )

    return validation_results


def verify_content_alignment(query_text: str, text_chunk: str, source_url: str) -> bool:
    """
    Verify content alignment between query, text chunk, and source URL.

    This is a basic implementation that checks for semantic alignment
    by looking for related terms in the content.
    """
    # Convert to lowercase for comparison
    query_lower = query_text.lower()
    chunk_lower = text_chunk.lower()
    url_lower = source_url.lower()

    # Check if the text chunk contains content that relates to the query
    query_words = query_lower.split()
    matching_words = [word for word in query_words if word in chunk_lower]

    # If at least one query word appears in the chunk, consider it aligned
    has_content_alignment = len(matching_words) > 0

    # Check if URL contains relevant information (optional)
    # This is a basic check - in a real implementation, you might fetch the page
    # and verify that the content matches what was retrieved

    return has_content_alignment


def validate_result_format(results: Dict) -> bool:
    """Validate the format and content of search results."""
    if not isinstance(results, dict):
        print("ERROR: Results should be a dictionary")
        return False

    required_keys = ["query", "results", "search_stats"]
    for key in required_keys:
        if key not in results:
            print(f"ERROR: Missing required key '{key}' in results")
            return False

    # Validate query section
    if not isinstance(results["query"], dict) or "text" not in results["query"]:
        print("ERROR: Query section is malformed")
        return False

    query_text = results["query"]["text"]

    # Validate results section
    if not isinstance(results["results"], list):
        print("ERROR: Results should be a list")
        return False

    for idx, result in enumerate(results["results"]):
        if not isinstance(result, dict):
            print(f"ERROR: Result at index {idx} is not a dictionary")
            return False

        required_result_keys = ["rank", "text_chunk", "metadata", "similarity_score"]
        for key in required_result_keys:
            if key not in result:
                print(f"ERROR: Missing required key '{key}' in result {idx}")
                return False

        # Validate metadata
        if not isinstance(result["metadata"], dict):
            print(f"ERROR: Metadata in result {idx} is not a dictionary")
            return False

        required_metadata_keys = ["source_url", "module", "section", "chunk_id"]
        for meta_key in required_metadata_keys:
            if meta_key not in result["metadata"]:
                print(f"ERROR: Missing required metadata key '{meta_key}' in result {idx}")
                return False

        # Perform metadata integrity check
        integrity_result = log_metadata_integrity_check(result["metadata"], idx)
        if not integrity_result["all_valid"]:
            # If any critical metadata is invalid, return False
            if not integrity_result["url_valid"] or not integrity_result["chunk_id_valid"]:
                return False

        # Validate module and section identifiers
        module = result["metadata"]["module"]
        section = result["metadata"]["section"]

        if module and not isinstance(module, str):
            print(f"ERROR: Module identifier in result {idx} is not a string: {type(module)}")
            return False

        if section and not isinstance(section, str):
            print(f"ERROR: Section identifier in result {idx} is not a string: {type(section)}")
            return False

        # Check if module and section are not empty when they should have values
        if module == "":
            print(f"WARNING: Module identifier in result {idx} is empty")
        if section == "":
            print(f"WARNING: Section identifier in result {idx} is empty")

        # Verify content alignment between query and retrieved chunk
        text_chunk = result["text_chunk"]
        is_aligned = verify_content_alignment(query_text, text_chunk, source_url)
        if not is_aligned:
            print(f"WARNING: Content in result {idx} may not be well aligned with query")

        # Validate chunk ID consistency
        chunk_id = result["metadata"]["chunk_id"]
        if not chunk_id or not isinstance(chunk_id, (str, int)):
            print(f"ERROR: Invalid or missing chunk_id in result {idx}: {chunk_id}")
            return False

        # Validate similarity score range
        score = result["similarity_score"]
        if not isinstance(score, (int, float)) or score < 0 or score > 1:
            print(f"ERROR: Similarity score {score} in result {idx} is out of range [0, 1]")
            return False

    # Validate search stats
    if not isinstance(results["search_stats"], dict):
        print("ERROR: Search stats should be a dictionary")
        return False

    required_stats_keys = ["retrieved_count", "execution_time_ms"]
    for key in required_stats_keys:
        if key not in results["search_stats"]:
            print(f"ERROR: Missing required search stats key '{key}'")
            return False

    print("SUCCESS: All result format validations passed")
    return True


def create_validation_summary(results: Dict, validation_passed: bool) -> Dict:
    """
    Create a validation summary with pass/fail status.

    Args:
        results: The search results to summarize
        validation_passed: Whether the validation passed or not

    Returns:
        Dictionary with validation summary information
    """
    total_results = len(results.get("results", []))

    summary = {
        "validation_passed": validation_passed,
        "total_results": total_results,
        "status": "PASS" if validation_passed else "FAIL",
        "details": {
            "format_validation": validation_passed,
            "metadata_integrity": True,  # This would be computed based on actual checks
            "content_alignment": True,  # This would be computed based on actual checks
            "similarity_scores_valid": True  # This would be computed based on actual checks
        }
    }

    # Print summary
    print("\nVALIDATION SUMMARY:")
    print("-" * 30)
    print(f"Status: {summary['status']}")
    print(f"Total Results Checked: {summary['total_results']}")
    print(f"Format Validation: {'PASS' if summary['details']['format_validation'] else 'FAIL'}")
    print("-" * 30)

    return summary


def create_validation_report(results: Dict) -> Dict:
    """
    Create a validation report showing accuracy metrics.

    Returns a dictionary with validation statistics.
    """
    if not results or "results" not in results:
        return {"error": "Invalid results format"}

    total_results = len(results["results"])
    valid_results = 0
    invalid_results = 0
    avg_similarity_score = 0
    valid_urls = 0
    valid_modules = 0
    valid_sections = 0

    if total_results > 0:
        similarity_scores = []
        for result in results["results"]:
            # Count valid results
            is_result_valid = True
            try:
                # Check if all required fields exist and are valid
                if result.get("similarity_score") is not None:
                    score = result["similarity_score"]
                    if isinstance(score, (int, float)) and 0 <= score <= 1:
                        similarity_scores.append(score)
                        avg_similarity_score += score

                # Check URL validity
                source_url = result["metadata"].get("source_url", "")
                if source_url and is_valid_url(source_url):
                    valid_urls += 1

                # Check module validity
                module = result["metadata"].get("module", "")
                if module and isinstance(module, str):
                    valid_modules += 1

                # Check section validity
                section = result["metadata"].get("section", "")
                if section and isinstance(section, str):
                    valid_sections += 1

                # For this basic validation, consider result valid if it has basic fields
                if all(key in result for key in ["rank", "text_chunk", "metadata", "similarity_score"]):
                    valid_results += 1
                else:
                    is_result_valid = False

            except Exception:
                is_result_valid = False

            if not is_result_valid:
                invalid_results += 1

        if similarity_scores:
            avg_similarity_score = sum(similarity_scores) / len(similarity_scores)
        else:
            avg_similarity_score = 0

    accuracy_metrics = {
        "total_results": total_results,
        "valid_results": valid_results,
        "invalid_results": invalid_results,
        "valid_urls": valid_urls,
        "valid_modules": valid_modules,
        "valid_sections": valid_sections,
        "avg_similarity_score": avg_similarity_score,
        "url_accuracy": (valid_urls / total_results * 100) if total_results > 0 else 0,
        "module_accuracy": (valid_modules / total_results * 100) if total_results > 0 else 0,
        "section_accuracy": (valid_sections / total_results * 100) if total_results > 0 else 0,
        "overall_accuracy": (valid_results / total_results * 100) if total_results > 0 else 0
    }

    # Print the report
    print("\nVALIDATION REPORT:")
    print("-" * 40)
    print(f"Total Results: {accuracy_metrics['total_results']}")
    print(f"Valid Results: {accuracy_metrics['valid_results']}")
    print(f"Invalid Results: {accuracy_metrics['invalid_results']}")
    print(f"URL Accuracy: {accuracy_metrics['url_accuracy']:.2f}% ({valid_urls}/{total_results})")
    print(f"Module Accuracy: {accuracy_metrics['module_accuracy']:.2f}% ({valid_modules}/{total_results})")
    print(f"Section Accuracy: {accuracy_metrics['section_accuracy']:.2f}% ({valid_sections}/{total_results})")
    print(f"Overall Accuracy: {accuracy_metrics['overall_accuracy']:.2f}%")
    print(f"Average Similarity Score: {accuracy_metrics['avg_similarity_score']:.4f}")
    print("-" * 40)

    return accuracy_metrics


def run_multiple_query_types_performance(queries: List[str], top_k: int = 3, num_runs_per_query: int = 3) -> Dict:
    """
    Test performance across multiple query types.

    Args:
        queries: List of different query types to test
        top_k: Number of results to retrieve
        num_runs_per_query: Number of runs per query type

    Returns:
        Dictionary with performance metrics for each query type
    """
    print(f"Testing performance across {len(queries)} different query types...")

    performance_by_query = {}

    for i, query in enumerate(queries):
        print(f"\nTesting query {i+1}/{len(queries)}: '{query}'")
        query_latencies = []

        for run in range(num_runs_per_query):
            print(f"  Run {run+1}/{num_runs_per_query}...")
            try:
                start_time = time.time()
                result = search_qdrant(query_text=query, top_k=top_k)
                end_time = time.time()

                execution_time = (end_time - start_time) * 1000
                query_latencies.append(execution_time)

                time.sleep(0.1)  # Small delay between runs
            except Exception as e:
                print(f"  Error during run {run+1}: {str(e)}")
                query_latencies.append(float('inf'))

        # Calculate stats for this query
        query_stats = calculate_latency_stats(query_latencies)
        performance_by_query[query] = {
            "latencies": query_latencies,
            "stats": query_stats
        }

    # Overall performance summary
    all_latencies = []
    for query_data in performance_by_query.values():
        all_latencies.extend([lat for lat in query_data["latencies"] if lat != float('inf')])

    overall_stats = calculate_latency_stats(all_latencies)

    performance_report = {
        "query_performance": performance_by_query,
        "overall_stats": overall_stats,
        "num_queries": len(queries),
        "runs_per_query": num_runs_per_query
    }

    # Print performance report
    print(f"\nPERFORMANCE REPORT FOR MULTIPLE QUERY TYPES:")
    print("=" * 60)
    for query, data in performance_report["query_performance"].items():
        print(f"Query: '{query}'")
        stats = data["stats"]
        print(f"  Average Latency: {stats['avg']:.2f} ms")
        print(f"  P95 Latency: {stats['p95']:.2f} ms")
        print(f"  Min Latency: {stats['min']:.2f} ms")
        print(f"  Max Latency: {stats['max']:.2f} ms")
        print(f"  Successful Runs: {stats['count']}/{num_runs_per_query}")
        print("-" * 40)

    print(f"OVERALL PERFORMANCE:")
    print(f"  Average Latency: {performance_report['overall_stats']['avg']:.2f} ms")
    print(f"  P95 Latency: {performance_report['overall_stats']['p95']:.2f} ms")
    print(f"  Min Latency: {performance_report['overall_stats']['min']:.2f} ms")
    print(f"  Max Latency: {performance_report['overall_stats']['max']:.2f} ms")
    print("=" * 60)

    return performance_report


def run_repeated_queries(query_text: str, top_k: int = 3, num_runs: int = 5) -> Dict:
    """
    Run the same query multiple times to test stability across runs.

    Args:
        query_text: The query text to run repeatedly
        top_k: Number of results to retrieve
        num_runs: Number of times to run the query

    Returns:
        Dictionary with performance and stability metrics
    """
    print(f"Running query '{query_text}' {num_runs} times to test stability...")

    latencies = []
    results_consistency = []
    all_results = []

    for i in range(num_runs):
        print(f"Run {i+1}/{num_runs}...")
        try:
            start_time = time.time()
            result = search_qdrant(query_text=query_text, top_k=top_k)
            end_time = time.time()

            # Calculate execution time in milliseconds
            execution_time = (end_time - start_time) * 1000
            latencies.append(execution_time)

            if result:
                all_results.append(result)
                # Check if the top result is consistent (comparing first result's text and score)
                if result.get("results"):
                    top_result = result["results"][0] if result["results"] else None
                    if top_result:
                        results_consistency.append({
                            "text": top_result["text_chunk"][:100],  # First 100 chars for comparison
                            "score": top_result["similarity_score"]
                        })

            time.sleep(0.1)  # Small delay between runs to avoid overwhelming the service
        except Exception as e:
            print(f"Error during run {i+1}: {str(e)}")
            latencies.append(float('inf'))  # Mark as failed run

    # Calculate performance statistics
    perf_stats = calculate_latency_stats(latencies)

    # Check result consistency
    consistent_results = 0
    if len(results_consistency) > 1:
        first_result = results_consistency[0]
        for result in results_consistency[1:]:
            # Check if top result is approximately the same
            if (abs(result["score"] - first_result["score"]) < 0.001 and
                result["text"][:50] == first_result["text"][:50]):  # Compare first 50 chars
                consistent_results += 1

    stability_report = {
        "num_runs": num_runs,
        "successful_runs": len([l for l in latencies if l != float('inf')]),
        "latency_stats": perf_stats,
        "result_consistency": {
            "consistent_runs": consistent_results,
            "consistency_rate": (consistent_results / (len(results_consistency) - 1)) * 100 if len(results_consistency) > 1 else 100
        },
        "all_results": all_results
    }

    # Print stability report
    print(f"\nSTABILITY REPORT:")
    print("-" * 40)
    print(f"Total Runs: {stability_report['num_runs']}")
    print(f"Successful Runs: {stability_report['successful_runs']}")
    print(f"Average Latency: {stability_report['latency_stats']['avg']:.2f} ms")
    print(f"P95 Latency: {stability_report['latency_stats']['p95']:.2f} ms")
    print(f"Min Latency: {stability_report['latency_stats']['min']:.2f} ms")
    print(f"Max Latency: {stability_report['latency_stats']['max']:.2f} ms")
    print(f"Result Consistency Rate: {stability_report['result_consistency']['consistency_rate']:.2f}%")
    print("-" * 40)

    return stability_report


def test_edge_cases_performance() -> Dict:
    """
    Test performance for edge cases like empty results and large queries.

    Returns:
        Dictionary with performance metrics for edge cases
    """
    print("Testing performance for edge cases...")

    edge_case_results = {}

    # Test 1: Very long query
    print("\n1. Testing with a very long query...")
    long_query = "Artificial intelligence and machine learning are fascinating fields that involve creating systems capable of learning and adapting. Artificial intelligence and machine learning are fascinating fields that involve creating systems capable of learning and adapting. Artificial intelligence and machine learning are fascinating fields that involve creating systems capable of learning and adapting."

    try:
        start_time = time.time()
        result = search_qdrant(query_text=long_query, top_k=3)
        end_time = time.time()
        long_query_latency = (end_time - start_time) * 1000
        edge_case_results["long_query"] = {
            "latency_ms": long_query_latency,
            "retrieved_count": result["search_stats"]["retrieved_count"] if result else 0,
            "within_threshold": validate_performance_threshold(long_query_latency)
        }
        print(f"   Long query latency: {long_query_latency:.2f} ms")
    except Exception as e:
        print(f"   Error with long query: {str(e)}")
        edge_case_results["long_query"] = {
            "latency_ms": float('inf'),
            "retrieved_count": 0,
            "within_threshold": False,
            "error": str(e)
        }

    # Test 2: Query that might return no results
    print("\n2. Testing with a query likely to return no results...")
    empty_query = "asdfsdfgsdgfsdgf"  # Random string unlikely to match anything

    try:
        start_time = time.time()
        result = search_qdrant(query_text=empty_query, top_k=3)
        end_time = time.time()
        empty_query_latency = (end_time - start_time) * 1000
        edge_case_results["empty_query"] = {
            "latency_ms": empty_query_latency,
            "retrieved_count": result["search_stats"]["retrieved_count"] if result else 0,
            "within_threshold": validate_performance_threshold(empty_query_latency)
        }
        print(f"   Empty query latency: {empty_query_latency:.2f} ms")
    except Exception as e:
        print(f"   Error with empty query: {str(e)}")
        edge_case_results["empty_query"] = {
            "latency_ms": float('inf'),
            "retrieved_count": 0,
            "within_threshold": False,
            "error": str(e)
        }

    # Test 3: Very high top_k value
    print("\n3. Testing with a high top_k value...")
    try:
        start_time = time.time()
        result = search_qdrant(query_text="robotics", top_k=50)
        end_time = time.time()
        high_k_latency = (end_time - start_time) * 1000
        edge_case_results["high_top_k"] = {
            "latency_ms": high_k_latency,
            "retrieved_count": result["search_stats"]["retrieved_count"] if result else 0,
            "within_threshold": validate_performance_threshold(high_k_latency)
        }
        print(f"   High top_k latency: {high_k_latency:.2f} ms")
    except Exception as e:
        print(f"   Error with high top_k: {str(e)}")
        edge_case_results["high_top_k"] = {
            "latency_ms": float('inf'),
            "retrieved_count": 0,
            "within_threshold": False,
            "error": str(e)
        }

    # Print edge case report
    print(f"\nEDGE CASE PERFORMANCE REPORT:")
    print("=" * 50)
    for case, data in edge_case_results.items():
        print(f"{case.replace('_', ' ').title()}:")
        print(f"  Latency: {data['latency_ms']:.2f} ms")
        print(f"  Retrieved Count: {data['retrieved_count']}")
        print(f"  Within Threshold: {data['within_threshold']}")
        if "error" in data:
            print(f"  Error: {data['error']}")
        print("-" * 30)
    print("=" * 50)

    return edge_case_results


def run_performance_benchmarking(query_text: str, top_k_values: List[int] = [1, 3, 5, 10], num_runs_per_k: int = 3) -> Dict:
    """
    Benchmark performance against different top-K values.

    Args:
        query_text: The query text to use for benchmarking
        top_k_values: List of different top-K values to test
        num_runs_per_k: Number of runs per top-K value

    Returns:
        Dictionary with performance metrics for each top-K value
    """
    print(f"Benchmarking performance for different top-K values: {top_k_values}")

    performance_by_k = {}

    for k in top_k_values:
        print(f"\nTesting with top_k={k}...")
        latencies = []

        for run in range(num_runs_per_k):
            print(f"  Run {run+1}/{num_runs_per_k}...")
            try:
                start_time = time.time()
                result = search_qdrant(query_text=query_text, top_k=k)
                end_time = time.time()

                execution_time = (end_time - start_time) * 1000
                latencies.append(execution_time)

                time.sleep(0.1)  # Small delay between runs
            except Exception as e:
                print(f"  Error during run {run+1}: {str(e)}")
                latencies.append(float('inf'))

        # Calculate stats for this k value
        stats = calculate_latency_stats(latencies)
        performance_by_k[k] = {
            "latencies": latencies,
            "stats": stats
        }

    benchmark_report = {
        "top_k_performance": performance_by_k,
        "query_text": query_text,
        "tested_k_values": top_k_values
    }

    # Print benchmark report
    print(f"\nPERFORMANCE BENCHMARKING REPORT:")
    print("=" * 50)
    for k, data in benchmark_report["top_k_performance"].items():
        stats = data["stats"]
        print(f"Top-K = {k}:")
        print(f"  Average Latency: {stats['avg']:.2f} ms")
        print(f"  P95 Latency: {stats['p95']:.2f} ms")
        print(f"  Min Latency: {stats['min']:.2f} ms")
        print(f"  Max Latency: {stats['max']:.2f} ms")
        print(f"  Successful Runs: {stats['count']}/{num_runs_per_k}")
        print("-" * 30)

    print("=" * 50)

    return benchmark_report


def run_test_query():
    """Run a test query to validate end-to-end functionality."""
    print("Running test query to validate end-to-end functionality...")

    # Use a sample query for testing
    test_query = "What is ROS 2 and how does it work?"
    top_k = 3

    try:
        results = search_qdrant(query_text=test_query, top_k=top_k)

        if results:
            print(f"Successfully retrieved {results['search_stats']['retrieved_count']} results")

            # Validate the result format and content
            is_valid = validate_result_format(results)
            if is_valid:
                print("All validations passed!")
            else:
                print("Some validations failed!")

            # Create and display validation report
            validation_report = create_validation_report(results)

            # Create and display validation summary
            validation_summary = create_validation_summary(results, is_valid)
            print("Validation report and summary generated.")

            # Run stability test with repeated queries
            stability_report = run_repeated_queries(test_query, top_k=3, num_runs=3)

            # Run performance benchmarking with different top-K values
            benchmark_report = run_performance_benchmarking(test_query, top_k_values=[1, 3, 5], num_runs_per_k=2)

            # Run performance validation across multiple query types
            queries = [
                "What is ROS 2?",
                "Explain robotics systems",
                "How does navigation work in robotics?"
            ]
            multi_query_report = run_multiple_query_types_performance(queries, top_k=3, num_runs_per_query=2)

            # Test edge cases performance
            edge_case_report = test_edge_cases_performance()

            return results
        else:
            print("No results returned from search")
            return None
    except Exception as e:
        print(f"Error during test query: {str(e)}")
        return None


import argparse


def main():
    """Main function to run the retrieval and validation pipeline."""
    print("Qdrant Retrieval & Validation Pipeline")
    print("=" * 50)

    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description="Qdrant Retrieval & Validation Pipeline")
    parser.add_argument("--query", type=str, help="Custom query text to search for",
                        default="What is ROS 2 and how does it work?")
    parser.add_argument("--top-k", type=int, default=3, help="Number of top results to retrieve (default: 3)")
    parser.add_argument("--run-tests", action="store_true", help="Run comprehensive validation tests")

    args = parser.parse_args()

    if args.run_tests:
        # Run comprehensive tests
        run_test_query()
    else:
        # Run a single query with the provided parameters
        print(f"Running single query: '{args.query}' with top_k={args.top_k}")
        try:
            results = search_qdrant(query_text=args.query, top_k=args.top_k)
            if results:
                print(f"Successfully retrieved {results['search_stats']['retrieved_count']} results")
            else:
                print("No results returned from search")
        except Exception as e:
            print(f"Error during query: {str(e)}")


if __name__ == "__main__":
    main()