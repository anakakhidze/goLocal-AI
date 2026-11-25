# Evidence · search_events · anakakhidze

## Golden cases (course format, `evals/tools/anakakhidze.yaml`, run by `tests/test_tool_golden.py`)

| id | Type | Case | Expected | Result |
|---|---|---|---|---|
| n1 | normal | free Tbilisi music | ids `[1]` | pass |
| n2 | normal | Batumi, limit 2 | ids `[7, 8]` | pass |
| n3 | normal | Tbilisi under 30 GEL, unknown price excluded | ids `[1, 2, 3, 5, 6]` | pass |
| b1 | bad-input | city `Kutaisi` | refused; error contains `invalid arguments` and `city` | pass |
| a1 | adversarial | extra `user_id` field | refused; error contains `invalid arguments` and `user_id` | pass |

Local run, Python 3.14, Windows, on commit `4db1a0f`: `python -m pytest tests -p no:cacheprovider -q` → **15 passed**
(5 golden cases, the same 5 through the MCP door, the MCP registration check, the five-case file check, and 3 log tests).

## Gate check: a weakened contract must fail

Run in a scratch worktree, not on main. In `src/tools/contract.py` I changed `extra="forbid"` to `extra="ignore"` (both models).
Result: **4 failed, 11 passed**:
- `test_tool_golden_case[anakakhidze:a1]`: the adversarial call ran instead of being refused.
- `test_both_doors_agree[a1]`: the direct door did not raise.
- `test_mcp_registers_the_tool_with_exact_fields`: `additionalProperties` is no longer `false`.
- `test_refused_call_is_logged_with_error_kind_only`: the refused call was logged as ok.

## CI runs (GitHub Actions, workflow `HW2 tool contract`)

- **Red run (CI failed on the pull request):** https://github.com/anakakhidze/goLocal-AI/actions/runs/45698715645/job/139502851273
  Throwaway PR #18 (`red-check-anakakhidze`), weakened to `extra="ignore"`. Three tests failed in that version of the tests; the local run above shows four, because the log tests were added later.
  Note: the merge button was blocked by the missing approval, not by this failing check. Branch protection on `main` requires one approving review but does not yet require the `golden-cases` status check. Until the repo owner adds that check, a failing CI run alone does not block a merge.
- **Green run on the product pull request (earlier commit `272442e`):** https://github.com/anakakhidze/goLocal-AI/actions/runs/45694038272/job/139486642833
- **Green run on the current commit `4db1a0f`:** _pending: add the link after CI runs on PR #17_

## What the red run taught me

Weakening `extra="forbid"` to `extra="ignore"` let the unknown `user_id` field through instead of refusing it,
and CI caught it on the pull request. The same change also broke the MCP registration check, which compares the
input schema to `additionalProperties: false`. A rule that only exists on paper does nothing; the test that
enforces it has to run on every pull request and block the merge.
