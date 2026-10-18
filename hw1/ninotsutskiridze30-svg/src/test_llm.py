import json

import pytest

from llm import extract_with_model


def test_fake_model_usage_is_logged_without_key_or_text(tmp_path, monkeypatch):
    monkeypatch.setenv("EVENT_MODEL_API_KEY", "fake-test-key")
    calls = []
    def fake(**kwargs):
        calls.append(kwargs)
        return {"extraction": {"is_event": False}, "tokens_in": 100, "tokens_out": 20}
    path = tmp_path / "usage.jsonl"
    result = extract_with_model("test notice", transport=fake, model="fake-model",
                               input_rate=2, output_rate=4, log_path=path)
    assert result == {"is_event": False}
    assert calls == [{"source_text": "test notice", "api_key": "fake-test-key", "model": "fake-model"}]
    line = json.loads(path.read_text())
    assert line["model"] == "fake-model"
    assert (line["tokens_in"], line["tokens_out"]) == (100, 20)
    assert line["cost_usd"] == pytest.approx(0.00028)
    assert line["latency_ms"] >= 0
    assert "fake-test-key" not in path.read_text()
    assert "test notice" not in path.read_text()


def test_missing_key_stops_before_transport(tmp_path, monkeypatch):
    monkeypatch.delenv("EVENT_MODEL_API_KEY", raising=False)
    def forbidden(**kwargs):
        raise AssertionError("No transport call without a key")
    with pytest.raises(RuntimeError, match="EVENT_MODEL_API_KEY"):
        extract_with_model("x", transport=forbidden, model="fake", input_rate=0, output_rate=0,
                           log_path=tmp_path / "usage.jsonl")
    assert not (tmp_path / "usage.jsonl").exists()


def test_failed_call_logs_unknown_usage_honestly(tmp_path, monkeypatch):
    monkeypatch.setenv("EVENT_MODEL_API_KEY", "fake-test-key")
    def failed(**kwargs):
        raise TimeoutError("fake timeout")
    path = tmp_path / "usage.jsonl"
    with pytest.raises(TimeoutError):
        extract_with_model("x", transport=failed, model="fake", input_rate=0, output_rate=0, log_path=path)
    record = json.loads(path.read_text())
    assert record["tokens_in"] is None and record["tokens_out"] is None
    assert record["cost_usd"] is None
