"""
Unit tests for tool functionality.
"""

import os
import tempfile
from unittest.mock import patch

import pytest

from ai_agent.tools import CalculatorTool, FileTool, ToolRegistry


class TestToolRegistry:
    """Test ToolRegistry functionality."""

    def test_register_and_get_tool(self):
        """Test registering and retrieving tools."""
        registry = ToolRegistry()
        calculator = CalculatorTool()

        registry.register_tool("calculator", calculator)

        retrieved_tool = registry.get_tool("calculator")
        assert retrieved_tool == calculator

        # Test getting non-existent tool
        with pytest.raises(ValueError, match="Tool not found"):
            registry.get_tool("nonexistent")

    def test_get_available_tools(self):
        """Test getting list of available tools."""
        registry = ToolRegistry()
        calculator = CalculatorTool()
        file_tool = FileTool()

        registry.register_tool("calculator", calculator)
        registry.register_tool("file", file_tool)

        available_tools = registry.get_available_tools()
        assert "calculator" in available_tools
        assert "file" in available_tools
        assert len(available_tools) == 2


class TestCalculatorTool:
    """Test CalculatorTool functionality."""

    def test_calculator_basic_operations(self):
        """Test basic arithmetic operations."""
        calculator = CalculatorTool()

        assert calculator.execute(operation="evaluate", expression="2 + 2") == 4
        assert calculator.execute(operation="evaluate", expression="10 - 5") == 5
        assert calculator.execute(operation="evaluate", expression="3 * 4") == 12
        assert calculator.execute(operation="evaluate", expression="15 / 3") == 5.0
        assert calculator.execute(operation="evaluate", expression="2 ** 3") == 8

    def test_calculator_complex_expressions(self):
        """Test complex mathematical expressions."""
        calculator = CalculatorTool()

        assert calculator.execute(operation="evaluate", expression="(2 + 3) * 4") == 20
        assert (
            calculator.execute(operation="evaluate", expression="2 + 3 * 4") == 14
        )  # Multiplication first
        # Note: sqrt and sin functions may not be supported in basic eval
        # These are just examples - actual implementation may vary
        assert calculator.execute(operation="evaluate", expression="16 ** 0.5") == 4.0

    def test_calculator_error_handling(self):
        """Test calculator error handling."""
        calculator = CalculatorTool()

        # Test division by zero
        result = calculator.execute(operation="evaluate", expression="1 / 0")
        assert "division by zero" in str(result).lower()

        # Test invalid expression
        result = calculator.execute(operation="evaluate", expression="2 + ")
        assert "invalid" in str(result).lower() or "error" in str(result).lower()


class TestFileTool:
    """Test FileTool functionality."""

    def test_file_read_write(self):
        """Test reading and writing files."""
        file_tool = FileTool()

        # Create a temporary file path without using NamedTemporaryFile
        # to avoid Windows file locking issues
        import tempfile
        import uuid
        
        tmp_dir = tempfile.gettempdir()
        tmp_path = os.path.join(tmp_dir, f"test_file_{uuid.uuid4().hex}.txt")

        try:
            # Test writing to file
            write_result = file_tool.execute(
                operation="write", path=tmp_path, content="Hello, World!"
            )
            assert "successfully" in write_result.lower()

            # Test reading from file
            read_result = file_tool.execute(operation="read", path=tmp_path)
            assert "Hello, World!" in read_result

        finally:
            # Clean up - try to remove file, but ignore errors if file is locked
            try:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            except (PermissionError, OSError):
                # File might be locked on Windows, this is acceptable for tests
                pass

    def test_file_read_nonexistent(self):
        """Test reading non-existent file."""
        file_tool = FileTool()

        # FileTool raises FileNotFoundError for non-existent files
        # This test expects the exception to be raised
        with pytest.raises(FileNotFoundError):
            file_tool.execute(operation="read", path="/nonexistent/file.txt")

    def test_file_invalid_action(self):
        """Test invalid file action."""
        file_tool = FileTool()

        # FileTool raises ValueError for invalid operations
        # This test expects the exception to be raised
        with pytest.raises(ValueError, match="Unknown file operation"):
            file_tool.execute(operation="invalid_action", path="/tmp/test.txt")

    def test_file_exists_operation(self):
        """Test file exists operation."""
        file_tool = FileTool()

        # Test with non-existent file
        result = file_tool.execute(operation="exists", path="/nonexistent/file.txt")
        assert result is False

        # Test with existing file (current directory)
        result = file_tool.execute(
            operation="exists", path=__file__  # This test file itself
        )
        assert result is True
