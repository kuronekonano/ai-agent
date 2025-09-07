"""
Simple runner for agent evaluation framework.
Uses MockModelClient directly for reliable testing.
简单运行器，直接使用MockModelClient进行可靠测试
"""

import asyncio
import time
from typing import Any, Dict, List, Optional

from .client import MockModelClient
from .evaluator import create_scorer
from .schema import ExecutionRecord, RunMeta, TestCase, generate_run_id, now_iso
from .storage import JSONLStore


class SimpleRunner:
    """Simple runner that uses MockModelClient directly.
    直接使用MockModelClient的简单运行器
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.concurrency = self.config.get("concurrency", 8)
        self.timeout_seconds = self.config.get("timeout_seconds", 30)

        # Use our MockModelClient directly
        self.client = MockModelClient(self.config.get("model", {}))

    async def run_suite(
        self,
        test_cases: List[TestCase],
        run_meta: RunMeta,
        storage: JSONLStore,
        scorer,
    ) -> List[ExecutionRecord]:
        """Run a suite of test cases using MockModelClient.
        使用MockModelClient运行测试套件
        """
        records = []

        # Run cases with limited concurrency
        semaphore = asyncio.Semaphore(self.concurrency)

        async def run_case_with_semaphore(case: TestCase):
            async with semaphore:
                return await self._run_single_case(case, run_meta, storage, scorer)

        tasks = [run_case_with_semaphore(case) for case in test_cases]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Collect successful records
        for i, result in enumerate(results):
            if isinstance(result, ExecutionRecord):
                records.append(result)
            elif isinstance(result, Exception):
                # Log the error but continue
                print(f"Case {i} execution failed: {result}")
                import traceback

                traceback.print_exception(type(result), result, result.__traceback__)

        return records

    async def _run_single_case(
        self,
        case: TestCase,
        run_meta: RunMeta,
        storage: JSONLStore,
        scorer,
    ) -> ExecutionRecord:
        """Run a single test case and return execution record.
        运行单个测试用例并返回执行记录
        """
        start_time = time.time()

        try:
            # Use our MockModelClient directly
            response = await self.client.call(case.prompt)

            # Score the response
            scoring = scorer.score(
                {
                    "expected": case.expected,
                    "actual": response["text"],
                    "response": response,
                }
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


def run_suite_simple(
    test_cases: List[TestCase],
    model_config: Optional[Dict[str, Any]] = None,
    concurrency: int = 8,
    storage_path: Optional[str] = None,
) -> List[ExecutionRecord]:
    """Convenience function to run a test suite with simple runner.
    使用简单运行器运行测试套件的便捷函数
    """

    # Create configuration
    config = {
        "concurrency": concurrency,
        "model": model_config or {},
    }

    # Create components
    runner = SimpleRunner(config)
    storage = JSONLStore(storage_path)
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

    return records
