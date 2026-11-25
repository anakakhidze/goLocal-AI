"""Contract for the search_events tool: input and output shapes, enforced in code.

Least privilege: the caller can filter events. The caller cannot name a user,
an account, a file, a URL, or SQL. Unknown fields are refused.
"""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

# Canonical categories from GoLocal's normalization.py.
Category = Literal["music", "nightlife", "exhibition", "theatre", "workshop", "technology",
                   "sports", "festival", "market", "family", "talk", "film", "food", "social", "other"]


class SearchEventsInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    city: Literal["Tbilisi"]
    category: Category | None = None
    keyword: str | None = Field(default=None, pattern=r"^[A-Za-z][A-Za-z ]{0,39}$")
    max_price_gel: float | None = Field(default=None, ge=0, le=500)
    start_date: date | None = None
    end_date: date | None = None
    limit: int = Field(default=5, ge=1, le=12)

    @model_validator(mode="after")
    def window_is_ordered(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class EventOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    external_id: str
    title: str
    venue_name: str
    start: str  # ISO 8601 with UTC offset
    end: str
    price_min: str | None  # decimal string; null means unknown
    price_max: str | None
    currency: str | None
    source_url: str = Field(pattern=r"^https://")


INPUT_FIELDS = tuple(SearchEventsInput.model_fields)
