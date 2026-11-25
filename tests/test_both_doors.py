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


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_both_doors_agree(case):
    if case["expect"] == "refused":
        with pytest.raises(ToolError):
            call_tool("search_events", case["arguments"])
        with pytest.raises(Exception) as raised:
            _mcp_call(case["arguments"])
        message = str(raised.value)
        assert "Traceback" not in message
        # The MCP door's wording comes from the framework; it must still name the offending field.
        offending = case["error_has"][-1]
        assert offending in message, message
    else:
        direct = [event["external_id"] for event in call_tool("search_events", case["arguments"])]
        content, _structured = _mcp_call(case["arguments"])
        via_mcp = [json.loads(item.text)["external_id"] for item in content]
        assert direct == case["result_has"]["ids"]
        assert via_mcp == case["result_has"]["ids"]


def test_mcp_registers_the_tool_with_exact_fields():
    tools = asyncio.run(mcp.list_tools())
    assert [tool.name for tool in tools] == ["search_events"]
    schema = tools[0].inputSchema
    request = schema["$defs"]["SearchEventsInput"]
    assert set(request["properties"]) == {"city", "category", "keyword", "max_price_gel", "start_date", "end_date", "limit"}
    assert request["additionalProperties"] is False
