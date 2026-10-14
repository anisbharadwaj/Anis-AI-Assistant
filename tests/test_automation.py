"""Automation tests use mocks and temporary directories; they launch no real apps."""
import os
from automation import applications, files, windows_system


def test_open_application_lookup_is_mocked(monkeypatch):
    monkeypatch.setattr(applications, "IS_WINDOWS", True)
    monkeypatch.setattr(applications.shutil, "which", lambda _name: None)
    launched = []
    monkeypatch.setattr(
        applications.subprocess,
        "Popen",
        lambda args, **kwargs: launched.append((args, kwargs)),
    )

    result = applications.open_application("notepad")

    assert result["success"] is True
    assert launched == [(["notepad.exe"], {"shell": False})]


def test_list_directory(tmp_path, monkeypatch):
    directory = tmp_path / "testdir"
    directory.mkdir()
    (directory / "file1.txt").write_text("hello", encoding="utf-8")
    monkeypatch.setenv("ALLOWED_DIRS", str(tmp_path))

    result = files.list_directory(str(directory))

    assert result.get("success")
    assert any(item["name"] == "file1.txt" for item in result.get("items", []))


def test_create_and_read_file(tmp_path, monkeypatch):
    monkeypatch.setenv("ALLOWED_DIRS", str(tmp_path))
    path = tmp_path / "new.txt"

    result = files.create_text_file(str(path), "abc")
    assert result.get("success")
    read_result = files.read_text_file(str(path))
    assert read_result.get("success") and "abc" in read_result.get("content", "")


def test_search_file(tmp_path, monkeypatch):
    monkeypatch.setenv("ALLOWED_DIRS", str(tmp_path))
    directory = tmp_path / "s"
    directory.mkdir()
    (directory / "note.log").write_text("x", encoding="utf-8")

    result = files.search_file(str(tmp_path), "*.log")

    assert result.get("success") and len(result.get("matches", [])) >= 1


def test_windows_system_calls():
    result = windows_system.get_disk_space()
    assert isinstance(result, dict)
    assert "success" in result
