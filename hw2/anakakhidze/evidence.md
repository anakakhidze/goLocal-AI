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

_To be redone on the current code. The earlier weakened-check numbers were for a separate package that has been removed from the product branch._

## Red run (CI must fail on a weakened contract)

_To be redone on the current code, on a throwaway branch with base `main`, and the failed run link pasted here._

## What the red run taught me

_To be written after the new red run._
