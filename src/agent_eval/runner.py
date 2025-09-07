"""
Async runner for agent evaluation framework.
Uses the existing ai_agent ReActEngine for execution.
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional

# Import from existing ai_agent framework
from ai_agent import ReActEngine

from .evaluator import create_scorer
from .schema import ExecutionRecord, RunMeta, TestCase, generate_run_id, now_iso
from .storage import BaseStore


class AgentRunner:
    """Runner that uses ai_agent's ReActEngine for test execution."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.concurrency = self.config.get("concurrency", 8)
        self.timeout_seconds = self.config.get("timeout_seconds", 30)

        # Initialize ai_agent ReActEngine
        ai_agent_config = self._create_ai_agent_config()
        self.engine = ReActEngine(ai_agent_config)

        # Thread pool for running sync ReActEngine
        self.executor = ThreadPoolExecutor(max_workers=self.concurrency)

    def _create_ai_agent_config(self) -> Dict[str, Any]:
        """Create ai_agent configuration from eval config."""
        model_config = self.config.get("model", {})

        return {
            "openai": {
                "api_key": "mock_key",  # Will use mock client
                "model": model_config.get("name", "gpt-3.5-turbo"),
                "temperature": model_config.get("temperature", 0.0),
                "max_tokens": model_config.get("max_tokens", 1000),
            },
            "agent": {
                "max_iterations": 5,
                "timeout_seconds": self.timeout_seconds,
            },
            "tools": {
                "enable_file_operations": False,  # Disable tools for evaluation
                "enable_calculator": False,
                "enable_web_search": False,
                "enable_python_code": False,
                "enable_memory_db": False,
            },
        }

    async def run_suite(
        self,
        test_cases: List[TestCase],
        run_meta: RunMeta,
        storage: BaseStore,
        scorer,
    ) -> List[ExecutionRecord]:
        """Run a suite of test cases using ai_agent ReActEngine."""
        records = []

        # Run cases with limited concurrency
        semaphore = asyncio.Semaphore(self.concurrency)

        async def run_case_with_semaphore(case: TestCase):
            async with semaphore:
                return await self._run_single_case(case, run_meta, storage, scorer)

        tasks = [run_case_with_semaphore(case) for case in test_cases]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Collect successful records
        for result in results:
            if isinstance(result, ExecutionRecord):
                records.append(result)
            elif isinstance(result, Exception):
                # Log the error but continue
                print(f"Case execution failed: {result}")

        return records

    async def _run_single_case(
        self,
        case: TestCase,
        run_meta: RunMeta,
        storage: BaseStore,
        scorer,
    ) -> ExecutionRecord:
        """Run a single test case and return execution record."""
        start_time = time.time()

        try:
            # Run the agent synchronously in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor, self.engine.run, case.prompt
            )

            # Get performance stats
            perf_stats = self.engine.get_performance_stats()

            # Create response structure
            response = {
                "text": result,
                "usage": perf_stats.get("total_token_usage", {}),
                "latency_ms": (time.time() - start_time) * 1000,
                "raw": {"result": result, "performance": perf_stats},
            }

            # Score the response
            scoring = scorer.score(
                {"expected": case.expected, "actual": result, "response": response}
            )

            # Create execution record
            record = ExecutionRecord(
                run_id=run_meta.run_id,
                test_case_id=case.id,
                prompt={"text": case.prompt, "meta": case.meta},
                response=response,
                scoring=scoring,
                status="success",
                created_at=now_iso(),
            )

            # Store the record
            storage.append(record.to_dict())

            return record

        except Exception as e:
            # Create error record
            error_record = ExecutionRecord(
                run_id=run_meta.run_id,
                test_case_id=case.id,
                prompt={"text": case.prompt, "meta": case.meta},
                response={
                    "error": str(e),
                    "latency_ms": (time.time() - start_time) * 1000,
                },
                scoring={"error": str(e)},
                status="error",
                error=str(e),
                created_at=now_iso(),
            )

            storage.append(error_record.to_dict())
            return error_record

    def close(self):
        """Clean up resources."""
        self.executor.shutdown()


def run_suite(
    test_cases: List[TestCase],
    model_config: Optional[Dict[str, Any]] = None,
    concurrency: int = 8,
    storage_path: Optional[str] = None,
) -> List[ExecutionRecord]:
    """Convenience function to run a test suite."""

    # Create configuration
    config = {
        "concurrency": concurrency,
        "model": model_config or {},
    }

    # Create components
    runner = AgentRunner(config)
    storage = BaseStore(storage_path)
    scorer = create_scorer("exact")  # Default exact match scorer

    # Create run metadata
    run_meta = RunMeta(
        run_id=generate_run_id(),
        test_suite_id="default_suite",
        model=config.get("model", {}),
        started_at=now_iso(),
    )

    # Run the suite
    loop = asyncio.get_event_loop()
    records = loop.run_until_complete(
        runner.run_suite(test_cases, run_meta, storage, scorer)
    )

    runner.close()
    return records
