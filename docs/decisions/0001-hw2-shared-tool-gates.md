# Decision 0001 — one HW2 executor and exact MCP schemas

Date: 2026-11-23. Status: implemented on product branch; teammate review pending.

The course repository has individual HW1 work but no common tool/MCP/CI frame.
Archil's HW2 therefore adds the smallest reusable frame plus `get_event_details`.
The baseline `list_events` function is distinct from the personal detail tool.

The 13 existing GoLocal corpus files are copied byte-for-byte from implementation
commit `51aa2c276131ebd2f0ef1d7c78454926f3b05075`; no fictional facts are introduced.
Lookup reloads the versioned corpus each time and explicitly identifies it as
historical. No live ticket feed, current inventory, authentication or complete HTTP
backend is claimed. An allowlisted corpus enumeration is used instead of building
a path from the model's slug; the contract still rejects traversal before lookup.

Use the documented **MCP SDK 2.3 low-level `Server`** API, rather than the decorator
wrapper. This publishes the exact Pydantic schema, including `additionalProperties=false`,
and routes every accepted/refused tool call through the same audited `call_tool()`.
Some decorator-generated models ignore extra fields; the individual contract must not.
This is an SDK-level API choice, not a custom MCP protocol or private SDK patch.
Both in-process and stdio protocol tests verify the actual server.

Alternative: duplicate validation in separately typed MCP wrappers. Rejected because
schema drift and unlogged pre-body SDK refusals would weaken evidence.

Gemini 3.1 Flash-Lite is retained from the existing product, through its HTTP
OpenAI-compatible function-calling endpoint. No key is read from `.env`. Native
assistant messages, including provider reasoning metadata, are echoed in memory.
Offline CI uses fake HTTP/model responses and never needs a paid key.

CI adds required-job candidate `test`; the repo owner must enforce that status and
one teammate approval in GitHub settings. A green workflow alone does not prove enforcement.

References:
- https://py.sdk.modelcontextprotocol.io/v2/advanced/low-level-server/
- https://ai.google.dev/gemini-api/docs/openai
- Lecturer: Lab-5/HOMEWORK.md and Lab-7/HOMEWORK.md.
