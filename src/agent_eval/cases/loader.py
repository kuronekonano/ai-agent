"""
Test case loader for agent evaluation framework.
代理评估框架的测试用例加载器
"""

import json
import os
from typing import Any, Dict, List

from ..schema import TestCase


class TestCaseLoader:
    """Loader for test cases in various formats.
    多种格式测试用例的加载器
    """

    def __init__(self):
        pass

    def load_from_jsonl(self, filepath: str) -> List[TestCase]:
        """Load test cases from JSONL file.
        从JSONL文件加载测试用例
        """
        test_cases = []

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Test case file not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    test_case = self._validate_and_create_case(data, line_num)
                    test_cases.append(test_case)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON on line {line_num}: {e}")

        return test_cases

    def load_from_file(self, filepath: str) -> List[TestCase]:
        """Load test cases from file based on extension.
        根据文件扩展名加载测试用例
        """
        ext = os.path.splitext(filepath)[1].lower()

        if ext == ".jsonl":
            return self.load_from_jsonl(filepath)
        elif ext == ".json":
            return self.load_from_json(filepath)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def load_from_json(self, filepath: str) -> List[TestCase]:
        """Load test cases from JSON array file.
        从JSON数组文件加载测试用例
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Test case file not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON: {e}")

        if not isinstance(data, list):
            raise ValueError("JSON file should contain an array of test cases")

        test_cases = []
        for i, item in enumerate(data):
            test_case = self._validate_and_create_case(item, i + 1)
            test_cases.append(test_case)

        return test_cases

    def _validate_and_create_case(
        self, data: Dict[str, Any], line_num: int
    ) -> TestCase:
        """Validate test case data and create TestCase object.
        验证测试用例数据并创建TestCase对象
        """
        if not isinstance(data, dict):
            raise ValueError(
                f"Line {line_num}: Expected object, got {type(data).__name__}"
            )

        if "id" not in data:
            raise ValueError(f"Line {line_num}: Missing required field 'id'")
        if "prompt" not in data:
            raise ValueError(f"Line {line_num}: Missing required field 'prompt'")

        # Ensure id and prompt are strings
        if not isinstance(data["id"], str):
            raise ValueError(f"Line {line_num}: 'id' must be a string")
        if not isinstance(data["prompt"], str):
            raise ValueError(f"Line {line_num}: 'prompt' must be a string")

        # Handle optional fields
        expected = data.get("expected")
        if expected is not None and not isinstance(expected, str):
            raise ValueError(
                f"Line {line_num}: 'expected' must be a string if provided"
            )

        meta = data.get("meta")
        if meta is not None and not isinstance(meta, dict):
            raise ValueError(f"Line {line_num}: 'meta' must be an object if provided")

        return TestCase(
            id=data["id"], prompt=data["prompt"], expected=expected, meta=meta
        )


def load_test_cases(filepath: str) -> List[TestCase]:
    """Convenience function to load test cases.
    加载测试用例的便捷函数
    """
    loader = TestCaseLoader()
    return loader.load_from_file(filepath)
