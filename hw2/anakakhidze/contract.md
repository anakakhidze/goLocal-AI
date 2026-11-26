# Tool contract · search_events · anakakhidze

*One page, from the Lab 5 template (`templates/tool-contract.md`).*
**Code on main (after merge):** [src/search_events.py](../../src/search_events.py) (contract and lookup) · [src/tools.py](../../src/tools.py) (one registry entry) · the shared executor [src/act.py](../../src/act.py) and MCP server [src/mcp_server.py](../../src/mcp_server.py)
**Data:** [data/demo_events.json](../../data/demo_events.json) (GoLocal's 25 fictional demo events)
**Golden set:** [evals/tools/anakakhidze.yaml](../../evals/tools/anakakhidze.yaml) · **Runner (shared):** [tests/test_tool_golden.py](../../tests/test_tool_golden.py) · **Filter checks:** [tests/test_search_events.py](../../tests/test_search_events.py)

## `search_events`

**In one sentence, for the model:** Finds GoLocal's fictional demo events in Tbilisi by category, keyword, price and date window. It reads a fixed list and changes nothing.

| | |
|---|---|
| **Effect** | reads |
| **Undo** | nothing to undo: no state changes |
| **Idempotent?** | yes: the same arguments give the same result, and nothing is written |
| **Offered to** | everyone, visitors included. It needs no identity, so offering it widely costs nothing |
| **Identity from** | n/a. The contract has no identity field, and the tool never receives a caller |
| **Touches** | `data/demo_events.json`, read only, at a fixed path the caller cannot change. No database |
| **Must never** | write data, act for a named person, or build a path, URL or query from the arguments |

**Inputs.** Every string has a pattern or a fixed set of values; every number has bounds; unknown fields are refused.

| Argument | Type | Constraint | Description the model reads |
|---|---|---|---|
| `city` | string | required; fixed set: `Tbilisi` | City to search (the demo fixture is all in Tbilisi) |
| `category` | string | optional; fixed set of 15 GoLocal categories (`music`, `nightlife`, `exhibition`, …, `other`) | Event category |
| `keyword` | string | optional; letters and spaces only, 1 to 40 characters | Word to find in the title or description, any case |
| `max_price_gel` | number | optional; 0 to 500 inclusive | Highest price in GEL. Events with unknown prices or other currencies are excluded |
| `start_date` | date | optional; `YYYY-MM-DD` | First local date to include |
| `end_date` | date | optional; `YYYY-MM-DD`; not before `start_date` | Last local date to include |
| `limit` | integer | default 5; 1 to 12 inclusive | How many events to return |

**Result.** A list of up to `limit` objects: `external_id`, `title`, `venue_name`, `start` and `end` (ISO 8601 with the Tbilisi offset `+04:00`), `price_min` and `price_max` (decimal strings, or null when unknown), `currency`, and `source_url` (an `https://` link to the demo source page). No internal fields.

**Expected failures**

| When | Message the model reads |
|---|---|
| an unknown field, such as `user_id` | `Invalid arguments: unexpected field 'user_id'. This tool accepts only: city, category, keyword, max_price_gel, start_date, end_date, limit. Remove that field and try again.` |
| a city outside the fixed set | `Invalid arguments: field 'city' must be 'Tbilisi'. Pick a listed value and try again.` |
| a keyword with characters outside the pattern, such as quotes or symbols | `Invalid arguments: field 'keyword' is invalid (...). Fix it and try again.` |
| a number out of bounds | `Invalid arguments: field 'max_price_gel' is invalid (...less than or equal to 500...). Fix it and try again.` |
| a date that is not a real date, or an end before the start | `Invalid arguments: field '...' is invalid (...). Fix it and try again.` |
| an unknown tool name | `Unknown tool 'x'. Available tools: search_events.` |

**Tests and golden cases**

| Case | Type | Expect | Where |
|---|---|---|---|
| `n1` Tbilisi music up to 30 GEL | normal | ids `[paper-lantern-jazz, sunset-guitar]` | `evals/tools/anakakhidze.yaml` |
| `n2` keyword `jazz` | normal | ids `[paper-lantern-jazz]` | `evals/tools/anakakhidze.yaml` |
| `n3` dates 2026-10-20 to 2026-10-22 | normal | ids `[paper-lantern-jazz, rooftop-dance, color-and-light]` | `evals/tools/anakakhidze.yaml` |
| `b1` city `Batumi` | bad-input | refused, names `city` | `evals/tools/anakakhidze.yaml` |
| `a1` keyword `x' OR '1'='1` (SQL injection text) | adversarial | refused, names `keyword` | `evals/tools/anakakhidze.yaml` |

The expected ids were checked by hand against the fixture file. Golden cases run through the shared executor `call_tool()` in `tests/test_tool_golden.py` in CI, the same runner as Archil's cases. The shared MCP server serves the same tool, and `tests/test_mcp.py` checks that every registry entry is registered. `tests/test_search_events.py` checks the filter rules.

**Log line.** The shared executor writes one audit line per call: timestamp, safe tool name, caller hash (none for this visitor-level tool), `ok`, error code and latency. It never records arguments, results, model text or tracebacks.

## Least-privilege locks (the seven from Lab 5)

1. **A contract in code:** fixed sets, patterns, ranges, extra fields refused. → `src/search_events.py`
2. **No identity, account or permission field** the model can fill. → none in the contract; checked by `test_mcp_registers_the_tool_with_exact_fields`
3. **Offered only to callers who need it.** → n/a: read-only, offered to everyone, no identity
4. **No destructive tool unless a person confirms.** → n/a: `search_events` only reads; no delete or update tool exists
5. **Errors that say what to do next, and leak nothing.** → the shared executor `src/act.py`; the golden runner checks the messages and no `Traceback`
6. **A budget.** → n/a: one call per request and no loop
7. **One log line per call; tests for the bad calls.** → `src/act.py` (`_record`); golden cases `b1` and `a1`

## Known limits

- The data is GoLocal's fictional demo fixture (every title marked `[DEMO]`). It is not live ticket data.
- The filters follow GoLocal's SQL rules, but they're reimplemented in Python. No database runs in tests, so the real SQL is not executed here.
- The fixture dates are anchored at 2026-10-19 (GoLocal's seed default), so date filters refer to that anchor.
- MCP door refusals are raised by the MCP framework before `call_tool()` runs, so they are **not** written to the log, and their wording is the framework's. Both doors refuse the same inputs; the golden cases check that.
