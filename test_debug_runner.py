#!/usr/bin/env python3
"""
Debug runner to see what's happening.
调试运行器查看问题
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent_eval.cases.loader import load_test_cases
from agent_eval.client import MockModelClient
from agent_eval.evaluator import ExactMatchScorer
from agent_eval.schema import ExecutionRecord, now_iso
import asyncio

async def debug_runner():
    """Debug the runner step by step."""
    print("Debugging runner step by step...")
    
    # Load test cases
    test_cases = load_test_cases("src/agent_eval/cases/sample_cases.jsonl")
    print(f"Loaded {len(test_cases)} test cases")
    
    # Create client and scorer
    client = MockModelClient()
    scorer = ExactMatchScorer()
    
    # Test first case
    case = test_cases[0]
    print(f"\nTesting first case: {case.id}")
    print(f"Prompt: {case.prompt}")
    print(f"Expected: {case.expected}")
    
    try:
        # Test client call
        print("\n1. Testing client call...")
        response = await client.call(case.prompt)
        print(f"Client response: {response}")
        
        # Test scoring
        print("\n2. Testing scoring...")
        scoring = scorer.score({
            "expected": case.expected,
            "actual": response["text"],
            "response": response
        })
        print(f"Scoring result: {scoring}")
        
        # Test record creation
        print("\n3. Testing record creation...")
        record = ExecutionRecord(
            run_id="debug-run-001",
            test_case_id=case.id,
            prompt={"text": case.prompt},
            response=response,
            scoring=scoring,
            status="success",
            created_at=now_iso()
        )
        print(f"Record created: {record}")
        
        print("\nAll steps completed successfully!")
        return True
        
    except Exception as e:
        print(f"\nError occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_runner())
    sys.exit(0 if success else 1)