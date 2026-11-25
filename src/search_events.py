"""HW2 · search_events: find GoLocal's fictional demo events by city, category, keyword, budget and dates.

This is a Python reimplementation of the filter rules in GoLocal's
src/golocal_data/discovery.py `search_events` (SQL). It reads only data/demo_events.json
(a fixed path the caller cannot change). No database, no network, no model calls.

Fixture times are local to Asia/Tbilisi (UTC+4, no daylight saving), anchored at the
seed date below, the same default GoLocal's seed script uses.
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .contracts import Contract

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "demo_events.json"
TBILISI = timezone(timedelta(hours=4))
SEED_DATE = date(2026, 10, 19)  # GoLocal seed default: day_offset 1 is the day after this
SOURCE_URL = "https://example.com/golocal-demo/"  # GoLocal demo.py SOURCE_URL
NOTICE = "Fictional GoLocal demo fixture, not live ticket data. Check dates and prices with the source."

Category = Literal["music", "nightlife", "exhibition", "theatre", "workshop", "technology",
                   "sports", "festival", "market", "family", "talk", "film", "food", "social", "other"]
DATE_TEXT = r"^\d{4}-\d{2}-\d{2}$"


class SearchEvents(Contract):
    """Find fictional GoLocal demo events in Tbilisi by category, keyword, budget and date window. Reads only."""
    city: Literal["Tbilisi"]
    category: Category | None = None
    keyword: str | None = Field(default=None, pattern=r"^[A-Za-z][A-Za-z ]{0,39}$",
                                description="Word to find in the title or description; letters and spaces only.")
    max_price_gel: float | None = Field(default=None, ge=0, le=500,
                                        description="Highest price in GEL. Unknown prices never match.")
    start_date: str | None = Field(default=None, pattern=DATE_TEXT,
                                   description="First local date to include, YYYY-MM-DD.")
    end_date: str | None = Field(default=None, pattern=DATE_TEXT,
                                 description="Last local date to include, YYYY-MM-DD; not before start_date.")
    limit: int = Field(default=5, ge=1, le=12, description="How many events to return, 1 to 12.")

    @model_validator(mode="after")
    def dates_are_real_and_ordered(self):
        start = date.fromisoformat(self.start_date) if self.start_date else None
        end = date.fromisoformat(self.end_date) if self.end_date else None
        if start and end and end < start:
            raise ValueError("end_date must be on or after start_date")
        return self


class EventRow(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    external_id: str
    title: str
    venue_name: str
    start: str  # ISO 8601 with the Tbilisi offset
    end: str
    price_min: str | None  # decimal string; null means unknown
    price_max: str | None
    currency: str | None
    source_url: str = Field(pattern=r"^https://")


class SearchEventsResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    event_ids: list[str]
    events: list[EventRow]
    notice: str = NOTICE


def _load() -> list[dict]:
    with DATA_PATH.open(encoding="utf-8") as handle:
        records = json.load(handle)
    if not isinstance(records, list) or len(records) != 25:
        raise ValueError("demo fixture must hold exactly 25 records")
    if len({record["external_id"] for record in records}) != len(records):
        raise ValueError("demo fixture identifiers must be unique")
    return records


def _start_end(record: dict) -> tuple[datetime, datetime]:
    day = SEED_DATE + timedelta(days=record["day_offset"])
    start = datetime.combine(day, time.fromisoformat(record["start_local"]), TBILISI)
    end = datetime.combine(day, time.fromisoformat(record["end_local"]), TBILISI)
    return start, end


def search_events(args: SearchEvents) -> SearchEventsResult:
    """Return matching fictional events, sorted by start time then external_id, at most args.limit."""
    budget = Decimal(str(args.max_price_gel)) if args.max_price_gel is not None else None
    keyword = args.keyword.casefold() if args.keyword else None
    start_day = date.fromisoformat(args.start_date) if args.start_date else None
    end_day = date.fromisoformat(args.end_date) if args.end_date else None
    matches = []
    for record in _load():
        start, end = _start_end(record)
        if args.category is not None and record["category"] != args.category:
            continue
        if keyword and keyword not in record["title"].casefold() and keyword not in record["description"].casefold():
            continue
        if budget is not None:
            # A budget excludes unknown prices and other currencies.
            if record["price_min"] is None or record["currency"] != "GEL" or Decimal(record["price_min"]) > budget:
                continue
        if start_day and start.date() < start_day:
            continue
        if end_day and start.date() > end_day:
            continue
        matches.append((start, record, end))

    matches.sort(key=lambda item: (item[0], item[1]["external_id"]))
    events = [
        EventRow(
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
        for start, record, end in matches[: args.limit]
    ]
    return SearchEventsResult(event_ids=[event.external_id for event in events], events=events)
