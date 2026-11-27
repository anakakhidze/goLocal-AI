import json
from pathlib import Path

import pytest

from src import catalog, tools
from src.catalog import CatalogError, load_catalog
from src.contracts import FindEventsByKind, GetEventDetails, ListEvents


def test_real_catalog_is_source_backed_and_explicitly_not_live():
    records = load_catalog()
    assert len(records) == 13
    event = tools.get_event_details(GetEventDetails(event_id="valerian-shiukashvili"))
    assert event.source_url == "https://tkt.ge/en/show/35299/valerian-shiukashvili-solo-koncerti"
    assert event.snapshot_date.isoformat() == "2026-10-19"
    assert event.event_time == "2026-10-21, 20:00; doors open at 19:30"
    assert not event.live_verified and "Historical" in event.notice


def test_missing_id_refuses_with_next_step():
    with pytest.raises(tools.ToolFailure, match="list_events"):
        tools.get_event_details(GetEventDetails(event_id="no-such-event"))


def test_uncertainty_is_preserved_instead_of_inventing_an_address():
    record = tools.get_event_details(GetEventDetails(event_id="hardhell"))
    assert "confirm the entrance" in record.location
    assert "does not assert a street number" in record.details


def test_list_returns_bounded_actual_event_ids_without_turning_a_venue_into_a_concert():
    listed = tools.list_events(ListEvents(limit=20)).events
    assert len(listed) == 12
    assert [e.event_id for e in listed] == sorted(e.event_id for e in listed)
    assert "digomi-olympic-pool" not in [e.event_id for e in listed]
    assert len(tools.list_events(ListEvents(limit=1)).events) == 1


def test_read_is_repeatable_and_does_not_modify_the_corpus():
    before = {p.name: p.read_bytes() for p in catalog.CORPUS.glob("*.md")}
    args = GetEventDetails(event_id="hardhell")
    assert tools.get_event_details(args) == tools.get_event_details(args)
    assert before == {p.name: p.read_bytes() for p in catalog.CORPUS.glob("*.md")}


def test_lookup_reloads_current_curated_data_instead_of_a_global_cache(tmp_path, monkeypatch):
    path = tmp_path / "test-event.md"
    template = "# {title}\n\n- Source: https://example.org/event\n- Compiled from the public listing: 2026-11-23\n- Event time: unknown\n\n## Details\nReviewed text.\n"
    monkeypatch.setattr(catalog, "CORPUS", tmp_path)
    path.write_text(template.format(title="First"), encoding="utf-8")
    assert tools.get_event_details(GetEventDetails(event_id="test-event")).title == "First"
    path.write_text(template.format(title="Updated"), encoding="utf-8")
    assert tools.get_event_details(GetEventDetails(event_id="test-event")).title == "Updated"


@pytest.mark.parametrize("content", ["# No metadata", "# Bad\n- Source: file:///private\n## Details\nx",
    "# Bad\n- Source: https://example.org\n- Compiled from the public listing: 2026-02-30\n## Details\nx"])
def test_corrupt_data_fails_closed_without_a_path_or_traceback(tmp_path, content):
    (tmp_path / "event.md").write_text(content, encoding="utf-8")
    with pytest.raises(CatalogError) as error:
        load_catalog(tmp_path)
    assert str(tmp_path) not in str(error.value) and "retry" in str(error.value)


def test_registry_exposes_only_public_reads():
    assert set(tools.TOOLS) == {"list_events", "get_event_details", "search_events", "find_events_by_kind"}
    assert tools.tools_for(None) == tools.tools_for("caller-a") == tools.tools_for("caller-b")
    assert all(tool.read_only for tool in tools.TOOLS.values())


def test_find_events_by_kind_returns_only_the_allowlisted_summaries():
    result = tools.find_events_by_kind(FindEventsByKind(kind="event", limit=3))
    assert [event.id for event in result.events] == ["echo-halloween", "erisioni", "golden-harlequin"]
    assert all(set(event.model_dump()) == {"id", "title", "kind", "source_url", "snapshot_date"}
               and event.kind == "event" for event in result.events)
    assert "details" not in result.model_dump_json().casefold()


def test_find_events_by_kind_venue_is_repeatable_and_limit_is_exact():
    args = FindEventsByKind(kind="venue", limit=10)
    first = tools.find_events_by_kind(args)
    assert first == tools.find_events_by_kind(args)
    assert [event.id for event in first.events] == ["digomi-olympic-pool"]
    limited = tools.find_events_by_kind(FindEventsByKind(kind="event", limit=1))
    assert [event.id for event in limited.events] == ["echo-halloween"]
