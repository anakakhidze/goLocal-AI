import asyncio
import json
import os
from pathlib import Path
import sys

from mcp import Client
from mcp.client.stdio import StdioServerParameters
import pytest

from src.act import call_tool
from src.mcp_server import mcp
from src.tools import TOOLS, tools_for


async def listing():
    async with Client(mcp) as client:
        return {t.name: t for t in (await client.list_tools()).tools}


async def invoke(name, arguments):
    async with Client(mcp) as client:
        return await client.call_tool(name, arguments)


def test_exact_both_doors_schema_including_additional_properties():
    registered = asyncio.run(listing())
    assert set(registered) == set(TOOLS)
    for name, tool in TOOLS.items():
        assert registered[name].input_schema == tool.schema()["function"]["parameters"]
        assert registered[name].input_schema["additionalProperties"] is False
        hints = registered[name].annotations
        assert hints.read_only_hint and hints.idempotent_hint and not hints.destructive_hint


def test_success_matches_the_real_executor():
    arguments = {"event_id": "valerian-shiukashvili"}
    direct = call_tool({"name": "get_event_details", "arguments": json.dumps(arguments)}, tools_for(None), None)
    result = asyncio.run(invoke("get_event_details", arguments))
    assert not result.is_error and result.structured_content == direct["result"]


@pytest.mark.parametrize("arguments", [{"event_id": "../../.env"}, {"event_id": "hardhell", "user_id": "victim"},
                                       {"event_id": 1}, {"event_id": "A Title"}])
def test_mcp_rejects_the_same_bad_and_adversarial_arguments_and_logs_once(arguments):
    result = asyncio.run(invoke("get_event_details", arguments))
    assert result.is_error and "invalid arguments" in result.content[0].text
    lines = Path(os.environ["GOLOCAL_TOOL_LOG"]).read_text().splitlines()
    assert len(lines) == 1 and json.loads(lines[0])["error_code"] == "invalid_arguments"
    assert "victim" not in lines[0] and "../../" not in lines[0]


def test_mcp_expected_failure_has_a_recovery_instruction():
    result = asyncio.run(invoke("get_event_details", {"event_id": "not-found"}))
    assert result.is_error and "list_events" in result.content[0].text


def test_mcp_public_result_does_not_depend_on_a_forged_identity(monkeypatch):
    monkeypatch.setenv("GOLOCAL_CALLER", "trusted-launcher-user")
    result = asyncio.run(invoke("get_event_details", {"event_id": "hardhell", "caller": "victim"}))
    assert result.is_error
    assert "GOLOCAL_CALLER" not in asyncio.run(listing())["get_event_details"].input_schema["properties"]


def test_real_stdio_process_lists_and_calls_the_personal_tool():
    async def run():
        parameters = StdioServerParameters(
            command=sys.executable, args=["-B", "-m", "src.mcp_server"],
            cwd=Path(__file__).resolve().parents[1],
            env={"GOLOCAL_TOOL_LOG": os.environ["GOLOCAL_TOOL_LOG"], "PYTHONDONTWRITEBYTECODE": "1"},
        )
        async with Client(parameters) as client:
            assert "get_event_details" in {t.name for t in (await client.list_tools()).tools}
            result = await client.call_tool("get_event_details", {"event_id": "hardhell"})
            assert not result.is_error and result.structured_content["event_id"] == "hardhell"
    asyncio.run(run())
