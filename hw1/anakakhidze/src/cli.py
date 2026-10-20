"""Command line: list free events in a date range as JSON.

Example (from the repository root):
    python hw1/anakakhidze/src/cli.py --from 2026-10-20 --to 2026-10-31

Exit codes: 0 success (an empty list is success), 1 malformed event data, 2 bad arguments.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from free_events import EventDataError, find_free_events, load_events

DEFAULT_FILE = Path(__file__).with_name("sample_events.json")


def _day(text: str) -> date:
    try:
        return date.fromisoformat(text)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"'{text}' is not a date in YYYY-MM-DD form") from error


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="List free events in a date range.")
    parser.add_argument("--from", dest="first_day", type=_day, required=True, help="first local start date, YYYY-MM-DD")
    parser.add_argument("--to", dest="last_day", type=_day, required=True, help="last local start date, YYYY-MM-DD")
    parser.add_argument("--file", type=Path, default=DEFAULT_FILE, help="JSON file with an array of event records")
    args = parser.parse_args(argv)

    if args.first_day > args.last_day:
        print("error: --from must be on or before --to", file=sys.stderr)
        return 2

    try:
        records = json.loads(args.file.read_text(encoding="utf-8"))
        if not isinstance(records, list):
            raise EventDataError("the file must contain a JSON array of event records")
        events = load_events(records)
    except (OSError, json.JSONDecodeError, EventDataError) as error:
        print(f"error: malformed event data: {error}", file=sys.stderr)
        return 1

    matches = find_free_events(events, args.first_day, args.last_day)
    output = [
        {
            "id": event.id,
            "title": event.title,
            "venue": event.venue,
            "start": event.start.isoformat(),
            "source_url": event.source_url,
        }
        for event in matches
    ]
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
