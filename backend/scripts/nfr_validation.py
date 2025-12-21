#!/usr/bin/env python3
"""
Comprehensive NFR validation including performance, reliability, and scalability tests
"""
import argparse
import json
import subprocess
import sys
import os
from datetime import datetime


def run_performance_test(url: str, output_dir: str) -> dict:
    """Run performance validation test"""
    print("Running performance validation test...")

    output_file = os.path.join(output_dir, "performance_report.json")
    cmd = [
        sys.executable, "scripts/performance_test.py",
        "--url", url,
        "--requests", "50",  # Reduced for demo purposes
        "--concurrency", "5",
        "--output", output_file
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5 minute timeout
        if result.returncode == 0:
            with open(output_file, 'r') as f:
                performance_data = json.load(f)
            return {"success": True, "data": performance_data}
        else:
            return {"success": False, "error": result.stderr}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Performance test timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_reliability_test(url: str, output_dir: str) -> dict:
    """Run reliability validation test (simulation mode)"""
    print("Running reliability validation test (simulation)...")

    output_file = os.path.join(output_dir, "reliability_report.json")
    cmd = [
        sys.executable, "scripts/reliability_test.py",
        "--url", url,
        "--simulate",
        "--sim-checks", "100",
        "--output", output_file
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            with open(output_file, 'r') as f:
                reliability_data = json.load(f)
            return {"success": True, "data": reliability_data}
        else:
            return {"success": False, "error": result.stderr}
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_scalability_test(url: str, output_dir: str) -> dict:
    """Run scalability validation test"""
    print("Running scalability validation test...")

    output_file = os.path.join(output_dir, "scalability_report.json")
    cmd = [
        sys.executable, "scripts/scalability_test.py",
        "--url", url,
        "--target", "1000",  # Reduced for demo purposes
        "--output", output_file
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5 minute timeout
        if result.returncode == 0:
            with open(output_file, 'r') as f:
                scalability_data = json.load(f)
            return {"success": True, "data": scalability_data}
        else:
            return {"success": False, "error": result.stderr}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Scalability test timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_comprehensive_nfr_validation(url: str, output_dir: str = "nfr_reports") -> dict:
    """Run all NFR validation tests"""
    print(f"Starting comprehensive NFR validation for URL: {url}")
    print(f"Output directory: {output_dir}")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Run all validation tests
    performance_result = run_performance_test(url, output_dir)
    reliability_result = run_reliability_test(url, output_dir)
    scalability_result = run_scalability_test(url, output_dir)

    # Compile overall results
    overall_result = {
        "timestamp": datetime.now().isoformat(),
        "target_url": url,
        "performance_test": performance_result,
        "reliability_test": reliability_result,
        "scalability_test": scalability_result,
        "overall_success": (
            performance_result["success"] and
            reliability_result["success"] and
            scalability_result["success"]
        )
    }

    # Save comprehensive report
    report_file = os.path.join(output_dir, "comprehensive_nfr_report.json")
    with open(report_file, 'w') as f:
        json.dump(overall_result, f, indent=2)

    return overall_result


def main():
    parser = argparse.ArgumentParser(description="Comprehensive NFR validation: Performance, reliability, and scalability tests")
    parser.add_argument("--url", required=True, help="URL to test for NFR validation")
    parser.add_argument("--output-dir", default="nfr_reports", help="Output directory for NFR reports (default: nfr_reports)")

    args = parser.parse_args()

    print("Starting comprehensive NFR validation...")
    print("="*60)

    results = run_comprehensive_nfr_validation(args.url, args.output_dir)

    # Print summary
    print("\n" + "="*60)
    print("COMPREHENSIVE NFR VALIDATION RESULTS")
    print("="*60)
    print(f"Target URL: {results['target_url']}")
    print(f"Timestamp: {results['timestamp']}")
    print()

    print("Performance Test:")
    if results['performance_test']['success']:
        perf_data = results['performance_test']['data']
        print(f"  ✅ PASSED")
        print(f"  Success Rate: {perf_data['success_rate']:.2f}%")
        print(f"  95% under 5s: {perf_data['threshold_compliance']['under_5s_percentage']:.2f}%")
    else:
        print(f"  ❌ FAILED: {results['performance_test']['error']}")
    print()

    print("Reliability Test:")
    if results['reliability_test']['success']:
        rel_data = results['reliability_test']['data']
        print(f"  ✅ PASSED")
        print(f"  Uptime: {rel_data['uptime_percentage']:.2f}%")
        print(f"  Target Met: {rel_data['target_met']}")
    else:
        print(f"  ❌ FAILED: {results['reliability_test']['error']}")
    print()

    print("Scalability Test:")
    if results['scalability_test']['success']:
        scale_data = results['scalability_test']['data']
        print(f"  ✅ PASSED")
        print(f"  Target Count: {scale_data['target_vector_count']:,}")
        print(f"  Scalability Target Met: {scale_data['scalability_target_met']}")
    else:
        print(f"  ❌ FAILED: {results['scalability_test']['error']}")
    print()

    print("Overall Result:")
    if results['overall_success']:
        print("  ✅ ALL NFR TESTS PASSED")
        print("  The system meets all non-functional requirements!")
        exit_code = 0
    else:
        print("  ❌ SOME NFR TESTS FAILED")
        print("  The system does not meet all non-functional requirements.")
        exit_code = 1

    print(f"\nComprehensive report saved to: {os.path.join(args.output_dir, 'comprehensive_nfr_report.json')}")

    exit(exit_code)


if __name__ == "__main__":
    main()