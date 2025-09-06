#!/usr/bin/env python3
"""
Test runner script for AI Agent Framework.
Run specific test categories or all tests.
"""

import argparse
import os
import subprocess
import sys


def run_tests(test_path=None, verbose=False, coverage=False):
    """Run tests using pytest."""
    cmd = ["pytest", "-v" if verbose else "--tb=short"]

    if coverage:
        cmd.extend(["--cov=ai_agent", "--cov-report=term-missing"])

    if test_path:
        cmd.append(test_path)
    else:
        cmd.append("tests/")

    # Add current directory to Python path
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print(f"Running command: {' '.join(cmd)}")
    print(f"Python path: {env['PYTHONPATH']}")
    print("=" * 60)

    result = subprocess.run(cmd, env=env, cwd=os.path.dirname(__file__))
    return result.returncode


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(description="Run AI Agent Framework tests")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument(
        "--integration", action="store_true", help="Run only integration tests"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--coverage", "-c", action="store_true", help="Generate coverage report"
    )
    parser.add_argument("--test", "-t", help="Run specific test file or test function")

    args = parser.parse_args()

    test_path = None
    if args.unit:
        test_path = "tests/unit/"
    elif args.integration:
        test_path = "tests/integration/"
    elif args.test:
        test_path = args.test

    return run_tests(test_path, args.verbose, args.coverage)


if __name__ == "__main__":
    sys.exit(main())
