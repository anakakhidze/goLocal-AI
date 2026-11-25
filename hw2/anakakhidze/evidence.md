# Evidence · search_events · anakakhidze

## Golden cases (course format, `evals/tools/anakakhidze.yaml`, run by the shared runner `tests/test_tool_golden.py`)

| id | Type | Case | Expected | Result |
|---|---|---|---|---|
| n1 | normal | Tbilisi music up to 30 GEL | `event_ids` `[paper-lantern-jazz, sunset-guitar]` | pass |
| n2 | normal | keyword `jazz` | `event_ids` `[paper-lantern-jazz]` | pass |
| n3 | normal | dates 2026-10-20 to 2026-10-22 | `event_ids` `[paper-lantern-jazz, rooftop-dance, color-and-light]` | pass |
| b1 | bad-input | city `Batumi` | refused; error contains `invalid arguments` and `city` | pass |
| a1 | adversarial | keyword `x' OR '1'='1` | refused; error contains `invalid arguments` and `keyword` | pass |

The expected ids were checked by hand against `data/demo_events.json`, not only against the code.

Local run, Python 3.14, Windows, in a virtual environment with `requirements-hw2.txt` (MCP SDK 2.3.0), on commit `5cc4df6`:
`python -m pytest -p no:cacheprovider tests` → **97 passed**. This includes Archil's cases, our 5 golden cases through the same runner, the filter checks in `tests/test_search_events.py`, and the shared MCP registration check.

## CI runs (GitHub Actions, workflow `ci`, job `test`)

- **Product PR #17, commit `5cc4df6`, `pull_request` event:** https://github.com/anakakhidze/goLocal-AI/actions/runs/45712404135
  Job `test`: completed, **success**.

## Gate check: a weakened contract must fail

Run in a scratch copy of commit `5cc4df6`. The `SearchEvents` model config was changed to `extra="ignore"`, placed after the docstring.
Result: **1 failed, 96 passed**: `tests/test_mcp.py::test_exact_both_doors_schema_including_additional_properties`. The adversarial golden case still refuses the SQL text, because the keyword pattern refuses it on its own.

## Red run (CI fails on a weakened contract)

- **Red run on the pull request, throwaway branch `red-check-anakakhidze-4`, base `main`, commit `0dd1948`:** https://github.com/anakakhidze/goLocal-AI/actions/runs/45713268078
  Job `ci / test`: **failure**. The same commit's push run also failed: https://github.com/anakakhidze/goLocal-AI/actions/runs/45713199871
  Expected: 1 failing test (the exact-schema MCP check). The job log has not been read; confirm the count there.
  To do: close the PR without merging and delete the branch `red-check-anakakhidze-4`.
  Note: the merge button is blocked by the missing approval, not by this failing check. Branch protection on `main` requires one approval but does not yet require the `test` status check. Until the repo owner adds that check, a failing CI run alone does not block a merge.

## What the red run taught me

A rule in the contract only protects the product if a test enforces it. Weakening `extra="forbid"` to `extra="ignore"` removes the schema rule that tells clients no extra fields are allowed, and the MCP exact-schema test catches that. The adversarial SQL case stayed refused, because a separate keyword pattern covers it, so each rule needs its own test.
