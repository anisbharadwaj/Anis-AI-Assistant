# Simple placeholder tests to verify the basic scaffolding

import pytest
from core.assistant import default_assistant

def test_assistant_echo():
    r = default_assistant.handle_text("hello")
    assert r.success
    assert "hello" in r.text
