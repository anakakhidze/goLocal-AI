# GoLocal tool contracts

## `get_event_details` — Archi-lee-Sun, individual HW2

Read a selected GoLocal event/listing from the currently checked-out curated corpus.
This is a runtime lookup of versioned source snapshots, **not a live ticket-site request**.
It supplies the missing detail capability behind the product's event-detail workflow.

| Boundary | Enforced behavior |
|---|---|
| Effect / undo | Public read; no booking, purchase, file export, account write or message. Nothing to undo. |
| Idempotency | Same corpus + same ID returns the same record; no persistent business state changes. |
| Offered to | Visitors and signed-in callers; caller-specific turn allowlist still enforced. |
| Identity | Trusted launcher/request context only; no identity parameter in either door. |
| Resources | Fixed `data/corpus/events/*.md`; no client-selected paths, URLs, SQL, network or private data. Audit metadata goes to the server-configured log. |
| Input | `event_id`: strict string, 1–64 characters, `^[a-z0-9]+(?:-[a-z0-9]+)*$`; unknown fields forbidden. |
| Output | `event_id`, title, original HTTPS source, snapshot date, verbatim listed time/location/details, kind, `live_verified=false`, freshness warning. Missing times/locations stay null. |
| Failures | Invalid arguments: fix the listed fields. Unknown ID: call `list_events`. Corpus failure: ask maintainer/retry. Unexpected error: sanitized refusal. |
| Never | Infer current availability, fabricate a venue/date/price, read an input-derived file, accept a caller ID, perform a consequential action. |

Implementation: `src/contracts.py`, `src/catalog.py`, `src/tools.py`, `src/act.py`.
MCP: `src/mcp_server.py`; exact schema and executor shared with function calling.
Evidence: `tests/test_contracts.py`, `test_tools.py`, `test_act.py`, `test_mcp.py`;
personal cases: `evals/tools/Archi-lee-Sun.yaml`.

Every attempted tool call writes one audit line: timestamp, safe tool name,
pseudonymous caller hash, success/error code and latency. No raw identity,
arguments, result body, model text, credentials or traceback is stored.

## `list_events` — minimal common Lab 5 frame

Public read returning available event IDs/titles/snapshot dates, sorted by ID.
`limit` is a strict integer from 1 to 20, default 5; no other fields accepted.
It excludes the reviewed pool/venue-only record. It does not assert dates are upcoming.
It is the common discovery tool, **not Archil's individual HW2 function**.

## HW2 ownership

| Member | Individual function | Status |
|---|---|---|
| Archi-lee-Sun | `get_event_details` | Implemented on product branch; teammate review required |
| anakakhidze | Not assigned by this change | Teammate selects a different function |
| ninotsutskiridze30-svg | Not assigned by this change | Teammate selects a different function |

No teammate's individual work is implemented or claimed here. The product PR also
adds the missing shared executor/MCP/CI frame needed to run Archil's tool.
