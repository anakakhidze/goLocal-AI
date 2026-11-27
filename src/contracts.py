"""One executable input contract for the function-calling and MCP doors."""
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


EventId = Annotated[str, Field(
    min_length=1, max_length=64, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    description="Exact public listing slug returned by list_events; never a path or URL.",
)]
Limit = Annotated[int, Field(strict=True, ge=1, le=20, description="Maximum results, 1 to 20.")]
EventKind = Literal["event", "venue"]
FindLimit = Annotated[int, Field(strict=True, ge=1, le=10, description="Maximum results, 1 to 10.")]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class GetEventDetails(Contract):
    """Read a source-backed event snapshot. Does not book, buy, save, or contact anyone."""
    event_id: EventId


class FindEventsByKind(Contract):
    """Find catalog records of one supported kind. Returns a short read-only summary; use the source URL for details."""
    kind: EventKind = Field(description='Catalog kind: "event" or "venue".')
    limit: FindLimit = 10


class ListEvents(Contract):
    """List available event snapshot identifiers, not live ticket inventory. Reads only."""
    limit: Limit = 5
