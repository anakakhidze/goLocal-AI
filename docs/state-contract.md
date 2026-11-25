# State contract — individual HW2 tool slice

This documents the state this slice actually uses. It does not claim that the full
Lab 6 streaming/conversation-memory feature has been implemented.

| What | Why | Scope / lifetime | Written when | Deleted by | Location |
|---|---|---|---|---|---|
| Model messages and native thought-signature fields | Allow a bounded function-calling turn | One `act()` invocation; at most 3 model turns and 4 calls/turn | Only inside that requested turn | Function return releases the in-memory list | Local function variables |
| Caller context | Attribute the tool attempt; never select someone else's data | Current request / trusted MCP launch; no profile is retained | Server supplies it; never a tool argument | End request / stop server | Runtime only |
| Audit metadata | Verify execution and refusal gates | Local developer/CI runtime; not a user-profile memory | Once per attempted tool call | Maintainer removes local logs; CI temporary files expire | Ignored `logs/`, isolated test temp directories |
| Reviewed listing snapshots | Return source facts | Shared public corpus; explicit snapshot date | Human-reviewed repository change | Normal reviewed repository change | Versioned `data/corpus/events/` |

Never store raw caller IDs, tool arguments, user questions, native thought signatures,
model answers or credentials in logs. No automatically inferred preferences exist.
Audit logs are not a TTL-governed user memory store; no GET/DELETE-memory endpoint is claimed.

Tests: `test_valid_call_returns_a_typed_result_and_one_private_audit_line`,
`test_mcp_public_result_does_not_depend_on_a_forged_identity`, and the bounded-loop tests.
