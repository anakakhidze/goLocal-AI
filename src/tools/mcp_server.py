"""MCP server that serves the registry. Door two: the same contract as call_tool().

The MCP input is the SearchEventsInput model itself (extra="forbid"), so the
server refuses unknown fields before the tool runs. The tool then runs through
the same call_tool() path as door one.
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from src.tools.contract import SearchEventsInput
from src.tools.registry import TOOLS, call_tool

mcp = FastMCP("goLocal-tools")


@mcp.tool(description=TOOLS["search_events"]["description"])
def search_events(request: SearchEventsInput) -> list[dict[str, Any]]:
    return call_tool("search_events", request.model_dump())


if __name__ == "__main__":
    mcp.run()
