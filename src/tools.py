"""Product functions and their shared registry. Neither capability changes user state."""
from dataclasses import dataclass
from datetime import date
from typing import Callable

from pydantic import BaseModel, ConfigDict

from .catalog import CatalogError, EventDetails, load_catalog
from .contracts import Contract, EventId, EventKind, FindEventsByKind, GetEventDetails, ListEvents
from .search_events import SearchEvents, search_events


class ToolFailure(Exception):
    """Expected, actionable failure safe to return to the model."""


class EventSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    event_id: str
    title: str
    snapshot_date: str


class EventList(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    events: list[EventSummary]
    notice: str = "Identifiers from historical snapshots; call get_event_details and verify the original source."


class KindEventSummary(BaseModel):
    """Public fields returned by find_events_by_kind; source prose and storage metadata are omitted."""
    model_config = ConfigDict(extra="forbid", frozen=True)
    id: EventId
    title: str
    kind: EventKind
    source_url: str
    snapshot_date: date


class KindEventList(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    events: list[KindEventSummary]


def _catalog():
    try:
        return load_catalog()
    except CatalogError as exc:
        raise ToolFailure(str(exc)) from exc


def get_event_details(args: GetEventDetails) -> EventDetails:
    if not isinstance(args, GetEventDetails):
        raise ToolFailure("Use the get_event_details contract with an event_id from list_events.")
    event = _catalog().get(args.event_id)
    if event is None:
        raise ToolFailure("Event not found. Call list_events and use one of its exact event_id values; do not guess.")
    return event


def find_events_by_kind(args: FindEventsByKind) -> KindEventList:
    """Return up to `limit` read-only catalog summaries for the exact requested kind."""
    if not isinstance(args, FindEventsByKind):
        raise ToolFailure('Use kind "event" or "venue" and a limit from 1 to 10.')
    events = [KindEventSummary(id=record.event_id, title=record.title, kind=record.kind,
                               source_url=record.source_url, snapshot_date=record.snapshot_date)
              for record in _catalog().values() if record.kind == args.kind]
    return KindEventList(events=events[:args.limit])


def list_events(args: ListEvents) -> EventList:
    if not isinstance(args, ListEvents):
        raise ToolFailure("Use the list_events contract with a limit from 1 to 20.")
    events = [EventSummary(event_id=e.event_id, title=e.title, snapshot_date=e.snapshot_date.isoformat())
              for e in _catalog().values() if e.kind == "event"]
    return EventList(events=events[:args.limit])


@dataclass(frozen=True)
class Tool:
    name: str
    args: type[Contract]
    run: Callable[[Contract], BaseModel]
    read_only: bool = True

    def schema(self) -> dict:
        return {"type": "function", "function": {
            "name": self.name, "description": self.args.__doc__.strip(),
            "parameters": self.args.model_json_schema(),
        }}


TOOLS = {t.name: t for t in (
    Tool("list_events", ListEvents, list_events),  # common frame, not Archil's HW2
    Tool("get_event_details", GetEventDetails, get_event_details),  # Archi-lee-Sun's HW2
    Tool("find_events_by_kind", FindEventsByKind, find_events_by_kind),  # ninotsutskiridze30-svg's HW2
    Tool("search_events", SearchEvents, search_events),  # anakakhidze's HW2
)}


def tools_for(caller: str | None) -> dict[str, Tool]:
    """Public reads need no account. Future private/write tools must add an explicit policy."""
    return {name: tool for name, tool in TOOLS.items() if tool.read_only}
