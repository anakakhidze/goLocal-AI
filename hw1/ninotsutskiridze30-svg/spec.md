# HW1 · Announcement text to event fields and routes

**Install, run, test** — Python 3.11+, PowerShell, from the repository root:
```powershell
python -m pip install --target hw1/ninotsutskiridze30-svg/src/.test-deps -r hw1/ninotsutskiridze30-svg/src/requirements.txt
$env:PYTHONPATH = (Resolve-Path hw1/ninotsutskiridze30-svg/src/.test-deps).Path
$env:Path = "$(Resolve-Path hw1/ninotsutskiridze30-svg/src/.test-deps/bin);$env:Path"
python hw1/ninotsutskiridze30-svg/src/cli.py "KIU Robotics Club, Open Build Night, Thursday 22 October 2026, 18:00, Lab B204" --today 2026-10-18 --rooms B204
pytest hw1/ninotsutskiridze30-svg -p no:cacheprovider
```

## Goal and users
Turn one campus event announcement into title, date, time, location and a review route, without prefilling unsupported guesses. **Club officer:** pastes an announcement and wants fields filled without wrong guesses. **Reviewer (a club officer checking drafts):** sees doubtful fields and reasons. Individual offline CLI; separate from the team application.

## Acceptance criteria
| ID | Script-decidable behavior |
|---|---|
| AC1 | Clean golden input returns `accepted`, title `Open Build Night`, date `2026-10-22`, time `18:00`, location `B204`; every populated field has `{value,evidence,confidence}` and exact substring evidence supporting its normalized value. |
| AC2 | Missing title/date/location or missing/nonmatching evidence gives `review`; affected fields have empty value and evidence, confidence 0. Invalid dates/times or unsupported values also give `review` and stay empty. Missing time alone is allowed. |
| AC3 | Date before explicit `today`, a stated weekday differing from the date, room absent from supplied canonical codes, or populated-field confidence <0.6 gives `confirm` with a flag and readable reason; exactly 0.6 does not trigger this flag. |
| AC4 | Validated `is_event=false` gives `rejected` and empty fields. Pydantic failure gives `review` and empty fields. Precedence: schema failure → non-event → unsafe/required field → soft flags → accepted. Confidence never bypasses evidence checks. |
| AC5 | `decide(extraction, source_text, today, rooms)` is pure; fake-extractor tests run without a key or real model. Optional model calls pass through `llm.py`, which logs model, tokens in/out, USD cost and latency; failed calls record unknown usage as null. |

## Context and constraints
`src/schema.py`: strict Pydantic shape. `decision.py`: normalization and routes. `extractor.py`: offline patterns and injectable extractor. `cli.py`: JSON output `{route,fields,flags}`; flags contain code, field, reason. `llm.py`: optional provider-neutral transport, environment key `EVENT_MODEL_API_KEY`, explicit rates, local ignored usage log. `test_routes.py`, `test_llm.py`, `conftest.py`, `requirements.txt`: verification/setup. No team imports, keys in files, or real personal data.

Offline scope: one English comma-separated announcement; named event types in `extractor.py`; ISO or day/month-name/year dates, 24-hour or AM/PM times, room codes like B204. Evidence is the field span itself. Supplied `today` and room set make decisions reproducible. Multiple weekdays conservatively flag any mismatch.

## Out of scope and verification
No live provider, web app, arbitrary natural-language understanding, multi-event announcements, year inference, time zones, room directory integration, or purchasing. CLI costs $0 in model usage. Tests exercise normalization, routes, blank required fields, schema errors, fake extraction and usage logging. Green means the test command exits 0. Run the three commands in `golden.md` yourself and record results.
