# Pattern Journal — ninotsutskiridze30-svg

These entries were written on 2026-11-27, retrospectively from the repository and test evidence. They do not claim attendance or work on earlier dates.

### Week 5 — Tool Contract — 2026-11-27
**Where I used it:** `src/contracts.py`, `tests/test_contracts.py`, and product PR #24. **What I noticed:** The two valid catalog kinds are derived from the 13 files, so writing a fixed enum alone would not keep it aligned with the catalog. The drift test makes that relationship explicit, while the extra-`user_id` spy case verifies rejection happens before the tool function runs. **Do differently:** I would define the accepted values and the test that ties them to the data together, before wiring the function into the registry.

### Week 6 — Session State — 2026-11-27
**Where I used it:** `src/act.py`, where `act()` creates a local `messages` list for one question and passes it through its model turns. The list is scoped to that call and is not persisted as a user session. **What I noticed:** Temporary conversation context and caller identity have different sources and lifetimes; the executor gets caller context separately, while tool arguments contain no user or account field. **Do differently:** Before adding cross-request memory, I would document exactly what is remembered, for whom, and for how long, then test that scope instead of assuming local prompt history persists.

### Week 7 — Supervised Autonomy Loop — 2026-11-27
**Where I used it:** The loop in `src/act.py` takes a user question, allows at most three model rounds and four calls per round, and invokes registered tools through the shared executor. There is no tool in `NEEDS_YES`: the registered tools are read-only, including `find_events_by_kind` in `src/tools.py`; no consequential action tool was built for this task. **What I noticed:** A call budget limits repeated tool use, but it is not a human confirmation gate; that distinction matters if the product later adds an action. **Do differently:** I would keep a future write or external-action tool out of the offered registry until its separate human approval step and refusal tests are in place.
