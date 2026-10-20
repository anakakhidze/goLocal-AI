# Pattern Journal · Archil Sanikidze · Weeks 1–4

These entries were reconstructed on **20 October 2026** from my repository work and the event-source notes. Codex helped draft the wording; the concrete file and commit references below are the evidence. They do not claim that the team's planned RAG pipeline is already working.

## Week 1 · Context as Budget

**Evidence date: 6 October 2026 (initial goLocal-AI scaffold).** I used this pattern in `docs/spec.md` by limiting the first discovery slice to the user's request and a local event fixture, with no more than three recommendations and one external model call. I delegated help with the initial spec and agent guidance to Codex; the written acceptance criteria provide the check, and next time I would estimate actual prompt tokens before leaving the token budget marked `PENDING`.

## Week 2 · Spec Before Code

**Evidence date: 19 October 2026 (GoLocal discovery branch).** Before the shared implementation, I agreed the `parse_query`, `search_events` and `explain` responsibilities and the one-call Gemini limit with the team, then delegated the implementation to Codex. The function contracts and `tests/test_discovery.py` are the recorded checks on that code; next time I would settle the exact HTTP response shape before coding instead of leaving that contract open while functions were built.

## Week 3 · Uncertainty-Aware UX

**Evidence date: 19 October 2026 (event-source collection).** The supplied HARDHELL text and the linked listing did not support one unambiguous street address, so the corpus note preserves that uncertainty and this HW1 fixture omits the event. I delegated corpus structuring to Codex; the source note records the conflict, and next time I would record field-level evidence and uncertainty during collection, before data reaches a user-facing result.

## Week 4 · Grounded Generation

**Evidence date: 20 October 2026 (individual HW1 fixture and golden run).** I supplied real listing descriptions and source links for the team's intended RAG corpus, then delegated this smaller source-backed lookup to Codex. Three recorded CLI golden runs and a test requiring original `source_url` values check this feature's provenance; next I would run a separate RAG golden set against retrieval and refusal behavior, because this lookup does not itself prove that the team's RAG answers are grounded.
