"""Tool registry and the single entry point every caller uses (call_tool).

Both doors (direct call_tool and the MCP server) validate through the same
contract and return the same messages.
"""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from src.tools.contract import INPUT_FIELDS, SearchEventsInput
from src.tools.search_events import search_events


class ToolError(Exception):
    """A message the model can read and act on. Never a stack trace, table name or path."""


TOOLS: dict[str, dict[str, Any]] = {
    "search_events": {
        "input": SearchEventsInput,
        "run": search_events,
        "description": (
            "Find synthetic events in Tbilisi or Batumi. Filter by category, free_only, "
            "max_price_gel (0 to 500 GEL) and limit (1 to 10). Results are sorted by start time."
        ),
    },
}


def _message_for(error: dict[str, Any]) -> str:
    loc = ".".join(str(part) for part in error.get("loc", ())) or "input"
    kind = error.get("type", "")
    if kind == "extra_forbidden":
        return (
            f"Unexpected field '{loc}'. This tool accepts only: {', '.join(INPUT_FIELDS)}. "
            "Remove that field and try again."
        )
    if kind.startswith("literal_error"):
        expected = error.get("ctx", {}).get("expected", "one of the listed values")
        return f"Field '{loc}' must be {expected}. Pick a listed value and try again."
    if kind == "missing":
        return f"Field '{loc}' is required. Add it and try again."
    return f"Field '{loc}' is invalid: {error.get('msg', 'bad value')}. Fix it and try again."


def call_tool(name: str, arguments: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Validate arguments against the tool's contract, then run the tool."""
    if name not in TOOLS:
        raise ToolError(f"Unknown tool '{name}'. Available tools: {', '.join(TOOLS)}.")
    entry = TOOLS[name]
    try:
        request = entry["input"].model_validate(arguments or {})
    except ValidationError as error:
        first = error.errors()[0]
        raise ToolError(_message_for(first)) from None
    return entry["run"](request)
