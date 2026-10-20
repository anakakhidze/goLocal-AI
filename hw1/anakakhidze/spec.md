# HW1 spec · Free events in a date range

Owner: anakakhidze · Feature: find free events between two dates

## Run and test (from the repository root)

- Install the test tool once: `python -m pip install pytest`
- List free events: `python hw1/anakakhidze/src/cli.py --from 2026-10-20 --to 2026-10-31`
- Run tests: `python -m pytest hw1/anakakhidze -p no:cacheprovider`

Python 3.10 or newer. No API keys, no network access, no model calls.

## Goal and users

Someone planning a week in Tbilisi wants a short, dated list of events that cost nothing, with links to the original listings. They give a date range and get back events whose price is 0, sorted by start time. The data is a local, fictional snapshot (`src/sample_events.json`).

## Acceptance criteria

1. Events with price `0` whose local start date is between `--from` and `--to` (inclusive) are returned, sorted by start time, then by id.
2. Events with price `null` (unknown) or above `0` are never returned.
3. When nothing matches, the command prints `[]` and exits with code `0`.
4. A start date after the end date, or a date not in `YYYY-MM-DD` form, prints an error and exits with code `2`, with no event output.
5. A record with a missing or blank title, venue or start, a start without a UTC offset, a negative or non-numeric price, or a non-HTTPS `source_url` makes the command print an error and exit with code `1`. Duplicate ids also exit with code `1`.
6. Successful output is UTF-8 JSON, an array of objects with exactly the fields `id`, `title`, `venue`, `start` (ISO 8601 with offset) and `source_url`.
7. The tests run offline and pass with `python -m pytest hw1/anakakhidze`.

## Context list

- `src/free_events.py`: validation (`parse_event`, `load_events`) and the filter (`find_free_events`). Standard library only.
- `src/cli.py`: command line; reads the JSON file, prints JSON, sets exit codes.
- `src/sample_events.json`: seven fictional records. Every title says "(fictional)" and every link points to `example.com`.
- `src/test_free_events.py`: unit tests for the filter and validation, plus command line tests with exit codes.

## Out of scope

Live scraping or any real ticket site; time zone conversion (dates use each event's own offset); pagination; saving results; a web page; personal preferences; model calls; ticket purchasing.
