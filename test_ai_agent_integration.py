#!/usr/bin/env python3
"""
Integration test for agent_eval with ai_agent ReActEngine.
测试agent_eval与ai_agent ReActEngine的集成
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent_eval.cases.loader import load_test_cases
from agent_eval.client import MockModelClient
from agent_eval.evaluator import ExactMatchScorer
from agent_eval.schema import ExecutionRecord, now_iso
from agent_eval.analyzer import Analyzer

# Import ai_agent components
from ai_agent import ReActEngine
import asyncio

def create_mock_ai_agent_config():
    """Create mock configuration for ai_agent ReActEngine."""
    return {
        "openai": {
            "api_key": "mock_key",
            "model": "mock-model",
            "temperature": 0.0,
            "max_tokens": 1000,
        },
        "agent": {
            "max_iterations": 3,
            "timeout_seconds": 30,
        },
        "tools": {
            "enable_file_operations": False,
            "enable_calculator": False,
            "enable_web_search": False,
            "enable_python_code": False,
            "enable_memory_db": False,
        }
    }

async def test_ai_agent_integration():
    """Test integration with ai_agent ReActEngine."""
    print("Testing Agent Evaluation Framework with ai_agent ReActEngine...")
    
    # Load test cases
    test_cases = load_test_cases("src/agent_eval/cases/sample_cases.jsonl")
    print(f"Loaded {len(test_cases)} test cases")
    
    # Create ai_agent ReActEngine with mock config
    config = create_mock_ai_agent_config()
    engine = ReActEngine(config)
    
    # Create scorer
    scorer = ExactMatchScorer()
    
    records = []
    
    # Process each test case using ai_agent
    for case in test_cases:
        print(f"Processing case: {case.id}")
        
        try:
            # Use ai_agent ReActEngine to process the prompt
            result = engine.run(case.prompt)
            
            # Get performance stats
            perf_stats = engine.get_performance_stats()
            
            # Create response structure
            response = {
                "text": result,
                "usage": perf_stats.get("total_token_usage", {}),
                "latency_ms": 100,  # Mock latency
                "raw": {
                    "result": result,
                    "performance": perf_stats
                }
            }
            
            # Score the response
            scoring = scorer.score({
                "expected": case.expected,
                "actual": result,
                "response": response
            })
            
            # Create execution record
            record = ExecutionRecord(
                run_id="ai_agent-test-run-001",
                test_case_id=case.id,
                prompt={"text": case.prompt},
                response=response,
                scoring=scoring,
                status="success",
                created_at=now_iso()
            )
            
            records.append(record)
            print(f"  Score: {scoring['score']:.2f}")
            print(f"  Result: {result[:100]}...")
            
        except Exception as e:
            print(f"  Error: {e}")
            
            # Create error record
            error_record = ExecutionRecord(
                run_id="ai_agent-test-run-001",
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
    os.makedirs("data/ai_agent_test", exist_ok=True)
    with open("data/ai_agent_test/integration_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("Report saved to data/ai_agent_test/integration_report.md")
    
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(test_ai_agent_integration()))