"""Filter behaviour of HW2 search_events, checked on GoLocal's fictional fixture. No database, no model."""

import pytest
from pydantic import ValidationError

from src.search_events import SearchEvents, search_events


def run(**arguments):
    return search_events(SearchEvents(city="Tbilisi", **arguments)).event_ids


def test_budget_excludes_unknown_prices():
    # 'mystery-activity' and 'robot-demo' have unknown prices; they never match a price limit.
    ids = run(max_price_gel=500, limit=12)
    assert "mystery-activity" not in ids and "robot-demo" not in ids


def test_results_are_sorted_by_start_then_id():
    starts = [event.start for event in search_events(SearchEvents(city="Tbilisi", limit=12)).events]
    assert starts == sorted(starts)
    assert starts[0].startswith("2026-10-20") and starts[1].startswith("2026-10-21")


def test_limit_cuts_the_list():
    assert len(run(limit=2)) == 2


def test_keyword_is_case_insensitive():
    assert run(keyword="JAZZ") == ["paper-lantern-jazz"]


def test_date_window_is_inclusive():
    assert run(start_date="2026-10-22", end_date="2026-10-22") == ["color-and-light"]


def test_end_before_start_is_refused():
    with pytest.raises(ValidationError):
        SearchEvents(city="Tbilisi", start_date="2026-10-22", end_date="2026-10-20")


def test_unreal_date_is_refused():
    with pytest.raises(ValueError):
        SearchEvents(city="Tbilisi", start_date="2026-02-30")


def test_sql_text_in_keyword_is_refused():
    with pytest.raises(ValidationError):
        SearchEvents(city="Tbilisi", keyword="x' OR '1'='1")


def test_every_result_has_the_required_fields_and_an_https_link():
    result = search_events(SearchEvents(city="Tbilisi", limit=3))
    for event in result.events:
        assert event.source_url.startswith("https://")
        assert event.start.endswith("+04:00")
