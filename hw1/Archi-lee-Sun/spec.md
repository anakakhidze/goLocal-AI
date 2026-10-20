# HW1 spec · Upcoming events from a dated listing snapshot

**Owner:** Archil Sanikidze (`Archi-lee-Sun`) · **Snapshot:** 19 October 2026

- **Run from repo root (Python 3.10+):** `python hw1/Archi-lee-Sun/src/find_events.py --on-or-after 2026-10-20`
- **Install test tool:** `python -m pip install pytest`
- **Verify:** `python -m pytest hw1/Archi-lee-Sun` (green means every test passes; no API key needed).

## Goal and users

People choosing cultural events in Tbilisi need a short chronological list with links to the original listings. Given a date and optional venue, this independent CLI searches a bundled snapshot and returns up to three events.

## Acceptance criteria

1. `--on-or-after YYYY-MM-DD` includes events on that local date and later. Return at most three unique records, sorted by start date/time and then ID.
2. `--venue` matches the full venue name, ignoring case and surrounding spaces. No matches return `"events": []` with exit code 0.
3. Each result has a nonempty title, local start time, venue, and fixture-backed HTTPS `source_url`. UTF-8 JSON output includes `snapshot_date`, `Asia/Tbilisi`, and a notice to check current details at the source.
4. Invalid dates and blank venues exit with code 2 and an error. Malformed fixture records and duplicate IDs fail validation before results are returned.
5. Lookup works with network access blocked: zero site or model calls and zero model API cost.

## Context list and constraints

- Inputs: date and optional venue; data: six dated records in `src/data/events.json`, transcribed from public event listings on 19 October 2026.
- Display facts come only from the fixture. No live scrape, model, team database, inferred price, or ticket availability check. The snapshot may become stale.

## Verification, risk, and out of scope

Tests cover sorting independent of fixture order, filtering, errors, duplicate data, and blocked network access. `golden.md` records three actual CLI runs. Listings can change; the snapshot date, original `source_url`, and notice tell users where to verify details. Live search, purchases, personalized ranking, and a web endpoint are outside this slice.
