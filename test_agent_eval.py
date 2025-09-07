#!/usr/bin/env python3
"""
Test script for agent evaluation framework.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent_eval.cases.loader import load_test_cases
from agent_eval.runner import run_suite
from agent_eval.analyzer import Analyzer

def main():
    """Test the agent evaluation system."""
    print("Testing Agent Evaluation Framework...")
    
    # Load test cases
    test_cases = load_test_cases("src/agent_eval/cases/sample_cases.jsonl")
    print(f"Loaded {len(test_cases)} test cases")
    
    # Run the test suite
    print("Running test suite...")
    records = run_suite(
        test_cases=test_cases,
        concurrency=2,
        storage_path="data/eval_test"
    )
    
    print(f"Completed! Processed {len(records)} records")
    
    # Analyze results
    analyzer = Analyzer()
    analysis = analyzer.analyze_records([r.to_dict() for r in records])
    
    # Generate and print report
    report = analyzer.generate_report(analysis, format="markdown")
    print("\n" + report)
    
    # Save report
    os.makedirs("data/eval_test", exist_ok=True)
    with open("data/eval_test/report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("Report saved to data/eval_test/report.md")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())