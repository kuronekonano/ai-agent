"""
Python code execution tool with safety restrictions.
Python代码执行工具（带有安全限制）
"""

import time
from typing import Any

from ..logger import get_logger
from .base import Tool

logger = get_logger(__name__)


class PythonCodeTool(Tool):
    """Tool for executing Python code with safety restrictions."""

    """Python代码执行工具（带有安全限制）"""

    def execute(self, **kwargs) -> Any:
        operation = kwargs.get("operation")
        logger.info(f"Executing Python code operation: {operation} with args: {kwargs}")

        start_time = time.time()
        success = True

        try:
            if operation == "execute":
                result = self._execute_code(kwargs["code"])
            elif operation == "evaluate":
                result = self._evaluate_expression(kwargs["expression"])
            else:
                logger.error(f"Unknown Python code operation: {operation}")
                raise ValueError(f"Unknown Python code operation: {operation}")

            logger.debug(f"Python code execution successful: {result}")
            return result
        except Exception as e:
            success = False
            logger.error(f"Python code execution error: {str(e)}")
            return f"Python code execution error: {str(e)}"
        finally:
            self._record_tool_usage(operation, start_time, success)

    def get_description(self) -> str:
        return "python_code: Execute Python code with safety restrictions - execute(code), evaluate(expression). \
WARNING: Code execution is restricted for security. Only basic Python operations are allowed. \
Prohibited: file I/O, network access, system calls, imports, and dangerous built-ins."

    def _execute_code(self, code: str) -> str:
        """Safely execute Python code with restricted environment."""
        """在受限环境中安全执行Python代码"""
        logger.debug(f"Executing Python code: {code}")

        # Security checks
        self._validate_code_safety(code)

        # Create restricted execution environment
        safe_globals = {
            "__builtins__": {
                "print": print,
                "len": len,
                "range": range,
                "list": list,
                "dict": dict,
                "set": set,
                "tuple": tuple,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "max": max,
                "min": min,
                "sum": sum,
                "abs": abs,
                "round": round,
                "sorted": sorted,
                "enumerate": enumerate,
                "zip": zip,
            }
        }

        safe_locals = {}

        try:
            # Execute the code
            exec(code, safe_globals, safe_locals)

            # Return any results from the execution
            if safe_locals:
                # Return the last variable created or a summary
                last_key = list(safe_locals.keys())[-1]
                result = safe_locals[last_key]
                return f"Code executed successfully. Result: {result}"
            else:
                return "Code executed successfully (no return value)"

        except Exception as e:
            logger.error(f"Error executing Python code: {str(e)}")
            raise ValueError(f"Error executing Python code: {str(e)}")

    def _evaluate_expression(self, expression: str) -> Any:
        """Safely evaluate a Python expression."""
        """安全评估Python表达式"""
        logger.debug(f"Evaluating Python expression: {expression}")

        # Security checks
        self._validate_code_safety(expression)

        # Create restricted execution environment
        safe_globals = {
            "__builtins__": {
                "abs": abs,
                "round": round,
                "min": min,
                "max": max,
                "sum": sum,
                "len": len,
            }
        }

        try:
            result = eval(expression, safe_globals, {})
            logger.debug(f"Expression evaluated: {expression} = {result}")
            return result
        except Exception as e:
            logger.error(f"Error evaluating expression: {str(e)}")
            raise ValueError(f"Error evaluating expression: {str(e)}")

    def _validate_code_safety(self, code: str) -> None:
        """Validate that the code doesn't contain dangerous operations."""
        """验证代码不包含危险操作"""
        dangerous_patterns = [
            "import",
            "from.*import",
            "open(",
            "exec(",
            "eval(",
            "__import__",
            "os.",
            "sys.",
            "subprocess.",
            "socket.",
            "requests.",
            "urllib.",
            "shutil.",
            "glob.",
            "re.",
            "pickle.",
            "marshal.",
            "ctypes.",
            "__builtins__",
            "__import__",
        ]

        for pattern in dangerous_patterns:
            if pattern in code:
                logger.error(f"Dangerous pattern detected in code: {pattern}")
                raise ValueError(f"Code contains prohibited pattern: {pattern}")

        # Additional checks for specific dangerous constructs
        if any(
            keyword in code
            for keyword in ["while True", "for.*:", "def ", "class ", "lambda "]
        ):
            logger.error("Complex code constructs not allowed")
            raise ValueError(
                "Complex code constructs (loops, functions, classes) are not allowed for security"
            )

        # Limit code length to prevent abuse
        if len(code) > 1000:
            logger.error("Code too long")
            raise ValueError("Code exceeds maximum length limit (1000 characters)")
