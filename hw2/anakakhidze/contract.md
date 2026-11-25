# Tool contract · search_events · anakakhidze

**Owner:** anakakhidze · **Function:** `search_events` (lookup over synthetic event data)
**Code on main (after merge):** [src/tools/contract.py](../../src/tools/contract.py) · [src/tools/search_events.py](../../src/tools/search_events.py) · [src/tools/registry.py](../../src/tools/registry.py) · [src/tools/mcp_server.py](../../src/tools/mcp_server.py)
**Golden set:** [evals/tools/anakakhidze.yaml](../../evals/tools/anakakhidze.yaml) · **Test runner:** [tests/test_tool_golden.py](../../tests/test_tool_golden.py), [tests/test_both_doors.py](../../tests/test_both_doors.py)

## Purpose

A model asks for events in one city, optionally filtered by category, price and count. The tool
returns matching events, sorted by start time. It is a read-only lookup. It sends no messages,
pays for nothing and changes no data.

## Inputs (exactly these five fields)

| Field | Type | Rule |
|---|---|---|
| `city` | string, required | fixed set: `Tbilisi`, `Batumi` |
| `category` | string, optional | fixed set: `music`, `film`, `art`, `sport`, `talk`, `other` |
| `free_only` | boolean, default `false` | when true, only events with price 0 |
| `max_price_gel` | number, optional | 0 to 500 inclusive. Events with unknown price never match a price limit |
| `limit` | integer, default 5 | 1 to 10 inclusive |

Any other field is refused (`extra="forbid"`). Identity fields (user, student, account), paths,
URLs and free-text queries are not part of the contract, so they cannot be passed.

## Output

A list of up to `limit` objects with exactly: `id`, `title`, `venue`, `start` (ISO 8601 with UTC offset),
`price_gel` (number or null when unknown), `source_url` (must start with `https://`).

## Errors (what the model sees)

- Direct door (`call_tool`): a message that names the field and the fix, for example
  `Unexpected field 'user_id'. This tool accepts only: city, category, free_only, max_price_gel, limit.`
- MCP door: the server validates the same model before the tool runs. Its message names the bad field.
- No stack traces, table names or file paths appear in any message. Tests check this.

## Least-privilege locks

1. Input model refuses unknown fields (`extra="forbid"`).
2. Every string is a fixed set (no free text reaches the tool).
3. Every number has bounds (`max_price_gel` 0–500, `limit` 1–10).
4. No user, student or account field exists.
5. Data is read from one fixed path. Callers cannot choose a file.
6. No network, no writes, no model calls.
7. Errors are messages for the model, not internal details.

## Known limits

- The data is synthetic (`data/synthetic_events.json`, every title marked `[SYNTHETIC]`). It is not a live ticket source.
- The MCP door's error text comes from the MCP framework, so it is less friendly than the direct door's text.
  Both refuse the same inputs; the golden cases check that.
