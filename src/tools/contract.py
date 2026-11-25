"""Contract for the search_events tool: input and output shapes, enforced in code.

Least privilege: the caller can filter events. The caller cannot name a user,
an account, a file, a URL or a query string. Unknown fields are refused.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

City = Literal["Tbilisi", "Batumi"]
Category = Literal["music", "film", "art", "sport", "talk", "other"]


class SearchEventsInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    city: City
    category: Category | None = None
    free_only: bool = False
    max_price_gel: float | None = Field(default=None, ge=0, le=500)
    limit: int = Field(default=5, ge=1, le=10)


class EventOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int = Field(ge=1)
    title: str
    venue: str
    start: str  # ISO 8601 with UTC offset
    price_gel: float | None
    source_url: str = Field(pattern=r"^https://")


INPUT_FIELDS = tuple(SearchEventsInput.model_fields)
