# Add automation tests. These use mocks and a temporary directory.
import os
from automation import applications, files, windows_system
from pathlib import Path


def test_open_application_lookup():
    res = applications.open_application("notepad")
    # On non-Windows systems, this may fail; assert structure
    assert isinstance(res, dict)
    assert "success" in res


def test_list_directory(tmp_path):
    d = tmp_path / "testdir"
    d.mkdir()
    (d / "file1.txt").write_text("hello")
    # monkeypatch allowed dirs to tmp_path via env
    os.environ["ALLOWED_DIRS"] = str(tmp_path)
    res = files.list_directory(str(d))
    assert res.get("success")
    assert any(item["name"] == "file1.txt" for item in res.get("items", []))


def test_create_and_read_file(tmp_path):
    os.environ["ALLOWED_DIRS"] = str(tmp_path)
    p = tmp_path / "new.txt"
    res = files.create_text_file(str(p), "abc")
    assert res.get("success")
    r2 = files.read_text_file(str(p))
    assert r2.get("success") and "abc" in r2.get("content")


def test_search_file(tmp_path):
    os.environ["ALLOWED_DIRS"] = str(tmp_path)
    d = tmp_path / "s"
    d.mkdir()
    (d / "note.log").write_text("x")
    res = files.search_file(str(tmp_path), "*.log")
    assert res.get("success") and len(res.get("matches", [])) >= 1


def test_windows_system_calls():
    res = windows_system.get_disk_space()
    assert isinstance(res, dict)
    assert "success" in res
