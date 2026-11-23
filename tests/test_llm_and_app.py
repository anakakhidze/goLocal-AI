import json
import os
from pathlib import Path

import httpx
import pytest

from src.app import handle_turn
from src.llm import ModelUnavailable, complete_tools
from src.tools import TOOLS


def test_provider_uses_real_schemas_and_preserves_native_reasoning_for_next_turn():
    requests = []
    native = {"role": "assistant", "content": None, "reasoning_details": [{"signature": "opaque"}],
              "tool_calls": [{"id": "c1", "type": "function", "function": {
                  "name": "get_event_details", "arguments": '{"event_id":"hardhell"}'}}]}
    def response(request):
        requests.append(json.loads(request.content))
        return httpx.Response(200, json={"choices": [{"message": native}],
                                       "usage": {"prompt_tokens": 100, "completion_tokens": 20}})
    with httpx.Client(transport=httpx.MockTransport(response)) as client:
        first = complete_tools([{"role": "user", "content": "details"}], [TOOLS["get_event_details"].schema()],
                               api_key="test-only-key", client=client)
        complete_tools([{"role": "assistant", "provider_content": first["provider_content"]}], [],
                       api_key="test-only-key", client=client)
    assert requests[0]["tools"][0]["function"]["parameters"]["additionalProperties"] is False
    assert requests[1]["messages"][0] == native
    log = Path(os.environ["GOLOCAL_USAGE_LOG"]).read_text()
    assert len(log.splitlines()) == 2 and "test-only-key" not in log and "opaque" not in log


def test_provider_failure_is_sanitized_and_logged():
    with httpx.Client(transport=httpx.MockTransport(lambda _: httpx.Response(503, text="private-provider-body"))) as client:
        with pytest.raises(ModelUnavailable) as error:
            complete_tools([], [], api_key="test-only-key", client=client)
    assert "private-provider-body" not in str(error.value)
    assert json.loads(Path(os.environ["GOLOCAL_USAGE_LOG"]).read_text())["status"] == "failed"


def test_model_key_is_not_needed_for_tools_but_missing_key_is_honest():
    with pytest.raises(ModelUnavailable, match="not configured"):
        complete_tools([], [])


def test_endpoint_identity_comes_from_launcher_and_not_the_request(monkeypatch):
    monkeypatch.setenv("GOLOCAL_CALLER", "server-user")
    status, _ = handle_turn({"question": "details", "user_id": "victim"}, llm=lambda *_: pytest.fail())
    assert status == 400
    status, result = handle_turn({"question": "details"}, llm=lambda *_: {"content": "Snapshot only", "tool_calls": []})
    assert status == 200 and result["text"] == "Snapshot only"


@pytest.mark.parametrize("question", [None, "", " ", "x" * 2001])
def test_bad_endpoint_question_calls_no_model(question):
    status, _ = handle_turn({"question": question}, llm=lambda *_: pytest.fail())
    assert status == 400
