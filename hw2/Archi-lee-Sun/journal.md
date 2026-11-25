# Pattern Journal — Archil Sanikidze — Weeks 5, 6 and 7

**Prepared retrospectively on 23 November 2026.** These entries refer to the actual
HW2 implementation and tests created on that date, not attendance or completed work
on the original teaching-week dates. Codex helped implement and draft the material
at my request; automated checks below were run by Codex, while my own code explanation,
teammate review and individual submission remain my responsibility.

## Week 5 — Tool Contract — evidence date 2026-11-23

I delegated a distinct public `get_event_details` capability and the missing shared
MCP/executor frame, with a bounded slug and no caller identity in arguments.
Verification actually performed: 83 product tests and six real-executor golden cases,
including both MCP/function-calling doors; removing only the regex in red PR #15
caused the bad-input and traversal cases to fail on GitHub.
Next time I would establish required CI status checks with the Repo keeper before
starting the personal tool: the existing one-review rule alone does not prove a CI gate.

Evidence: `src/contracts.py`, `src/act.py`, `tests/test_tool_golden.py`,
[red PR #15](https://github.com/anakakhidze/goLocal-AI/pull/15),
[green run](https://github.com/anakakhidze/goLocal-AI/actions/runs/45137119115).

## Week 6 — Session State — evidence date 2026-11-23

The concrete state decision in `docs/state-contract.md` is that caller context and
native provider messages exist only within the requested turn; this public read tool
does not need a persistent user profile or automatically inferred preferences.
I delegated those boundaries to Codex, whose audit-log and identity-injection tests
verify hashed-only caller metadata, no raw question/arguments in logs, and rejection
of a forged user field through MCP; the full team's TTL store and streaming were not
built by this HW2 change.
Next time I would specify lifetime and a deletion path before introducing any
persistent personal memory, rather than treating browser saves as conversation state.

Evidence: `docs/state-contract.md`,
`test_valid_call_returns_a_typed_result_and_one_private_audit_line`,
`test_mcp_public_result_does_not_depend_on_a_forged_identity`.

## Week 7 — Supervised Autonomy Loop — evidence date 2026-11-23

The real boundary in `docs/agent-contract.md` permits only `list_events` and
`get_event_details`; buying/reserving a ticket or sending a recommendation must wait
for an explicit human yes, and none of those consequential tools is exposed here.
I delegated a bounded information loop: tests verify only public-read tools are
offered, tool errors reach the next model turn, and execution stops after three
model turns or an excessive batch; this does not claim a full Lab 7 confirmation endpoint.
Next time I would implement and test park → confirm → idempotent execution before
adding the first consequential tool; an answer saying “proposed” must never mean “done”.

Evidence: `docs/agent-contract.md`, `src/act.py`,
`test_registry_exposes_only_public_reads`,
`test_nonterminating_model_is_stopped_at_the_round_budget`,
`test_parallel_call_budget_stops_before_execution`.
