"""Both doors: the same golden cases must give the same answer through call_tool() and through the MCP server.

Door one: call_tool(name, arguments), the direct path.
Door two: the MCP server, which takes a single 'request' object shaped like SearchEventsInput.
"""

import asyncio
import json
from pathlib import Path

import pytest
import yaml

from src.tools.mcp_server import mcp
from src.tools.registry import ToolError, call_tool

CASES = []
for path in sorted((Path(__file__).resolve().parents[1] / "evals" / "tools").glob("*.yaml")):
    CASES += yaml.safe_load(path.read_text(encoding="utf-8"))["cases"]


def _mcp_call(arguments):
    return asyncio.run(mcp.call_tool("search_events", {"request": arguments}))


@pytest.mark.parametrize("case", CASES, ids=[c["name"] for c in CASES])
def test_both_doors_agree(case):
    expect = case["expect"]
    if "error_contains" in expect:
        with pytest.raises(ToolError):
            call_tool(case["tool"], case["arguments"])
        with pytest.raises(Exception) as raised:
            _mcp_call(case["arguments"])
        message = str(raised.value)
        assert "Traceback" not in message
        assert any(key in message for key in case["arguments"]), message
    else:
        direct = call_tool(case["tool"], case["arguments"])
        content, _structured = _mcp_call(case["arguments"])
        via_mcp = [json.loads(item.text)["id"] for item in content]
        assert [event["id"] for event in direct] == expect["ids"]
        assert via_mcp == expect["ids"]


def test_mcp_registers_the_tool_with_exact_fields():
    tools = asyncio.run(mcp.list_tools())
    assert [tool.name for tool in tools] == ["search_events"]
    schema = tools[0].inputSchema
    request = schema["$defs"]["SearchEventsInput"]
    assert set(request["properties"]) == {"city", "category", "free_only", "max_price_gel", "limit"}
    assert request["additionalProperties"] is False
