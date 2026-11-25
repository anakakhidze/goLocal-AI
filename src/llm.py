"""Optional Gemini function-calling adapter. Offline tool/MCP tests need no model key."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time

import httpx


MODEL = "gemini-3.1-flash-lite"
URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"


class ModelUnavailable(Exception):
    """Credential-free provider failure that can be displayed to a caller."""


def complete_tools(messages: list[dict], schemas: list[dict], *, client=None, api_key=None) -> dict:
    key = api_key or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise ModelUnavailable("Gemini is not configured. Export GOOGLE_API_KEY in your process environment.")
    wire = []
    for message in messages:
        if message["role"] == "assistant":
            if message.get("provider_content"):
                wire.append(message["provider_content"])
            else:
                wire.append({"role": "assistant", "content": message.get("content"), "tool_calls": [
                    {"id": c["id"], "type": "function", "function": {
                        "name": c["name"], "arguments": c["arguments"]}}
                    for c in message.get("tool_calls", [])]})
        else:
            wire.append({k: v for k, v in message.items() if k in {"role", "content", "tool_call_id", "name"}})
    payload = {"model": MODEL, "messages": wire, "tools": schemas, "temperature": 0,
               "max_tokens": 1200}
    started = time.perf_counter()
    usage = {}
    status = "failed"
    try:
        if client is None:
            with httpx.Client(timeout=30, follow_redirects=False) as owned:
                response = owned.post(URL, headers={"Authorization": "Bearer " + key}, json=payload)
        else:
            response = client.post(URL, headers={"Authorization": "Bearer " + key}, json=payload)
        response.raise_for_status()
        body = response.json()
        native = body["choices"][0]["message"]
        calls = [{"id": c["id"], "name": c["function"]["name"], "arguments": c["function"]["arguments"]}
                 for c in native.get("tool_calls", [])]
        usage = body.get("usage") or {}
        status = "ok"
        return {"content": native.get("content"), "tool_calls": calls, "provider_content": native}
    except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError) as exc:
        raise ModelUnavailable("Gemini request failed. Retry later; no booking, purchase or message was made.") from exc
    finally:
        destination = Path(os.environ.get("GOLOCAL_USAGE_LOG", "logs/usage.jsonl"))
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps({
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(), "model": MODEL,
                    "status": status, "tokens_in": usage.get("prompt_tokens"),
                    "tokens_out": usage.get("completion_tokens"),
                    "latency_ms": round((time.perf_counter() - started) * 1000, 3),
                }) + "\n")
        except OSError:
            pass
