"""search_events: look up GoLocal's fictional demo events by city, category, keyword, budget and dates.

This is a Python reimplementation of the filter rules in GoLocal's
src/golocal_data/discovery.py `search_events` (SQL). It reads only
data/demo_events.json (a fixed path the caller cannot change). No database,
no network, no model calls.

Fixture times are local to Asia/Tbilisi (UTC+4, no daylight saving), anchored at
the seed date below, the same default GoLocal's seed script uses.
"""

from __future__ import annotations

import json
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

from src.tools.contract import EventOut, SearchEventsInput

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "demo_events.json"
TBILISI = timezone(timedelta(hours=4))
SEED_DATE = date(2026, 10, 19)  # GoLocal seed default: day_offset 1 is the day after this
SOURCE_URL = "https://example.com/golocal-demo/"  # GoLocal demo.py SOURCE_URL


def _load() -> list[dict[str, Any]]:
    with DATA_PATH.open(encoding="utf-8") as handle:
        records = json.load(handle)
    if not isinstance(records, list) or len(records) != 25:
        raise ValueError("demo fixture must hold exactly 25 records")
    if len({record["external_id"] for record in records}) != len(records):
        raise ValueError("demo fixture identifiers must be unique")
    return records


def _start_end(record: dict[str, Any]) -> tuple[datetime, datetime]:
    day = SEED_DATE + timedelta(days=record["day_offset"])
    start = datetime.combine(day, time.fromisoformat(record["start_local"]), TBILISI)
    end = datetime.combine(day, time.fromisoformat(record["end_local"]), TBILISI)
    return start, end


def search_events(request: SearchEventsInput) -> list[dict[str, Any]]:
    """Return matching fictional events, sorted by start time then external_id, at most request.limit."""
    budget = Decimal(str(request.max_price_gel)) if request.max_price_gel is not None else None
    keyword = request.keyword.casefold() if request.keyword else None
    matches = []
    for record in _load():
        start, end = _start_end(record)
        if record["category"] != request.category and request.category is not None:
            continue
        if keyword and keyword not in record["title"].casefold() and keyword not in record["description"].casefold():
            continue
        if budget is not None:
            # A budget excludes unknown prices and other currencies.
            if record["price_min"] is None or record["currency"] != "GEL" or Decimal(record["price_min"]) > budget:
                continue
        if request.start_date and start.date() < request.start_date:
            continue
        if request.end_date and start.date() > request.end_date:
            continue
        matches.append((start, record, end))

    matches.sort(key=lambda item: (item[0], item[1]["external_id"]))
    results = []
    for start, record, end in matches[: request.limit]:
        event = EventOut(
            external_id=record["external_id"],
            title=record["title"],
            venue_name=record["venue_name"],
            start=start.isoformat(),
            end=end.isoformat(),
            price_min=record["price_min"],
            price_max=record["price_max"],
            currency=record["currency"],
            source_url=SOURCE_URL + record["external_id"],
        )
        results.append(event.model_dump())
    return results
