"""Tests for script runner module.

Tests the universal script self-awareness functionality.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from truth_forge.core.script_runner import run_script_with_knowledge_capture


class TestRunScriptWithKnowledgeCapture:
    """Tests for run_script_with_knowledge_capture function."""

    def test_successful_script_execution(self) -> None:
        """Test running a successful script."""
        mock_governance = MagicMock()
        mock_knowledge = MagicMock()

        def mock_get_service(name: str) -> MagicMock:
            if name == "governance":
                return mock_governance
            elif name == "knowledge":
                return mock_knowledge
            raise ValueError(f"Unknown service: {name}")

        def sample_script() -> None:
            print("Hello from script")

        # Patch at source since import happens inside function
        with patch("truth_forge.services.factory.get_service", mock_get_service):
            with patch("sys.argv", ["test_script.py", "--arg1"]):
                run_script_with_knowledge_capture(sample_script)

        # Check governance was called with start event
        start_call = mock_governance.inhale.call_args_list[0]
        assert start_call[0][0]["event_type"] == "script_started"
        assert start_call[0][0]["script_name"] == "test_script.py"

        # Check governance was called with finish event
        finish_call = mock_governance.inhale.call_args_list[1]
        assert finish_call[0][0]["event_type"] == "script_finished"
        assert finish_call[0][0]["status"] == "success"

        # Check knowledge was called with output
        knowledge_call = mock_knowledge.inhale.call_args[0][0]
        assert "Hello from script" in knowledge_call["content"]
        assert knowledge_call["source"] == "script:test_script.py"
        assert knowledge_call["metadata"]["status"] == "success"

        # Check sync was called
        mock_knowledge.sync.assert_called_once()

    def test_failed_script_execution(self) -> None:
        """Test running a script that raises an exception."""
        mock_governance = MagicMock()
        mock_knowledge = MagicMock()

        def mock_get_service(name: str) -> MagicMock:
            if name == "governance":
                return mock_governance
            elif name == "knowledge":
                return mock_knowledge
            raise ValueError(f"Unknown service: {name}")

        def failing_script() -> None:
            raise ValueError("Script error")

        with patch("truth_forge.services.factory.get_service", mock_get_service):
            with patch("sys.argv", ["failing_script.py"]):
                with patch("sys.stderr"):  # Suppress stderr output
                    run_script_with_knowledge_capture(failing_script)

        # Check finish event has failed status
        finish_call = mock_governance.inhale.call_args_list[1]
        assert finish_call[0][0]["status"] == "failed"

        # Check knowledge has exception info
        knowledge_call = mock_knowledge.inhale.call_args[0][0]
        assert knowledge_call["metadata"]["status"] == "failed"
        assert knowledge_call["metadata"]["exception"] is not None
        assert "ValueError" in knowledge_call["metadata"]["exception"]

    def test_stdout_is_captured_and_restored(self) -> None:
        """Test that stdout is captured during script and restored after."""
        import sys

        original_stdout = sys.stdout
        mock_governance = MagicMock()
        mock_knowledge = MagicMock()

        def mock_get_service(name: str) -> MagicMock:
            if name == "governance":
                return mock_governance
            elif name == "knowledge":
                return mock_knowledge
            raise ValueError(f"Unknown service: {name}")

        def script_that_prints() -> None:
            print("Line 1")
            print("Line 2")

        with patch("truth_forge.services.factory.get_service", mock_get_service):
            with patch("sys.argv", ["print_script.py"]):
                run_script_with_knowledge_capture(script_that_prints)

        # stdout should be restored after execution
        assert sys.stdout == original_stdout

        # The knowledge service should have received the captured output
        knowledge_call = mock_knowledge.inhale.call_args[0][0]
        assert "Line 1" in knowledge_call["content"]
        assert "Line 2" in knowledge_call["content"]

    def test_script_args_are_captured(self) -> None:
        """Test that script arguments are captured in events."""
        mock_governance = MagicMock()
        mock_knowledge = MagicMock()

        def mock_get_service(name: str) -> MagicMock:
            if name == "governance":
                return mock_governance
            elif name == "knowledge":
                return mock_knowledge
            raise ValueError(f"Unknown service: {name}")

        def empty_script() -> None:
            pass

        with patch("truth_forge.services.factory.get_service", mock_get_service):
            with patch("sys.argv", ["script.py", "arg1", "--flag", "value"]):
                run_script_with_knowledge_capture(empty_script)

        # Check args were captured
        start_call = mock_governance.inhale.call_args_list[0]
        assert start_call[0][0]["args"] == ["arg1", "--flag", "value"]

        knowledge_call = mock_knowledge.inhale.call_args[0][0]
        assert knowledge_call["metadata"]["args"] == ["arg1", "--flag", "value"]

    def test_timestamp_is_included_in_events(self) -> None:
        """Test that timestamps are included in governance events."""
        mock_governance = MagicMock()
        mock_knowledge = MagicMock()

        def mock_get_service(name: str) -> MagicMock:
            if name == "governance":
                return mock_governance
            elif name == "knowledge":
                return mock_knowledge
            raise ValueError(f"Unknown service: {name}")

        def empty_script() -> None:
            pass

        with patch("truth_forge.services.factory.get_service", mock_get_service):
            with patch("sys.argv", ["script.py"]):
                run_script_with_knowledge_capture(empty_script)

        # Check timestamps are present
        start_call = mock_governance.inhale.call_args_list[0]
        assert "timestamp" in start_call[0][0]

        finish_call = mock_governance.inhale.call_args_list[1]
        assert "timestamp" in finish_call[0][0]

    def test_empty_output_script(self) -> None:
        """Test script that produces no output."""
        mock_governance = MagicMock()
        mock_knowledge = MagicMock()

        def mock_get_service(name: str) -> MagicMock:
            if name == "governance":
                return mock_governance
            elif name == "knowledge":
                return mock_knowledge
            raise ValueError(f"Unknown service: {name}")

        def silent_script() -> None:
            # Does nothing, produces no output
            x = 1 + 1  # noqa: F841

        with patch("truth_forge.services.factory.get_service", mock_get_service):
            with patch("sys.argv", ["silent.py"]):
                run_script_with_knowledge_capture(silent_script)

        # Knowledge should still be called with empty content
        knowledge_call = mock_knowledge.inhale.call_args[0][0]
        assert knowledge_call["content"] == ""
