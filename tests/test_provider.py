# AI provider tests
import os
from ai import provider as provider_mod


def test_default_provider_is_mock(monkeypatch):
    monkeypatch.delenv("AI_PROVIDER", raising=False)
    p = provider_mod.get_provider()
    assert p.__class__.__name__ == "MockProvider"


def test_select_local_provider(monkeypatch, tmp_path):
    monkeypatch.setenv("AI_PROVIDER", "local")
    # no local model path set -> local provider fallback
    p = provider_mod.get_provider()
    assert p.__class__.__name__ in ("LocalProvider", "MockProvider")


def test_mock_interpret():
    p = provider_mod.MockProvider()
    r = p.interpret("open notepad")
    assert r.get("type") == "action"
    assert r.get("action_id") == "open_application"
