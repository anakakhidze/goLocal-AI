"""One log line per call, with argument names but never argument values."""

import json

import pytest

from src.tools import registry
from src.tools.registry import ToolError, call_tool


@pytest.fixture
def log_file(tmp_path, monkeypatch):
    path = tmp_path / "tools.jsonl"
    monkeypatch.setattr(registry, "LOG_PATH", path)
    return path


def _lines(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_successful_call_writes_one_line_without_values(log_file):
    call_tool("search_events", {"city": "Batumi", "limit": 2})
    (record,) = _lines(log_file)
    assert record["tool"] == "search_events"
    assert record["argument_names"] == ["city", "limit"]
    assert record["ok"] is True
    assert record["error_kind"] is None
    assert "Batumi" not in log_file.read_text(encoding="utf-8")


def test_refused_call_is_logged_with_error_kind_only(log_file):
    with pytest.raises(ToolError):
        call_tool("search_events", {"city": "Tbilisi", "user_id": "u-42"})
    (record,) = _lines(log_file)
    assert record["ok"] is False
    assert record["error_kind"] == "invalid_arguments"
    assert "u-42" not in log_file.read_text(encoding="utf-8")


def test_unknown_tool_is_logged(log_file):
    with pytest.raises(ToolError):
        call_tool("delete_everything", {})
    (record,) = _lines(log_file)
    assert record["error_kind"] == "unknown_tool"
