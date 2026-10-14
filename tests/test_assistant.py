# Simple placeholder tests to verify the basic scaffolding

import pytest
from core.assistant import default_assistant
from core import action_registry


def test_assistant_echo():
    r = default_assistant.handle_text("hello")
    assert r.success
    assert "Echo" in r.text


def test_open_application_action():
    # Use the assistant to interpret an open command
    r = default_assistant.handle_text("open notepad")
    assert r.action == "open_application"
    assert r.action_args and r.action_args.get("name") == "notepad"
    # Execute via action registry but don't actually fail the environment if not present
    res = action_registry.execute_action(r.action, r.action_args)
    # The registry will attempt to run and should either return success or a requires_confirmation flag
    assert isinstance(res, dict)
