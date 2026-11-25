"""search_events: look up synthetic events by city, category and price.

Reads only data/synthetic_events.json (fixed path, not from the caller).
No network, no writes, no model calls.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from src.tools.contract import EventOut, SearchEventsInput

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "synthetic_events.json"


def _load() -> list[dict[str, Any]]:
    with DATA_PATH.open(encoding="utf-8") as handle:
        records = json.load(handle)
    if not isinstance(records, list):
        raise ValueError("synthetic event data must be a JSON array")
    return records


def search_events(request: SearchEventsInput) -> list[dict[str, Any]]:
    """Return matching events, sorted by start time then id, at most request.limit long.

    Unknown prices (null) never match a price filter, so with max_price_gel or
    free_only set they are excluded.
    """
    matches = []
    for record in _load():
        if record["city"] != request.city:
            continue
        if request.category is not None and record["category"] != request.category:
            continue
        price = record["price_gel"]
        if request.free_only and price != 0:
            continue
        if request.max_price_gel is not None and (price is None or price > request.max_price_gel):
            continue
        matches.append(record)

    matches.sort(key=lambda r: (datetime.fromisoformat(r["start"]), r["id"]))
    results = []
    for record in matches[: request.limit]:
        event = EventOut(
            id=record["id"],
            title=record["title"],
            venue=record["venue"],
            start=record["start"],
            price_gel=record["price_gel"],
            source_url=record["source_url"],
        )
        results.append(event.model_dump())
    return results
