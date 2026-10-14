from automation import applications


def test_unknown_application_is_rejected_without_launching(monkeypatch):
    def unexpected_launch(*_args, **_kwargs):
        raise AssertionError("A real or mocked process should not be launched")

    monkeypatch.setattr(applications.subprocess, "Popen", unexpected_launch)
    result = applications.open_application("notepad.exe & whoami")

    assert result["success"] is False
    assert "Unsupported application" in result["error"]


def test_open_website_normalizes_and_mocks_browser(monkeypatch):
    calls = []
    monkeypatch.setattr(
        applications.webbrowser,
        "open",
        lambda url, new=0: calls.append((url, new)) or True,
    )

    result = applications.open_website("example.com/path")

    assert result["success"] is True
    assert calls == [("https://example.com/path", 2)]


def test_open_website_rejects_non_http_scheme_without_opening(monkeypatch):
    monkeypatch.setattr(
        applications.webbrowser,
        "open",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("Browser must not be called for an unsafe URL")
        ),
    )

    result = applications.open_website("javascript:alert(1)")

    assert result["success"] is False
    assert "http:// and https://" in result["error"]


def test_open_application_can_verify_window_with_a_mock(monkeypatch):
    monkeypatch.setattr(applications, "IS_WINDOWS", True)
    monkeypatch.setattr(applications.shutil, "which", lambda _name: None)
    monkeypatch.setattr(applications.subprocess, "Popen", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        applications,
        "verify_window_visible",
        lambda title, timeout_seconds=3.0: {
            "success": True,
            "visible": True,
            "title": title,
        },
    )

    result = applications.open_application("notepad", verify_window=True, verify_timeout=1)

    assert result["success"] is True
    assert result["window_verification"]["visible"] is True
    assert result["window_verification"]["title"] == "Notepad"
