# Tool contract · search_events · anakakhidze

*One page, from the Lab 5 template (`templates/tool-contract.md`).*
**Code on main (after merge):** [src/tools/contract.py](../../src/tools/contract.py) · [src/tools/search_events.py](../../src/tools/search_events.py) · [src/tools/registry.py](../../src/tools/registry.py) · [src/tools/mcp_server.py](../../src/tools/mcp_server.py)
**Golden set:** [evals/tools/anakakhidze.yaml](../../evals/tools/anakakhidze.yaml) · **Runners:** [tests/test_tool_golden.py](../../tests/test_tool_golden.py), [tests/test_both_doors.py](../../tests/test_both_doors.py), [tests/test_tools_log.py](../../tests/test_tools_log.py)

## `search_events`

**In one sentence, for the model:** Finds synthetic events in Tbilisi or Batumi, filtered by category, free-only, maximum price and count. It reads data and changes nothing.

| | |
|---|---|
| **Effect** | reads |
| **Undo** | nothing to undo: no state changes |
| **Idempotent?** | yes: the same arguments give the same result, and nothing is written |
| **Offered to** | everyone, visitors included. It needs no identity, so offering it widely costs nothing |
| **Identity from** | n/a. The contract has no identity field, and the tool never receives a caller |
| **Touches** | `data/synthetic_events.json`, read only, at a fixed path the caller cannot change |
| **Must never** | write data, act for a named person, or build a path or URL from the arguments |

**Inputs.** Every string has a fixed set of values; every number has bounds; unknown fields are refused.

| Argument | Type | Constraint | Description the model reads |
|---|---|---|---|
| `city` | string | required; fixed set: `Tbilisi`, `Batumi` | City to search |
| `category` | string | optional; fixed set: `music`, `film`, `art`, `sport`, `talk`, `other` | Event category |
| `free_only` | boolean | default `false` | Only events with price 0 |
| `max_price_gel` | number | optional; 0 to 500 inclusive. Unknown prices never match | Highest price in GEL |
| `limit` | integer | default 5; 1 to 10 inclusive | How many events to return |

**Result.** A list of up to `limit` objects: `id` (integer ≥ 1), `title`, `venue`, `start` (ISO 8601 with UTC offset), `price_gel` (number, or null when unknown), `source_url` (must start with `https://`). No internal fields.

**Expected failures**

| When | Message the model reads |
|---|---|
| an unknown field, such as `user_id` | `Invalid arguments: unexpected field 'user_id'. This tool accepts only: city, category, free_only, max_price_gel, limit. Remove that field and try again.` |
| a city outside the fixed set | `Invalid arguments: field 'city' must be 'Tbilisi' or 'Batumi'. Pick a listed value and try again.` |
| a number out of bounds | `Invalid arguments: field 'max_price_gel' is invalid (...less than or equal to 500...). Fix it and try again.` |
| a required field missing | `Invalid arguments: field 'city' is required. Add it and try again.` |
| an unknown tool name | `Unknown tool 'x'. Available tools: search_events.` |

**Tests and golden cases**

| Case | Type | Expect | Where |
|---|---|---|---|
| `n1` free Tbilisi music | normal | ids `[1]` | `evals/tools/anakakhidze.yaml` |
| `n2` Batumi, limit 2 | normal | ids `[7, 8]` | `evals/tools/anakakhidze.yaml` |
| `n3` Tbilisi under 30 GEL, unknown price excluded | normal | ids `[1, 2, 3, 5, 6]` | `evals/tools/anakakhidze.yaml` |
| `b1` city `Kutaisi` | bad-input | refused, names `city` | `evals/tools/anakakhidze.yaml` |
| `a1` extra `user_id` field | adversarial | refused, names `user_id` | `evals/tools/anakakhidze.yaml` |

Golden cases run through `call_tool()` in `tests/test_tool_golden.py` in CI. `tests/test_both_doors.py` runs the same cases through the MCP server. `tests/test_tools_log.py` checks the log line.

**Log line.** `logs/tools.jsonl` gets one line per call: timestamp, tool name, argument **names** (never values), `ok`, error kind (`invalid_arguments`, `unknown_tool` or null) and latency in ms. Deliberately left out: argument values, which can hold personal data; results; and any caller id, since the tool never receives one.

## Least-privilege locks (the seven from Lab 5)

1. **A contract in code:** fixed sets, patterns, ranges, extra fields refused. → `src/tools/contract.py`
2. **No identity, account or permission field** the model can fill. → none in the contract; checked by `test_mcp_registers_the_tool_with_exact_fields`
3. **Offered only to callers who need it.** → n/a: read-only, offered to everyone, no identity
4. **No destructive tool unless a person confirms.** → n/a: `search_events` only reads; no delete or update tool exists
5. **Errors that say what to do next, and leak nothing.** → `src/tools/registry.py` (`_message_for`); the tests check for no `Traceback`
6. **A budget.** → n/a: one call per request and no loop
7. **One log line per call; tests for the bad calls.** → `registry._log`; `tests/test_tools_log.py`; golden cases `b1` and `a1`

## Known limits

- The data is synthetic (`data/synthetic_events.json`, every title marked `[SYNTHETIC]`). It is not a live ticket source.
- MCP door refusals are raised by the MCP framework before `call_tool()` runs, so they are **not** written to the log, and their wording is the framework's. Both doors refuse the same inputs; the golden cases check that.
