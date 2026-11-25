"""MCP SDK 2.3 server. The registry supplies exact schemas and every call uses our gates."""
import json
import os

from mcp.server import Server
from mcp.types import CallToolResult, ListToolsResult, TextContent, Tool as MCPTool, ToolAnnotations

from .act import call_tool
from .catalog import EventDetails
from .tools import EventList, tools_for


def _caller():
    # Trusted launcher context, not a field accepted from an MCP client or model.
    return os.environ.get("GOLOCAL_CALLER") or None


async def list_mcp_tools(_context, _params):
    return ListToolsResult(tools=[MCPTool(
        name=tool.name, description=tool.args.__doc__.strip(),
        input_schema=tool.args.model_json_schema(),
        output_schema=(EventDetails if tool.name == "get_event_details" else EventList).model_json_schema(),
        annotations=ToolAnnotations(read_only_hint=True, destructive_hint=False,
                                    idempotent_hint=True, open_world_hint=False),
    ) for tool in tools_for(_caller()).values()])


async def call_mcp_tool(_context, params):
    outcome = call_tool({"id": "mcp", "name": params.name,
                         "arguments": json.dumps(params.arguments if params.arguments is not None else {})},
                        tools_for(_caller()), _caller())
    if not outcome["ok"]:
        return CallToolResult(is_error=True, content=[TextContent(type="text", text=outcome["error"])])
    result = outcome["result"]
    return CallToolResult(is_error=False, structured_content=result,
                          content=[TextContent(type="text", text=json.dumps(result, ensure_ascii=False))])


# The SDK's public low-level API keeps additionalProperties=false identical and
# routes rejected calls through our audit logger too. No private SDK internals.
mcp = Server("golocal", version="0.1.0", instructions=(
    "Read GoLocal event snapshots. Always show the original source and snapshot warning. "
    "No tool books tickets, writes user data, or contacts external services."
), on_list_tools=list_mcp_tools, on_call_tool=call_mcp_tool)


if __name__ == "__main__":
    import asyncio
    import sys
    if "--http" in sys.argv:
        import uvicorn
        uvicorn.run(mcp.streamable_http_app(), host="127.0.0.1", port=8001)
    else:
        from mcp.server.stdio import stdio_server

        async def serve():
            async with stdio_server() as (read_stream, write_stream):
                await mcp.run(read_stream, write_stream, mcp.create_initialization_options())

        asyncio.run(serve())
