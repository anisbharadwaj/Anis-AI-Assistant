from automation import window_verification


def test_verification_reports_windows_only_when_not_on_windows(monkeypatch):
    monkeypatch.setattr(window_verification, "IS_WINDOWS", False)

    result = window_verification.verify_window_visible("Notepad", timeout_seconds=0)

    assert result["success"] is False
    assert result["visible"] is False
    assert "only supported on Windows" in result["error"]


def test_verification_succeeds_when_mock_window_is_found(monkeypatch):
    monkeypatch.setattr(window_verification, "IS_WINDOWS", True)
    monkeypatch.setattr(window_verification, "_find_visible_window", lambda _title: True)

    result = window_verification.verify_window_visible("Notepad", timeout_seconds=0)

    assert result["success"] is True
    assert result["visible"] is True
    assert result["title"] == "Notepad"


def test_verification_times_out_when_no_mock_window_is_found(monkeypatch):
    monkeypatch.setattr(window_verification, "IS_WINDOWS", True)
    monkeypatch.setattr(window_verification, "_find_visible_window", lambda _title: False)

    result = window_verification.verify_window_visible("Missing Window", timeout_seconds=0)

    assert result["success"] is False
    assert result["visible"] is False
    assert "before timeout" in result["error"]
