"""One executable input contract for the function-calling and MCP doors."""
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


EventId = Annotated[str, Field(
    min_length=1, max_length=64,
    description="Exact public listing slug returned by list_events; never a path or URL.",
)]
Limit = Annotated[int, Field(strict=True, ge=1, le=20, description="Maximum results, 1 to 20.")]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class GetEventDetails(Contract):
    """Read a source-backed event snapshot. Does not book, buy, save, or contact anyone."""
    event_id: EventId


class ListEvents(Contract):
    """List available event snapshot identifiers, not live ticket inventory. Reads only."""
    limit: Limit = 5
