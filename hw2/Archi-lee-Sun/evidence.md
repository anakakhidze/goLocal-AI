# HW2 verification evidence — Archi-lee-Sun

Recorded on **23 November 2026**. Results below were actually executed locally and
on GitHub; pending submission controls are explicitly separated from implemented code.

## Product and reproduction

- [Product PR #14](https://github.com/anakakhidze/goLocal-AI/pull/14), branch `slice-13-hw2-Archi-lee-Sun`.
- Product commit: `7dd52f91a86fdcd6c8cac038e14bda2934f360fc`.
- [Golden YAML](https://github.com/anakakhidze/goLocal-AI/blob/7dd52f91a86fdcd6c8cac038e14bda2934f360fc/evals/tools/Archi-lee-Sun.yaml).
- [Actual six-case JSON report](https://github.com/anakakhidze/goLocal-AI/blob/7dd52f91a86fdcd6c8cac038e14bda2934f360fc/evals/results/2026-11-23-Archi-lee-Sun-tools.json).
- [Setup / host / model runbook](https://github.com/anakakhidze/goLocal-AI/blob/7dd52f91a86fdcd6c8cac038e14bda2934f360fc/docs/HW2-RUNBOOK.md).

From the product checkout, install `requirements-hw2.txt` in a venv, then:

```text
python -m pytest -q tests
python -m pytest -q hw1/Archi-lee-Sun
python -m evals.run_tool_golden
python -m src.cli mcp-smoke
```

Actual local results: **83 product tests passed**, **13 existing personal HW1 tests
passed**, **6/6 golden cases passed**, and the MCP client listed both tools and
successfully called `get_event_details`. `pip check` found no broken requirements.
The tests include a separate stdio server subprocess, not just a direct function mock.
Test and tool evaluation calls use **no model, key, paid service or ticket-site access**.

## Personal golden cases

All six run in `tests/test_tool_golden.py` through production `call_tool()`, inside
GitHub job **`test`**. `n3` is a normal, expected world-state refusal.

| ID | Type / call | Expected | Actual result | Pass |
|---|---|---|---|---|
| n1 | Visitor; `event_id=valerian-shiukashvili` | Selected record and trusted source/date | `ok=true`; original TKT URL; snapshot `2026-10-19`; `live_verified=false` | yes |
| n2 | Signed-in test caller; `event_id=hardhell` | Same public-source contract, uncertainty retained | `ok=true`; `event_id=hardhell`; entrance caveat retained, no invented street number | yes |
| n3 | `event_id=event-that-does-not-exist` | Refuse without fabrication; recovery instruction | `tool_failure`; “Event not found. Call list_events…” | yes |
| b1 | `event_id="Valerian Concert"` | Reject title before function/catalog access | `invalid_arguments`; error names `event_id` | yes |
| a1 | `event_id="../../.env"` | Reject traversal before function/catalog access | `invalid_arguments`; error names `event_id`; no input-selected file read | yes |
| a2 | Valid ID plus `user_id=test-user-b` | Refuse model-selected identity | `invalid_arguments`; error names `user_id` | yes |

Separate spy tests assert that invalid input never reaches the function. Other tests
cover strict types/limits, duplicate JSON keys, unknown tool, per-turn allowlists,
sanitized failures, private audit logs, repeatable read/no corpus write, and model budgets.
MCP tests compare the **entire** input schema, including `additionalProperties=false`,
and verify success, extra-field/traversal refusals, error messages and audit lines.

## Actual green GitHub CI

- [Product PR green run — 45137119115](https://github.com/anakakhidze/goLocal-AI/actions/runs/45137119115), event `pull_request`, commit `7dd52f9`.
- [Successful job `test`](https://github.com/anakakhidze/goLocal-AI/actions/runs/45137119115/job/137565946256).
- GitHub log: `83 passed in 1.51s`; existing HW1 regression step: `13 passed in 0.16s`.
- Dependency installation, product/golden tests, HW1 regression and JUnit artifact upload all succeeded on Ubuntu/Python 3.11.
- [Independent push run — 45137044540](https://github.com/anakakhidze/goLocal-AI/actions/runs/45137044540) also succeeded.

## Actual red contract-regression CI

- [Throwaway PR #15 — closed, never merged](https://github.com/anakakhidze/goLocal-AI/pull/15).
- Branch `hw2-Archi-lee-Sun-red`; mutation commit `414b09eacb9b1c6f82d6c60670886a70a8b6a364`.
- The **only mutation relative to the product commit** removes the `EventId` pattern
  in `src/contracts.py`. Tests, golden expectations and all other bounds are unchanged.
- [Red PR run — 45137340632](https://github.com/anakakhidze/goLocal-AI/actions/runs/45137340632).
- [Failed job `test`](https://github.com/anakakhidze/goLocal-AI/actions/runs/45137340632/job/137566657466): **17 failed, 66 passed**.
- Crucially, `test_tool_golden_case[Archi-lee-Sun:b1]` and `[Archi-lee-Sun:a1]`
  failed: expected `invalid arguments`, received the later `Event not found` refusal.
  Contract and MCP regression tests failed for the same weakening. This was a real
  contract-regression failure, not an installation/network failure.
- PR #15 was closed with `merged=false`; its remote branch was deleted. The mutation
  was never applied to `main` or the product branch.

**What the red run taught me.** The corpus dictionary's “not found” behavior was a
second defense, not proof of input validation. Removing the pattern allowed a title
and path-like input past the boundary even though lookup still did not construct an
input-derived path. The golden cases assert the specific early-refusal behavior,
so a future refactor cannot quietly rely on accidental absence from today's data.
No test was weakened to obtain green.

## Merge-blocking evidence: important remaining gap

The GitHub API reported `mergeable_state=blocked` for both PRs. However, the active
ruleset **Protect main branch** (ID `24660276`) currently enforces **one approving
review**, deletion prevention and non-fast-forward prevention, **not a required CI
status**. Therefore the observed blocked state does **not** prove that red CI itself
blocked a merge. The account used here (`Archi-lee-Sun`) has push permission but no
repository-admin permission; it cannot finish that owner-only setting.

**Repo keeper action:** Settings → Rules → Rulesets → Protect main branch → require
status checks → select **`test`**; keep the required teammate approval. Then repeat
the same throwaway mutation against the enforced rule and preserve the blocked-merge
evidence before closing/deleting that new red branch. This part of the lecturer's
verification criterion remains incomplete until performed. A red workflow alone is
not presented as full compliance.

## Remaining submission / personal boundaries

- [ ] A teammate reviews and merges product PR #14, including Repo keeper review of `.github/`.
- [ ] GitHub requires job `test`; a red run is demonstrated to block merge because of that check.
- [ ] Product tests and personal golden cases pass on `main` after merge.
- [ ] The separate individual write-up PR is approved/merged; its diff stays inside `hw2/Archi-lee-Sun/`.
- [ ] The individual Teams submission form is completed with merged-folder and product-PR links.

An actual MCP SDK client/stdio host was exercised, but no interactive Claude/Cursor
model answer is claimed. `GOOGLE_API_KEY` was not configured in the execution process;
the optional Gemini adapter was verified with fake HTTP responses, including usage
logging and preserved reasoning metadata. No key was read from `.env`.

The journal is transparently reconstructed on 23 November from this work. It does
not claim attendance or personal verification on earlier teaching-week dates.
The full team's streaming/state/confirmation endpoint and frontend integration are
outside this individual read-only tool and are not claimed as completed.
