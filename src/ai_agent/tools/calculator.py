"""
Mathematical calculations tool.
数学计算工具
"""

import math
import time
from typing import Any

from ..logger import get_logger
from .base import Tool

logger = get_logger(__name__)


class CalculatorTool(Tool):
    """Tool for mathematical calculations."""

    """数学计算工具"""

    def execute(self, **kwargs) -> Any:
        operation = kwargs.get("operation")
        logger.info(f"Executing calculator operation: {operation} with args: {kwargs}")

        start_time = time.time()
        success = True

        try:
            if operation == "add":
                result = self._add(kwargs["a"], kwargs["b"])
            elif operation == "subtract":
                result = self._subtract(kwargs["a"], kwargs["b"])
            elif operation == "multiply":
                result = self._multiply(kwargs["a"], kwargs["b"])
            elif operation == "divide":
                result = self._divide(kwargs["a"], kwargs["b"])
            elif operation == "power":
                result = self._power(kwargs["base"], kwargs["exponent"])
            elif operation == "sqrt":
                result = self._sqrt(kwargs["number"])
            elif operation == "evaluate":
                result = self._evaluate_expression(kwargs["expression"])
            else:
                logger.error(f"Unknown calculation operation: {operation}")
                raise ValueError(f"Unknown calculation operation: {operation}")

            logger.debug(f"Calculation successful: {result}")
            return result
        except Exception as e:
            success = False
            logger.error(f"Calculation error: {str(e)}")
            return f"Calculation error: {str(e)}"
        finally:
            self._record_tool_usage(operation, start_time, success)

    def get_description(self) -> str:
        return "calculator: Perform mathematical calculations - add(a, b), subtract(a, b), multiply(a, b), divide(a, b), power(base, exponent), sqrt(number), evaluate(expression)"

    def _add(self, a: float, b: float) -> float:
        return a + b

    def _subtract(self, a: float, b: float) -> float:
        return a - b

    def _multiply(self, a: float, b: float) -> float:
        return a * b

    def _divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Division by zero")
        return a / b

    def _power(self, base: float, exponent: float) -> float:
        return base**exponent

    def _sqrt(self, number: float) -> float:
        if number < 0:
            raise ValueError("Cannot calculate square root of negative number")
        return math.sqrt(number)

    def _evaluate_expression(self, expression: str) -> float:
        """Safely evaluate a mathematical expression."""
        """安全评估数学表达式"""
        logger.debug(f"Evaluating expression: {expression}")
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in expression):
            logger.error("Expression contains invalid characters")
            raise ValueError("Expression contains invalid characters")

        try:
            result = eval(expression, {"__builtins__": {}}, {})
            logger.debug(f"Expression evaluated: {expression} = {result}")
            return result
        except Exception as e:
            logger.error(f"Error evaluating expression: {str(e)}")
            raise ValueError(f"Error evaluating expression: {str(e)}")
