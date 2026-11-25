# Evidence · search_events · anakakhidze

## Golden cases (run through `call_tool()` in `tests/test_tool_golden.py`)

| # | Case | Kind | Expected | Result |
|---|---|---|---|---|
| 1 | `free_tbilisi_music` | normal | ids `[1]` | pass |
| 2 | `batumi_limit_two` | normal | ids `[7, 8]` | pass |
| 3 | `tbilisi_under_30_gel_skips_unknown_price` | normal | ids `[1, 2, 3, 5, 6]` (event 4, unknown price, excluded) | pass |
| 4 | `unknown_city_is_refused` | bad input | error naming `city` | pass |
| 5 | `smuggled_identity_field_is_refused` | adversarial | error `Unexpected field 'user_id'` | pass |

Local run, Python 3.14, Windows: `python -m pytest tests -p no:cacheprovider -q` → **12 passed**
(5 golden cases, 5 golden cases through the MCP door, 1 registration check, and the golden file check).

## Gate check: a weakened contract must fail

Run in a scratch copy, not on main. In `src/tools/contract.py` I changed `extra="forbid"` to `extra="ignore"`.
Result: **3 failed, 9 passed**. The failures were `test_golden_case[smuggled_identity_field_is_refused]`,
`test_both_doors_agree[smuggled_identity_field_is_refused]`, and `test_mcp_registers_the_tool_with_exact_fields`
(`additionalProperties` is no longer false). This shows the tests catch the weakening locally.

## CI runs (GitHub Actions, workflow `HW2 tool contract`)

- **Red run (CI failed on the pull request):** https://github.com/anakakhidze/goLocal-AI/actions/runs/45698715645/job/139502851273
  Throwaway PR #18 (`red-check-anakakhidze`, weakened contract). Three tests failed.
  Note: the merge button was blocked by the missing approval, not by this failing check. Branch protection on `main` requires one approving review but does not yet require the `golden-cases` status check. Until the repo owner adds that required check, a failing CI run alone does not block a merge.
- **Green run on the real product pull request:** https://github.com/anakakhidze/goLocal-AI/actions/runs/45694038272/job/139486642833
  Product PR #17 (`slice-hw2-anakakhidze`). The `golden-cases` job passed.

## What the red run taught me

Weakening `extra="forbid"` to `extra="ignore"` let the unknown `user_id` field through instead of refusing it,
and CI caught it on the pull request. The same change also broke the MCP registration check, which compares the
input schema to `additionalProperties: false`. A rule that only exists on paper does nothing; the test that
enforces it has to run on every pull request and block the merge.
