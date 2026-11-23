from dataclasses import replace
import json
import os
from pathlib import Path

import pytest

from src.act import MAX_ROUNDS, act, call_tool
from src.tools import TOOLS, tools_for


def call(arguments, name="get_event_details", allowed=None, caller=None):
    return call_tool({"id": "test", "name": name,
                      "arguments": arguments if isinstance(arguments, str) else json.dumps(arguments)},
                     tools_for(caller) if allowed is None else allowed, caller)


def test_valid_call_returns_a_typed_result_and_one_private_audit_line():
    out = call({"event_id": "hardhell"}, caller="private-user-a")
    assert out["ok"] and out["result"]["event_id"] == "hardhell"
    lines = Path(os.environ["GOLOCAL_TOOL_LOG"]).read_text().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["ok"] and record["latency_ms"] >= 0 and len(record["caller_hash"]) == 16
    assert "private-user-a" not in lines[0] and "hardhell" not in lines[0]


@pytest.mark.parametrize("arguments", [{"event_id": "../../.env"}, {"event_id": "hardhell", "user_id": "victim"},
                                        {"event_id": 2}, {"event_id": "a" * 65}])
def test_bad_arguments_never_reach_the_function(arguments):
    reached = []
    spy = replace(TOOLS["get_event_details"], run=lambda args: reached.append(args))
    out = call(arguments, allowed={"get_event_details": spy})
    assert not out["ok"] and out["error_code"] == "invalid_arguments"
    assert reached == []


def test_tool_omitted_from_turn_allowlist_never_runs():
    out = call({"event_id": "hardhell"}, allowed={})
    assert not out["ok"] and out["error_code"] == "not_offered"


@pytest.mark.parametrize("raw", ['[]', 'null', 'not json', '{"event_id":"hardhell","event_id":"other"}',
                               '{"event_id":NaN}', '{"event_id":"' + 'x' * 5000 + '"}'])
def test_malformed_or_oversized_json_is_a_safe_refusal(raw):
    out = call(raw)
    assert not out["ok"] and out["error_code"] == "invalid_arguments"


def test_unexpected_exception_is_sanitized():
    def broken(_):
        raise RuntimeError("secret database table at C:/private/credentials")
    spy = replace(TOOLS["get_event_details"], run=broken)
    out = call({"event_id": "hardhell"}, allowed={"get_event_details": spy})
    assert not out["ok"] and out["error_code"] == "internal_error"
    assert "secret" not in json.dumps(out) and "C:/" not in json.dumps(out)


def test_log_failure_is_reported_instead_of_claiming_audited_success(tmp_path, monkeypatch):
    path = tmp_path / "not-a-directory"
    path.write_text("file")
    monkeypatch.setenv("GOLOCAL_TOOL_LOG", str(path / "tools.jsonl"))
    assert call({"event_id": "hardhell"})["error_code"] == "audit_unavailable"


def test_error_is_returned_to_model_and_native_reasoning_is_preserved():
    requests = []
    native = {"role": "assistant", "content": None, "reasoning_details": [{"signature": "opaque"}]}
    def model(messages, _schemas):
        requests.append(list(messages))
        if len(requests) == 1:
            return {"content": None, "provider_content": native, "tool_calls": [
                {"id": "c1", "name": "get_event_details", "arguments": '{"event_id":"../bad"}'}]}
        assert messages[-2]["provider_content"] == native
        assert json.loads(messages[-1]["content"])["error_code"] == "invalid_arguments"
        return {"content": "Please select an ID from list_events.", "tool_calls": []}
    assert act("details please", llm=model)["status"] == "answered"
    assert len(requests) == 2


def test_nonterminating_model_is_stopped_at_the_round_budget():
    calls = []
    def forever(*_):
        calls.append(1)
        return {"content": None, "tool_calls": [{"id": "c", "name": "list_events", "arguments": "{}"}]}
    assert act("keep looking", llm=forever)["status"] == "stopped"
    assert len(calls) == MAX_ROUNDS


def test_parallel_call_budget_stops_before_execution():
    def too_many(*_):
        return {"tool_calls": [{"id": "c", "name": "list_events", "arguments": "{}"}] * 5}
    result = act("look up everything", llm=too_many)
    assert result["status"] == "stopped" and result["calls"] == []


@pytest.mark.parametrize("question", ["", "   ", None, "x" * 2001])
def test_invalid_question_makes_zero_model_calls(question):
    with pytest.raises(ValueError):
        act(question, llm=lambda *_: pytest.fail("invalid input called the model"))
