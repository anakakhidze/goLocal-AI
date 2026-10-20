"""Find free events in a date range. Standard library only; no network or model calls."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any


class EventDataError(ValueError):
    """Raised when an event record is malformed."""


@dataclass(frozen=True)
class Event:
    id: int
    title: str
    venue: str
    start: datetime  # timezone-aware; the local date is the date in its own offset
    price: float | None  # None means unknown, 0 means free
    source_url: str


def _text(record: dict[str, Any], field: str) -> str:
    value = record.get(field)
    if not isinstance(value, str) or not value.strip():
        raise EventDataError(f"field '{field}' must be a nonempty string")
    return value.strip()


def parse_event(record: dict[str, Any]) -> Event:
    """Validate one raw record and return an Event. Raises EventDataError if it is malformed."""
    event_id = record.get("id")
    if not isinstance(event_id, int) or isinstance(event_id, bool) or event_id <= 0:
        raise EventDataError("field 'id' must be a positive integer")

    try:
        start = datetime.fromisoformat(_text(record, "start"))
    except ValueError as error:
        raise EventDataError("field 'start' must be an ISO 8601 datetime") from error
    if start.tzinfo is None:
        raise EventDataError("field 'start' must include a UTC offset, for example +04:00")

    price = record.get("price")
    if price is not None:
        if isinstance(price, bool) or not isinstance(price, (int, float)) or price < 0:
            raise EventDataError("field 'price' must be null or a number of zero or more")
        price = float(price)

    source_url = _text(record, "source_url")
    if not source_url.startswith("https://"):
        raise EventDataError("field 'source_url' must be an HTTPS link")

    return Event(
        id=event_id,
        title=_text(record, "title"),
        venue=_text(record, "venue"),
        start=start,
        price=price,
        source_url=source_url,
    )


def load_events(records: list[dict[str, Any]]) -> list[Event]:
    """Validate every record. Rejects the whole list if any record is malformed or an ID repeats."""
    events = [parse_event(record) for record in records]
    seen: set[int] = set()
    for event in events:
        if event.id in seen:
            raise EventDataError(f"duplicate event id {event.id}")
        seen.add(event.id)
    return events


def find_free_events(events: list[Event], first_day: date, last_day: date) -> list[Event]:
    """Return events with price 0 whose local start date is between first_day and last_day, inclusive.

    Sorted by start time, then by id. Returns an empty list when nothing matches.
    """
    if first_day > last_day:
        raise ValueError("'from' must be on or before 'to'")
    matches = [
        event
        for event in events
        if event.price == 0 and first_day <= event.start.date() <= last_day
    ]
    return sorted(matches, key=lambda event: (event.start, event.id))
