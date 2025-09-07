"""
Command line interface for agent evaluation framework.
"""

import argparse
import json

from .analyzer import Analyzer
from .cases.loader import load_test_cases
from .runner import run_suite


def run_suite_command(args):
    """Run a test suite."""
    print(f"Loading test cases from {args.suite_path}")

    try:
        test_cases = load_test_cases(args.suite_path)
        print(f"Loaded {len(test_cases)} test cases")

        # Run the test suite
        print(f"Running test suite with concurrency: {args.concurrency}")
        records = run_suite(
            test_cases=test_cases,
            concurrency=args.concurrency,
            storage_path=args.output,
        )

        # Analyze results
        analyzer = Analyzer()
        analysis = analyzer.analyze_records([r.to_dict() for r in records])

        # Generate report
        report = analyzer.generate_report(analysis, format="markdown")
        print("\n" + report)

        # Save report to file
        if args.output:
            report_path = f"{args.output}/report.md"
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"\nReport saved to: {report_path}")

            # Also save raw analysis JSON
            json_path = f"{args.output}/analysis.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            print(f"Raw analysis saved to: {json_path}")

        print(f"\nCompleted! Processed {len(records)} records")

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Agent Evaluation Framework")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Run suite command
    run_parser = subparsers.add_parser("run-suite", help="Run a test suite")
    run_parser.add_argument("suite_path", help="Path to test suite file (JSONL/JSON)")
    run_parser.add_argument(
        "--concurrency",
        "-c",
        type=int,
        default=8,
        help="Number of concurrent executions (default: 8)",
    )
    run_parser.add_argument("--output", "-o", help="Output directory for results")
    run_parser.set_defaults(func=run_suite_command)

    # Parse arguments
    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    exit(main())
