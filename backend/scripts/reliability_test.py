#!/usr/bin/env python3
"""
Reliability validation script to measure 99% uptime over defined time window
"""
import argparse
import time
import json
import datetime
from typing import Dict, List
from src.services.qdrant_retrieval_service import QdrantRetrievalService


class UptimeMonitor:
    """Monitor system availability and track uptime metrics"""

    def __init__(self, test_url: str):
        self.test_url = test_url
        self.service = QdrantRetrievalService()
        self.checks: List[Dict] = []

    def perform_health_check(self) -> Dict:
        """Perform a single health check"""
        start_time = time.time()
        timestamp = datetime.datetime.now().isoformat()

        try:
            # Try to retrieve a known URL to test system availability
            vectors, count = self.service.retrieve_by_url(self.test_url, limit=1)
            success = True
            error = None
        except Exception as e:
            success = False
            error = str(e)

        end_time = time.time()
        response_time = end_time - start_time

        check_result = {
            'timestamp': timestamp,
            'success': success,
            'response_time': response_time,
            'error': error
        }

        self.checks.append(check_result)
        return check_result

    def get_uptime_stats(self) -> Dict:
        """Calculate uptime statistics from collected checks"""
        if not self.checks:
            return {
                'total_checks': 0,
                'successful_checks': 0,
                'failed_checks': 0,
                'uptime_percentage': 0.0,
                'target_met': False
            }

        successful_checks = [c for c in self.checks if c['success']]
        failed_checks = [c for c in self.checks if not c['success']]

        uptime_percentage = len(successful_checks) / len(self.checks) * 100

        return {
            'total_checks': len(self.checks),
            'successful_checks': len(successful_checks),
            'failed_checks': len(failed_checks),
            'uptime_percentage': uptime_percentage,
            'target_met': uptime_percentage >= 99.0,
            'time_window': {
                'start': self.checks[0]['timestamp'] if self.checks else None,
                'end': self.checks[-1]['timestamp'] if self.checks else None
            }
        }


def run_reliability_test(test_url: str, duration_minutes: int = 60, check_interval_seconds: int = 30) -> Dict:
    """Run reliability test for specified duration"""
    monitor = UptimeMonitor(test_url)

    print(f"Starting reliability test for {duration_minutes} minutes...")
    print(f"Checking every {check_interval_seconds} seconds using URL: {test_url}")

    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)  # Convert minutes to seconds

    check_count = 0
    while time.time() < end_time:
        check_result = monitor.perform_health_check()
        check_count += 1

        status = "UP" if check_result['success'] else "DOWN"
        print(f"Check #{check_count:3d}: {status} - {check_result['response_time']:.3f}s - {check_result['timestamp']}")

        # Wait for the next check interval (unless time is up)
        if time.time() + check_interval_seconds < end_time:
            time.sleep(check_interval_seconds)

    return monitor.get_uptime_stats()


def simulate_uptime_test(test_url: str, checks: int = 100, failure_rate: float = 0.01) -> Dict:
    """Simulate uptime test with configurable failure rate for testing purposes"""
    import random

    monitor = UptimeMonitor(test_url)

    print(f"Simulating reliability test with {checks} checks and {failure_rate*100:.1f}% failure rate...")

    for i in range(checks):
        # Simulate success/failure based on failure rate
        success = random.random() > failure_rate
        response_time = random.uniform(0.1, 2.0)  # Simulate response time between 0.1-2.0 seconds

        check_result = {
            'timestamp': datetime.datetime.now().isoformat(),
            'success': success,
            'response_time': response_time,
            'error': None if success else "Simulated failure"
        }

        monitor.checks.append(check_result)

        status = "UP" if success else "DOWN"
        print(f"Check #{i+1:3d}: {status} - {response_time:.3f}s")

    return monitor.get_uptime_stats()


def main():
    parser = argparse.ArgumentParser(description="Reliability validation: Measure 99% uptime over defined time window")
    parser.add_argument("--url", required=True, help="URL to test system availability")
    parser.add_argument("--duration", type=int, default=5, help="Test duration in minutes (default: 5, use --simulate for longer tests)")
    parser.add_argument("--interval", type=int, default=30, help="Check interval in seconds (default: 30)")
    parser.add_argument("--simulate", action='store_true', help="Run simulation instead of real test")
    parser.add_argument("--sim-checks", type=int, default=100, help="Number of checks for simulation (default: 100)")
    parser.add_argument("--sim-failure-rate", type=float, default=0.01, help="Failure rate for simulation (default: 0.01 = 1%)")
    parser.add_argument("--output", help="Output file for reliability report", default=None)

    args = parser.parse_args()

    if args.simulate:
        print("Running simulation mode...")
        metrics = simulate_uptime_test(args.url, args.sim_checks, args.sim_failure_rate)
    else:
        print(f"Running real reliability test for {args.duration} minutes...")
        print("Warning: This may take a while. Consider using --simulate for testing.")
        response = input("Continue? (y/N): ")
        if response.lower() != 'y':
            print("Test cancelled.")
            exit(0)

        metrics = run_reliability_test(args.url, args.duration, args.interval)

    # Print results
    print("\n" + "="*60)
    print("RELIABILITY TEST RESULTS")
    print("="*60)
    print(f"Total Checks: {metrics['total_checks']}")
    print(f"Successful: {metrics['successful_checks']}")
    print(f"Failed: {metrics['failed_checks']}")
    print(f"Uptime: {metrics['uptime_percentage']:.2f}%")
    print()

    if metrics['time_window']['start'] and metrics['time_window']['end']:
        print(f"Time Window: {metrics['time_window']['start']} to {metrics['time_window']['end']}")

    print()
    if metrics['target_met']:
        print("✅ RELIABILITY TEST PASSED: 99% uptime target achieved")
        exit_code = 0
    else:
        print("❌ RELIABILITY TEST FAILED: Less than 99% uptime achieved")
        exit_code = 1

    # Save report if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(metrics, f, indent=2)
        print(f"Reliability report saved to: {args.output}")

    exit(exit_code)


if __name__ == "__main__":
    main()