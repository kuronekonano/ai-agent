#!/usr/bin/env python3
"""
Simple integration test for agent_eval using the simple runner.
使用简单运行器测试agent_eval的集成
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent_eval.cases.loader import load_test_cases
from agent_eval.simple_runner import run_suite_simple
from agent_eval.analyzer import Analyzer

def test_simple_integration():
    """Test agent_eval integration with simple runner."""
    print("Testing Agent Evaluation Framework with Simple Runner...")
    
    # Load test cases
    test_cases = load_test_cases("src/agent_eval/cases/sample_cases.jsonl")
    print(f"Loaded {len(test_cases)} test cases")
    
    # Run the test suite
    records = run_suite_simple(
        test_cases=test_cases,
        concurrency=4,
        storage_path="data/simple_test"
    )
    
    print(f"\nCompleted! Processed {len(records)} records")
    
    # Analyze results
    analyzer = Analyzer()
    analysis = analyzer.analyze_records([r.to_dict() for r in records])
    
    # Generate and print report
    report = analyzer.generate_report(analysis, format="markdown")
    print("\n" + report)
    
    # Save report
    os.makedirs("data/simple_test", exist_ok=True)
    with open("data/simple_test/simple_integration_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("Report saved to data/simple_test/simple_integration_report.md")
    
    return 0

if __name__ == "__main__":
    sys.exit(test_simple_integration())