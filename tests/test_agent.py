from unittest.mock import Mock, patch

import pytest

from src.ai_agent.agent import ReActEngine, ReActStep


class TestReActEngine:

    @pytest.fixture
    def mock_config(self):
        """Provide a mock configuration for testing."""
        return {
            "openai": {"api_key": "test_key", "model": "gpt-4"},
            "agent": {"max_iterations": 5, "timeout_seconds": 300},
            "tools": {
                "enable_file_operations": True,
                "enable_calculator": True,
                "enable_web_search": False,
            },
        }

    @patch("src.ai_agent.agent.create_client")
    def test_react_engine_initialization(self, mock_create_client, mock_config):
        """Test ReAct engine initialization."""
        mock_client = Mock()
        mock_create_client.return_value = mock_client

        engine = ReActEngine(mock_config)

        assert engine.max_iterations == 5
        assert engine.timeout_seconds == 300
        mock_create_client.assert_called_once_with(mock_config["openai"])

    @patch("src.ai_agent.agent.create_client")
    def test_setup_tools(self, mock_create_client, mock_config):
        """Test tool setup during initialization."""
        mock_client = Mock()
        mock_create_client.return_value = mock_client

        engine = ReActEngine(mock_config)

        available_tools = engine.tool_registry.get_available_tools()
        assert "file" in available_tools
        assert "calculator" in available_tools
        assert "web_search" not in available_tools

    @patch("src.ai_agent.agent.create_client")
    def test_execute_action_success(self, mock_create_client, mock_config):
        """Test successful action execution."""
        mock_client = Mock()
        mock_create_client.return_value = mock_client

        engine = ReActEngine(mock_config)

        # Mock the tool execution
        mock_tool = Mock()
        mock_tool.execute.return_value = "success"
        engine.tool_registry.register_tool("test_tool", mock_tool)

        action_decision = {"action": "test_tool", "action_input": {"param": "value"}}

        result = engine._execute_action(action_decision)
        assert result == "success"
        mock_tool.execute.assert_called_once_with(param="value")

    @patch("src.ai_agent.agent.create_client")
    def test_execute_action_error(self, mock_create_client, mock_config):
        """Test action execution with error."""
        mock_client = Mock()
        mock_create_client.return_value = mock_client

        engine = ReActEngine(mock_config)

        # Mock the tool to raise an exception
        mock_tool = Mock()
        mock_tool.execute.side_effect = Exception("Tool error")
        engine.tool_registry.register_tool("test_tool", mock_tool)

        action_decision = {"action": "test_tool", "action_input": {"param": "value"}}

        result = engine._execute_action(action_decision)
        assert "Error executing action" in result
        assert "Tool error" in result

    @patch("src.ai_agent.agent.create_client")
    def test_is_task_complete(self, mock_create_client, mock_config):
        """Test task completion detection."""
        mock_client = Mock()
        mock_create_client.return_value = mock_client

        engine = ReActEngine(mock_config)

        # Test with final answer
        final_step = ReActStep(
            thought="thought",
            action="final_answer",
            action_input={"answer": "result"},
            observation="obs",
            result="result",
        )
        assert engine._is_task_complete(final_step, {}) == True

        # Test with tool action
        tool_step = ReActStep(
            thought="thought",
            action="calculator",
            action_input={"operation": "add"},
            observation="obs",
            result="2",
        )
        assert engine._is_task_complete(tool_step, {}) == False


class TestReActStep:

    def test_react_step_creation(self):
        """Test ReActStep dataclass creation."""
        step = ReActStep(
            thought="test thought",
            action="test_action",
            action_input={"param": "value"},
            observation="test observation",
            result="test result",
            step_number=1,
        )

        assert step.thought == "test thought"
        assert step.action == "test_action"
        assert step.action_input == {"param": "value"}
        assert step.observation == "test observation"
        assert step.result == "test result"
        assert step.step_number == 1
