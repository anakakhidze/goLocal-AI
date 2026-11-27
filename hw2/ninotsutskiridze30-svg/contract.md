# HW2 Tool Contract — `find_events_by_kind`

**Owner:** `ninotsutskiridze30-svg` · **Team repo:** [anakakhidze/goLocal-AI](https://github.com/anakakhidze/goLocal-AI)  
**Code on `main`:** [`EventKind`](../../src/contracts.py#L12) and [`FindEventsByKind`](../../src/contracts.py#L25); [`KindEventSummary`](../../src/tools.py#L30), [`find_events_by_kind`](../../src/tools.py#L61), and [`TOOLS` registry](../../src/tools.py#L93); MCP listing and call handlers (`../../src/mcp_server.py#L18 and #L29). **Product PR:** [#24](https://github.com/anakakhidze/goLocal-AI/pull/24) - **Merged commit:** `2ad9db5134ff8d1f498b47f09141cf943f6f4b61`.

**For the model (docstring):** “Return up to `limit` read-only catalog summaries for the exact requested kind.”

| Boundary | Contract |
|---|---|
| Effect / undo | Reads the curated event catalog. Nothing to undo; it makes no state changes. |
| Idempotent | Yes for unchanged catalog files. The recorded `event, limit=1` result is the same first event as the first row of `event, limit=3`; a separate duplicate-call measurement is not recorded. |
| Offered to | `tools_for()` offers read-only tools to callers; this tool needs no identity. |
| Identity from | `GOLOCAL_CALLER` is trusted launcher context for the MCP server; it is not an argument and is not passed into this public catalog lookup. |
| Touches | Reads `data/corpus/events/*.md` through `src/catalog.py`; shared executor writes a metadata-only audit line. No database, external URL, or user data. |
| Must never | Write catalog or user state, accept identity as a tool argument, or return source prose or filesystem paths. |

**Input.** `FindEventsByKind` inherits strict validation and `extra="forbid"` from `Contract` (`src/contracts.py`).

| Argument | Type | Constraint | Description shown to model |
|---|---|---|---|
| `kind` | `Literal["event", "venue"]` | Exactly the two kinds derived by the catalog over all 13 files; no other string accepted. | Catalog kind: `event` or `venue`. |
| `limit` | strict integer | Default `10`; inclusive range `1–10`; booleans and non-integers rejected. | Maximum results, 1 to 10. |

No user, account, or caller field is accepted. The output is `KindEventList`; every item is limited to `id`, `title`, `kind`, `source_url`, and `snapshot_date`. It contains no source text, paths, or internal catalog fields. The function filters the fixed catalog in its existing order and applies the validated limit.

**Expected failures.** `call_tool()` validates before calling the function. Invalid arguments produce the exact safe message `invalid arguments: <field>. Follow the listed schema; remove unknown fields.` (for example, `invalid arguments: kind. Follow the listed schema; remove unknown fields.`). Catalog-read failure produces `Event data is unavailable. Ask the maintainer to check the curated corpus; retry later.` Unexpected exceptions produce `Tool unavailable. Retry later or contact the maintainer; do not repeat the same request in a loop.` There is no not-found error: a valid kind with no matching records returns an empty list. No stack trace, raw input, or path is returned.

**MCP, audit, CI.** Both function calling and MCP use the shared registry and executor. `src/mcp_server.py` publishes the Pydantic input/output schemas; tests compare both doors. Each attempted call writes one private metadata-only audit line (UTC timestamp, safe tool name, caller hash, outcome/error code, latency), without arguments or result content. CI workflow `.github/workflows/ci.yml` runs `pytest` in job `test` on pull requests; repository protection must require that job for merge.

**Decision.** The earlier task direction was to wrap `get_event`; it was replaced before this tool was implemented with the distinct catalog-filtering function `find_events_by_kind`. I chose a summary allowlist so this tool can select records without exposing the source-backed details owned by `get_event_details`. That boundary is visible in `KindEventSummary` and its exact-field tests; it has no source-text field. There is no earlier checked-in implementation of this tool with a broader output, so I do not claim a removal diff.
