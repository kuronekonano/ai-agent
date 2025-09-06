import os
import tempfile

import pytest

from src.ai_agent.tools import CalculatorTool, FileTool, ToolRegistry, WebSearchTool


class TestToolRegistry:

    def test_tool_registry_initialization(self):
        """Test tool registry initialization."""
        registry = ToolRegistry()
        assert registry.get_available_tools() == []

    def test_register_and_get_tool(self):
        """Test registering and retrieving a tool."""
        registry = ToolRegistry()
        tool = CalculatorTool()

        registry.register_tool("calculator", tool)
        assert registry.get_available_tools() == ["calculator"]
        assert registry.get_tool("calculator") == tool

    def test_get_nonexistent_tool(self):
        """Test getting a tool that doesn't exist."""
        registry = ToolRegistry()

        with pytest.raises(ValueError, match="Tool not found: calculator"):
            registry.get_tool("calculator")


class TestFileTool:

    def test_file_tool_description(self):
        """Test file tool description."""
        tool = FileTool()
        assert "file operations" in tool.get_description().lower()

    def test_file_read_write(self):
        """Test file read and write operations."""
        tool = FileTool()

        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as f:
            test_content = "Hello, World!"
            f.write(test_content)
            temp_path = f.name

        try:
            # Test read
            content = tool.execute(operation="read", path=temp_path)
            assert content == test_content

            # Test write
            new_content = "New content"
            result = tool.execute(
                operation="write", path=temp_path, content=new_content
            )
            assert "Successfully wrote" in result

            # Verify write
            content = tool.execute(operation="read", path=temp_path)
            assert content == new_content

        finally:
            os.unlink(temp_path)

    def test_file_list_directory(self):
        """Test directory listing."""
        tool = FileTool()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some test files
            test_files = ["test1.txt", "test2.txt"]
            for file_name in test_files:
                with open(os.path.join(temp_dir, file_name), "w") as f:
                    f.write("test")

            # Test list
            files = tool.execute(operation="list", path=temp_dir)
            assert all(file_name in files for file_name in test_files)

    def test_file_exists(self):
        """Test file existence check."""
        tool = FileTool()

        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name

        try:
            # Test exists
            exists = tool.execute(operation="exists", path=temp_path)
            assert exists == True

            # Test not exists
            not_exists = tool.execute(operation="exists", path="/nonexistent/path")
            assert not_exists == False

        finally:
            os.unlink(temp_path)

    def test_invalid_file_operation(self):
        """Test invalid file operation."""
        tool = FileTool()

        with pytest.raises(ValueError, match="Unknown file operation: invalid"):
            tool.execute(operation="invalid")


class TestCalculatorTool:

    def test_calculator_tool_description(self):
        """Test calculator tool description."""
        tool = CalculatorTool()
        assert "mathematical calculations" in tool.get_description().lower()

    def test_basic_operations(self):
        """Test basic arithmetic operations."""
        tool = CalculatorTool()

        assert tool.execute(operation="add", a=2, b=3) == 5
        assert tool.execute(operation="subtract", a=5, b=3) == 2
        assert tool.execute(operation="multiply", a=2, b=3) == 6
        assert tool.execute(operation="divide", a=6, b=3) == 2
        assert tool.execute(operation="power", base=2, exponent=3) == 8
        assert tool.execute(operation="sqrt", number=9) == 3

    def test_division_by_zero(self):
        """Test division by zero error."""
        tool = CalculatorTool()

        result = tool.execute(operation="divide", a=1, b=0)
        assert "Calculation error" in result

    def test_expression_evaluation(self):
        """Test expression evaluation."""
        tool = CalculatorTool()

        assert tool.execute(operation="evaluate", expression="2 + 3 * 4") == 14
        assert tool.execute(operation="evaluate", expression="(2 + 3) * 4") == 20

    def test_invalid_expression(self):
        """Test invalid expression evaluation."""
        tool = CalculatorTool()

        result = tool.execute(operation="evaluate", expression="2 + ")
        assert "Calculation error" in result

    def test_invalid_calculator_operation(self):
        """Test invalid calculator operation."""
        tool = CalculatorTool()

        with pytest.raises(ValueError, match="Unknown calculation operation: invalid"):
            tool.execute(operation="invalid")


class TestWebSearchTool:

    def test_web_search_tool_description(self):
        """Test web search tool description."""
        tool = WebSearchTool()
        assert "web search" in tool.get_description().lower()

    def test_web_search_placeholder(self):
        """Test web search placeholder functionality."""
        tool = WebSearchTool()

        result = tool.execute(query="test query")
        assert "would be performed here" in result
        assert "test query" in result

    def test_web_search_missing_query(self):
        """Test web search with missing query."""
        tool = WebSearchTool()

        with pytest.raises(ValueError, match="Search query is required"):
            tool.execute()
