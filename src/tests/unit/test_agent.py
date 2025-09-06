"""
Unit tests for ReAct agent functionality.
"""

from unittest.mock import Mock, patch

from ai_agent.agent import ReActEngine, ReActStep


class TestReActEngine:
    """Test ReActEngine functionality."""

    def test_initialization(self, mock_config):
        """Test that ReActEngine initializes correctly."""
        with patch("ai_agent.agent.create_client") as mock_create:
            mock_create.return_value

            engine = ReActEngine(config=mock_config)

            assert engine.max_iterations == 3
            assert engine.timeout_seconds == 30
            assert hasattr(engine, "tool_registry")
            assert hasattr(engine, "trajectory_recorder")

    def test_execute_step_final_answer(self, react_engine):
        """Test executing a step that results in final answer."""
        # Start trajectory before executing step
        react_engine.trajectory_recorder.start("test")
        step = react_engine._execute_step(0, {"task": "test", "progress": ""})

        assert isinstance(step, ReActStep)
        assert step.action == "final_answer"
        assert "Test response" in step.result

    def test_is_task_complete(self, react_engine):
        """Test task completion detection."""
        # Test with final answer
        final_step = ReActStep(
            thought="test",
            action="final_answer",
            action_input={"answer": "test"},
            observation="test",
            result="test",
        )
        assert react_engine._is_task_complete(final_step, {"task": "test"})

        # Test with tool action
        tool_step = ReActStep(
            thought="test",
            action="calculator",
            action_input={"expression": "2+2"},
            observation="4",
            result="4",
        )
        assert not react_engine._is_task_complete(tool_step, {"task": "test"})

    def test_execute_action_with_tool(self, react_engine):
        """Test executing an action with a tool."""
        # Mock the tool registry
        mock_tool = Mock()
        mock_tool.execute.return_value = "4"
        react_engine.tool_registry.get_tool = Mock(return_value=mock_tool)

        action_decision = {
            "action": "calculator",
            "action_input": {"expression": "2+2"},
        }

        result = react_engine._execute_action(action_decision)

        assert result == "4"
        mock_tool.execute.assert_called_once_with(expression="2+2")

    def test_execute_action_tool_not_found(self, react_engine):
        """Test executing action with non-existent tool."""
        react_engine.tool_registry.get_tool = Mock(
            side_effect=ValueError("Tool not found")
        )

        action_decision = {
            "action": "nonexistent_tool",
            "action_input": {"param": "value"},
        }

        result = react_engine._execute_action(action_decision)

        assert "Error executing action" in result
        assert "Tool not found" in result

    def test_reset_functionality(self, react_engine):
        """Test agent reset functionality."""
        # Start trajectory before recording steps
        react_engine.trajectory_recorder.start("test")
        # Add some data to trajectory
        react_engine.trajectory_recorder.record_step(
            ReActStep(
                thought="test",
                action="test",
                action_input={},
                observation="test",
                result="test",
            )
        )

        # Verify data exists
        trajectory_before = react_engine.get_trajectory()
        assert len(trajectory_before.steps) > 0

        # Reset
        react_engine.reset()

        # Verify data is cleared (reset should return None for trajectory)
        trajectory_after = react_engine.get_trajectory()
        assert trajectory_after is None


class TestReActStep:
    """Test ReActStep dataclass."""

    def test_react_step_creation(self):
        """Test creating a ReActStep instance."""
        step = ReActStep(
            thought="I need to calculate 2+2",
            action="calculator",
            action_input={"expression": "2+2"},
            observation="4",
            result="4",
        )

        assert step.thought == "I need to calculate 2+2"
        assert step.action == "calculator"
        assert step.action_input == {"expression": "2+2"}
        assert step.observation == "4"
        assert step.result == "4"
