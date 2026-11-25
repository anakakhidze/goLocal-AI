"""Product functions and their shared registry. Neither capability changes user state."""
from dataclasses import dataclass
from typing import Callable

from pydantic import BaseModel, ConfigDict

from .catalog import CatalogError, EventDetails, load_catalog
from .contracts import Contract, GetEventDetails, ListEvents
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
    Tool("search_events", SearchEvents, search_events),  # anakakhidze's HW2
)}


def tools_for(caller: str | None) -> dict[str, Tool]:
    """Public reads need no account. Future private/write tools must add an explicit policy."""
    return {name: tool for name, tool in TOOLS.items() if tool.read_only}
