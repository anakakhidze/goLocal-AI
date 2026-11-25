# Evidence · search_events · anakakhidze

## Golden cases (course format, `evals/tools/anakakhidze.yaml`, run by `tests/test_tool_golden.py`)

| id | Type | Case | Expected | Result |
|---|---|---|---|---|
| n1 | normal | Tbilisi music up to 30 GEL | ids `[paper-lantern-jazz, sunset-guitar]` | pass |
| n2 | normal | keyword `jazz` | ids `[paper-lantern-jazz]` | pass |
| n3 | normal | dates 2026-10-20 to 2026-10-22 | ids `[paper-lantern-jazz, rooftop-dance, color-and-light]` | pass |
| b1 | bad-input | city `Batumi` | refused; error contains `invalid arguments` and `city` | pass |
| a1 | adversarial | keyword `x' OR '1'='1` | refused; error contains `invalid arguments` and `keyword` | pass |

The expected ids were checked by hand against `data/demo_events.json`, not only against the code.

Local run, Python 3.14, Windows, on commit `ae4ff4d`: `python -m pytest tests -p no:cacheprovider -q` → **15 passed**
(5 golden cases, the same 5 through the MCP door, the MCP registration check, the five-case file check, and 3 log tests).

## Gate check: a weakened contract must fail

Run in a scratch copy, not on main. Two weakenings, each on its own:
- `extra="forbid"` changed to `extra="ignore"` (both models). Result: **2 failed, 13 passed**: the MCP registration check (`additionalProperties` no longer `false`), and the log test for a refused call. The adversarial case still fails to run, because the keyword pattern refuses the SQL text on its own.
- The keyword `pattern` removed. Result: **2 failed, 13 passed**: `test_tool_golden_case[anakakhidze:a1]` and `test_both_doors_agree[a1]`. The adversarial SQL text then runs instead of being refused.

This shows the tests catch both weakenings locally.

## CI runs (GitHub Actions, workflow `HW2 tool contract`)

- **Green run on the current product commit `ae4ff4d`:** https://github.com/anakakhidze/goLocal-AI/actions/runs/45706224737
  Product PR #17, `pull_request` event, conclusion `success`.
- **Previous green run on `4db1a0f` (the synthetic-data version):** https://github.com/anakakhidze/goLocal-AI/actions/runs/45703332573
- **Red run (CI failed on the pull request, current contract):** https://github.com/anakakhidze/goLocal-AI/actions/runs/45708853743/job/139537734360
  Throwaway PR #21 (`red-check-anakakhidze-3`, base `main`), with `extra="forbid"` changed to `extra="ignore"` in both models. Job `golden-cases` concluded **failure**. The local weakened check predicts 2 failing tests (the MCP registration check and the refused-call log test); confirm the count in the job log.
  Note: the merge button was blocked by the missing approval, not by this failing check. Branch protection on `main` requires one approving review but does not yet require the `golden-cases` status check. Until the repo owner adds that check, a failing CI run alone does not block a merge.

## What the red run taught me

Weakening `extra="forbid"` to `extra="ignore"` let an unknown field through instead of refusing it, and CI caught it on the pull request. The same change also broke the MCP registration check, which compares the input schema to `additionalProperties: false`. A rule that only exists on paper does nothing; the test that enforces it has to run on every pull request and block the merge.
