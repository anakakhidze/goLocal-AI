"""Find up to three upcoming events in a dated, local listing snapshot.

No network or model call is made. The original listing is the authority for
current schedules and ticket availability.
"""

from __future__ import annotations

import argparse
from datetime import date, datetime
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit


FIXTURE = Path(__file__).resolve().parent / "data" / "events.json"
MAX_RESULTS = 3


def iso_date(value: str) -> date:
    """Parse only the public YYYY-MM-DD form, rejecting compact ISO variants."""
    try:
        parsed = date.fromisoformat(value)
        if parsed.isoformat() != value:
            raise ValueError("non-canonical date")
        return parsed
    except ValueError as exc:
        raise argparse.ArgumentTypeError("date must be YYYY-MM-DD") from exc


def load_snapshot(path: Path = FIXTURE) -> dict:
    """Validate the curated snapshot before any event reaches the result."""
    snapshot = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get("events"), list):
        raise ValueError("snapshot must contain an events list")
    try:
        iso_date(snapshot["snapshot_date"])
        if snapshot["time_zone"] != "Asia/Tbilisi":
            raise ValueError("unexpected time zone")
    except (KeyError, TypeError, argparse.ArgumentTypeError) as exc:
        raise ValueError("snapshot metadata is invalid") from exc

    seen_ids: set[str] = set()
    for event in snapshot["events"]:
        if not isinstance(event, dict):
            raise ValueError("event must be an object")
        try:
            for field in ("id", "title", "starts_at", "venue", "source_url"):
                if not isinstance(event[field], str) or not event[field].strip():
                    raise ValueError(f"event {field} is empty")
            start = datetime.strptime(event["starts_at"], "%Y-%m-%dT%H:%M")
            if start.strftime("%Y-%m-%dT%H:%M") != event["starts_at"]:
                raise ValueError("event starts_at is not canonical")
            source = urlsplit(event["source_url"])
            if source.scheme != "https" or not source.netloc:
                raise ValueError("event source_url must be an HTTPS URL")
            if event["id"] in seen_ids:
                raise ValueError("duplicate event id")
            seen_ids.add(event["id"])
        except (KeyError, TypeError) as exc:
            raise ValueError("event is missing a required field") from exc
    return snapshot


def find_events(
    on_or_after: date, venue: str | None = None, *, snapshot: dict | None = None
) -> list[dict]:
    """Return the next three records on/after a date, optionally at one venue."""
    if not isinstance(on_or_after, date) or isinstance(on_or_after, datetime):
        raise TypeError("on_or_after must be a date")
    if venue is not None and (not isinstance(venue, str) or not venue.strip()):
        raise ValueError("venue must be a nonempty string")

    data = load_snapshot() if snapshot is None else snapshot
    matches = [
        event
        for event in data["events"]
        if date.fromisoformat(event["starts_at"][:10]) >= on_or_after
        and (venue is None or event["venue"].casefold() == venue.strip().casefold())
    ]
    matches.sort(key=lambda event: (event["starts_at"], event["id"]))
    return matches[:MAX_RESULTS]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--on-or-after", required=True, type=iso_date, metavar="YYYY-MM-DD")
    parser.add_argument("--venue", help="exact venue name; case-insensitive")
    args = parser.parse_args(argv)
    if args.venue is not None and not args.venue.strip():
        parser.error("venue must not be blank")

    snapshot = load_snapshot()
    result = {
        "snapshot_date": snapshot["snapshot_date"],
        "time_zone": snapshot["time_zone"],
        "events": find_events(args.on_or_after, args.venue, snapshot=snapshot),
        "notice": "Historical snapshot; check each source_url for current details.",
    }
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
