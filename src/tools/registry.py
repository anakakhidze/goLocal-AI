"""Tool registry and the single entry point every caller uses (call_tool).

Both doors (direct call_tool and the MCP server) validate through the same
contract and return the same messages. Every call writes one log line to
logs/tools.jsonl: tool name, argument NAMES (never values), ok or error kind,
and latency.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from src.tools.contract import INPUT_FIELDS, SearchEventsInput
from src.tools.search_events import search_events

LOG_PATH = Path(__file__).resolve().parents[2] / "logs" / "tools.jsonl"


class ToolError(Exception):
    """A message the model can read and act on. Never a stack trace, table name or path."""

    def __init__(self, message: str, kind: str = "error") -> None:
        super().__init__(message)
        self.kind = kind


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
            f"Invalid arguments: unexpected field '{loc}'. This tool accepts only: "
            f"{', '.join(INPUT_FIELDS)}. Remove that field and try again."
        )
    if kind.startswith("literal_error"):
        expected = error.get("ctx", {}).get("expected", "one of the listed values")
        return f"Invalid arguments: field '{loc}' must be {expected}. Pick a listed value and try again."
    if kind == "missing":
        return f"Invalid arguments: field '{loc}' is required. Add it and try again."
    return f"Invalid arguments: field '{loc}' is invalid ({error.get('msg', 'bad value')}). Fix it and try again."


def _log(name: str, arguments: Any, ok: bool, error_kind: str | None, started: float) -> None:
    """One line per call. Argument names only: values can contain personal data, so they are never written."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "tool": name,
        "argument_names": sorted(arguments) if isinstance(arguments, dict) else [],
        "ok": ok,
        "error_kind": error_kind,
        "latency_ms": round((time.perf_counter() - started) * 1000, 2),
    }
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def call_tool(name: str, arguments: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Validate arguments against the tool's contract, run the tool, and log the call."""
    started = time.perf_counter()
    ok = False
    error_kind = None
    try:
        if name not in TOOLS:
            raise ToolError(f"Unknown tool '{name}'. Available tools: {', '.join(TOOLS)}.", kind="unknown_tool")
        entry = TOOLS[name]
        try:
            request = entry["input"].model_validate(arguments or {})
        except ValidationError as error:
            first = error.errors()[0]
            raise ToolError(_message_for(first), kind="invalid_arguments") from None
        result = entry["run"](request)
        ok = True
        return result
    except ToolError as error:
        error_kind = error.kind
        raise
    finally:
        _log(name, arguments, ok, error_kind, started)
