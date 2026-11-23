# GoLocal event-information loop — HW2 boundary

1. **Goal:** answer a person's event-detail question by listing IDs and reading the selected source snapshot.
2. **Allowed tools:** `list_events`, `get_event_details`; both are public reads. No general shell, URL fetcher, account writer or ticketing tool.
3. **Action that must wait for a yes:** buying/reserving a ticket or sending a recommendation to another person must require explicit human confirmation. These capabilities are deliberately **absent** from this slice, so the loop cannot execute them at all. Adding one requires a separate gate implementation and review.
4. **Budget:** at most 3 model turns and 4 tool calls per turn; stop visibly on exhaustion. Tool failures are observations, not reasons for unlimited retries.
5. **What a person sees:** event facts with original source URL, snapshot date and a warning to check current details. No output may say that a booking, purchase, save or message was completed.

Executable boundary: `tools_for()` offers only read-only tools;
`test_registry_exposes_only_public_reads` and the loop budget tests verify it.
This is **not** a claim that the team's full Lab 7 consequential-action loop or
`POST /plan/confirm` exists. The individual HW2 tool is read-only and needs no confirmation gate.
