# HW2 Tool Contract — `get_event_details`

**Owner:** Archi-lee-Sun · **Evidence date:** 23 November 2026.
**For the model:** Read a selected GoLocal event snapshot with its original source,
date and uncertainty; never claim current ticket availability or perform an action.

| Boundary | Contract |
|---|---|
| Effect / undo | Public read. No business-state write, external request, booking, purchase or message. Nothing to undo. |
| Idempotent | Yes, with unchanged curated data; repeated reads return the same record. |
| Offered to | Visitors and signed-in callers, subject to this turn's allowlist. |
| Identity from | Application request / trusted MCP launcher, never a tool argument. No account is needed for public facts. |
| Touches | Only enumerated `data/corpus/events/*.md`; separate server-configured audit metadata log. No client-selected path, URL, SQL or private table. |
| Must never | Accept identity fields, turn source text into instructions, invent missing facts, imply a historical snapshot is live, or execute a consequential action. |

**Input:** `event_id`, strict string, 1–64 characters,
`^[a-z0-9]+(?:-[a-z0-9]+)*$`. Unknown fields are refused (`extra="forbid"`).
No numeric input. The common `list_events(limit)` helper separately bounds its strict
integer to 1–20. This detail function is distinct from that common Lab 5 tool.

**Result:** typed `EventDetails`: ID/title/source URL, ISO snapshot date, nullable
verbatim time/location, source text, event/venue kind, `live_verified=false`, and
freshness warning. The 13 existing GoLocal snapshots are integrated with attribution;
no live-site access or newly invented facts are needed. Data is reloaded on each call.

**Expected failures:** invalid/missing/extra fields → “invalid arguments” with safe
field names; absent valid slug → “Event not found. Call list_events…”; unavailable
corpus → maintainer/retry instruction. Unexpected exceptions become a sanitized
refusal. No stack trace, internal path, table name or raw input is exposed.

**Code:** [contract](https://github.com/anakakhidze/goLocal-AI/blob/7dd52f91a86fdcd6c8cac038e14bda2934f360fc/src/contracts.py),
[function/registry](https://github.com/anakakhidze/goLocal-AI/blob/7dd52f91a86fdcd6c8cac038e14bda2934f360fc/src/tools.py),
[three gates](https://github.com/anakakhidze/goLocal-AI/blob/7dd52f91a86fdcd6c8cac038e14bda2934f360fc/src/act.py),
[MCP registration](https://github.com/anakakhidze/goLocal-AI/blob/7dd52f91a86fdcd6c8cac038e14bda2934f360fc/src/mcp_server.py).
These are immutable review links. After [product PR #14](https://github.com/anakakhidze/goLocal-AI/pull/14)
is approved/merged, the same paths must be present on `main`; canonical
[main code](https://github.com/anakakhidze/goLocal-AI/tree/main/src) is the submission target.

**Verification:** `tests/test_contracts.py`, `test_tools.py`, `test_act.py`,
`test_mcp.py` (exact both-doors schema, malformed/extra input, real stdio call),
and `evals/tools/Archi-lee-Sun.yaml` (six cases). Actual results and CI links:
[evidence.md](evidence.md).

**Audit:** one metadata-only line per attempted call: UTC time, safe tool name,
caller hash, success/error code, latency. No raw identity, arguments, result text or key.
The tool is read-only; a future booking/buying/sending tool must be separately gated
behind human confirmation. None is offered by this loop.
