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
Result: **3 failed, 9 passed**. The failures were the adversarial case through `call_tool()`, the adversarial
case through the MCP door, and the MCP registration check (`additionalProperties` is no longer false).
This shows the tests catch the weakening locally.

## CI runs (GitHub Actions, workflow `HW2 tool contract`)

- **Red run that blocked a merge:** _to be filled in_ (link: ...). Steps: on a throwaway branch,
  weaken the contract as above, push, open a pull request, watch CI turn red, copy the link here,
  close the pull request without merging, and delete the branch.
- **Green run on the real product pull request:** _to be filled in_ (link: ...).

## What the red run taught me

_To be written after the red run: one paragraph in my own words._
