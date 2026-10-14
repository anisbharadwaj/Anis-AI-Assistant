from core import action_registry


def _capture_open_application_handler(monkeypatch):
    action = action_registry.get_action("open_application")
    captured = {}

    def fake_handler(**kwargs):
        captured.update(kwargs)
        return {"success": True, "action": "open_application"}

    monkeypatch.setattr(action, "handler", fake_handler)
    return captured


def test_open_application_declares_optional_verification_args():
    action = action_registry.get_action("open_application")
    assert action.args_schema == {"name": str}
    assert action.optional_args_schema == {"verify_window": bool, "verify_timeout": float}


def test_verification_arguments_are_passed_to_handler(monkeypatch):
    captured = _capture_open_application_handler(monkeypatch)
    result = action_registry.execute_action(
        "open_application",
        {"name": "notepad", "verify_window": True, "verify_timeout": 1},
    )
    assert result["success"] is True
    assert captured == {"name": "notepad", "verify_window": True, "verify_timeout": 1.0}


def test_window_verification_remains_optional(monkeypatch):
    captured = _capture_open_application_handler(monkeypatch)
    result = action_registry.execute_action("open_application", {"name": "notepad"})
    assert result["success"] is True
    assert captured == {"name": "notepad"}


def test_invalid_verification_type_is_rejected_before_handler(monkeypatch):
    captured = _capture_open_application_handler(monkeypatch)
    result = action_registry.execute_action(
        "open_application", {"name": "notepad", "verify_window": "yes"}
    )
    assert result["success"] is False
    assert "Invalid type for verify_window" in result["error"]
    assert captured == {}


def test_unknown_action_argument_is_rejected_before_handler(monkeypatch):
    captured = _capture_open_application_handler(monkeypatch)
    result = action_registry.execute_action(
        "open_application", {"name": "notepad", "run_anything": True}
    )
    assert result["success"] is False
    assert "Unsupported argument" in result["error"]
    assert captured == {}
