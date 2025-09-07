#!/usr/bin/env python3
"""
Simple test script for agent evaluation framework using mock client.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent_eval.cases.loader import load_test_cases
from agent_eval.client import MockModelClient
from agent_eval.evaluator import ExactMatchScorer
from agent_eval.schema import ExecutionRecord, now_iso
from agent_eval.analyzer import Analyzer

async def main():
    """Test the agent evaluation system with mock client."""
    print("Testing Agent Evaluation Framework with Mock Client...")
    
    # Load test cases
    test_cases = load_test_cases("src/agent_eval/cases/sample_cases.jsonl")
    print(f"Loaded {len(test_cases)} test cases")
    
    # Create mock client and scorer
    client = MockModelClient()
    scorer = ExactMatchScorer()
    
    records = []
    
    # Process each test case
    for case in test_cases:
        print(f"Processing case: {case.id}")
        
        try:
            # Mock API call
            response = await client.call(case.prompt)
            
            # Score the response
            scoring = scorer.score({
                "expected": case.expected,
                "actual": response["text"],
                "response": response
            })
            
            # Create execution record
            record = ExecutionRecord(
                run_id="test-run-001",
                test_case_id=case.id,
                prompt={"text": case.prompt},
                response=response,
                scoring=scoring,
                status="success",
                created_at=now_iso()
            )
            
            records.append(record)
            print(f"  Score: {scoring['score']:.2f}")
            
        except Exception as e:
            print(f"  Error: {e}")
            
            # Create error record
            error_record = ExecutionRecord(
                run_id="test-run-001",
                test_case_id=case.id,
                prompt={"text": case.prompt},
                response={"error": str(e)},
                scoring={"error": str(e)},
                status="error",
                error=str(e),
                created_at=now_iso()
            )
            
            records.append(error_record)
    
    print(f"\nCompleted! Processed {len(records)} records")
    
    # Analyze results
    analyzer = Analyzer()
    analysis = analyzer.analyze_records([r.to_dict() for r in records])
    
    # Generate and print report
    report = analyzer.generate_report(analysis, format="markdown")
    print("\n" + report)
    
    # Save report
    os.makedirs("data/eval_test", exist_ok=True)
    with open("data/eval_test/simple_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("Report saved to data/eval_test/simple_report.md")
    
    return 0

if __name__ == "__main__":
    import asyncio
    sys.exit(asyncio.run(main()))