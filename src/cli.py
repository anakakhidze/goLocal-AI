"""Offline executor CLI, optional model turn, and an actual MCP client smoke test."""
import argparse
import asyncio
import json
import sys

from .act import act, call_tool
from .tools import tools_for


async def mcp_smoke():
    from mcp import Client
    from .mcp_server import mcp
    async with Client(mcp) as client:
        listed = await client.list_tools()
        result = await client.call_tool("get_event_details", {"event_id": "valerian-shiukashvili"})
        return {"tools": [t.name for t in listed.tools], "is_error": result.is_error,
                "result": result.structured_content}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["tool", "ask", "mcp-smoke"])
    parser.add_argument("value", nargs="?")
    parser.add_argument("arguments", nargs="?", default="{}")
    args = parser.parse_args()
    try:
        if args.mode == "tool":
            result = call_tool({"name": args.value, "arguments": args.arguments}, tools_for(None), None)
            failed = not result["ok"]
        elif args.mode == "mcp-smoke":
            result = asyncio.run(mcp_smoke())
            failed = result["is_error"]
        else:
            result = act(args.value)
            failed = result["status"] != "answered"
    except Exception as exc:
        from .llm import ModelUnavailable
        if isinstance(exc, (ValueError, ModelUnavailable)):
            result = {"ok": False, "error": str(exc)}
        else:
            result = {"ok": False, "error": "Command failed. Check local setup and retry."}
        failed = True
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
