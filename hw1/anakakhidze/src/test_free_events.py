"""Tests for the free-event finder. They use fictional data and never touch the network."""

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

from free_events import EventDataError, find_free_events, load_events

CLI = Path(__file__).with_name("cli.py")
SAMPLE = Path(__file__).with_name("sample_events.json")


def record(**overrides):
    base = {
        "id": 1,
        "title": "Test Event",
        "venue": "Test Venue",
        "start": "2026-10-24T19:00:00+04:00",
        "price": 0,
        "source_url": "https://example.com/events/1",
    }
    base.update(overrides)
    return base


def test_returns_only_free_events_in_range_sorted_by_start_then_id():
    events = load_events([
        record(id=3, start="2026-10-25T10:00:00+04:00"),
        record(id=1, start="2026-10-24T19:00:00+04:00"),
        record(id=2, start="2026-10-24T19:00:00+04:00"),
    ])
    found = find_free_events(events, date(2026, 10, 20), date(2026, 10, 31))
    assert [event.id for event in found] == [1, 2, 3]


def test_excludes_paid_and_unknown_price_events():
    events = load_events([
        record(id=1, price=25),
        record(id=2, price=None),
        record(id=3, price=0),
    ])
    found = find_free_events(events, date(2026, 10, 20), date(2026, 10, 31))
    assert [event.id for event in found] == [3]


def test_range_is_inclusive_on_both_ends():
    events = load_events([
        record(id=1, start="2026-10-20T00:30:00+04:00"),
        record(id=2, start="2026-10-31T23:30:00+04:00"),
        record(id=3, start="2026-11-01T00:30:00+04:00"),
        record(id=4, start="2026-10-19T23:30:00+04:00"),
    ])
    found = find_free_events(events, date(2026, 10, 20), date(2026, 10, 31))
    assert [event.id for event in found] == [1, 2]


def test_no_matches_returns_empty_list():
    events = load_events([record(id=1, price=10)])
    assert find_free_events(events, date(2026, 10, 20), date(2026, 10, 31)) == []


def test_from_after_to_is_rejected():
    with pytest.raises(ValueError):
        find_free_events([], date(2026, 10, 31), date(2026, 10, 20))


@pytest.mark.parametrize("bad", [
    record(source_url="http://example.com/events/1"),
    record(title="   "),
    record(venue=None),
    record(start="2026-10-24T19:00:00"),
    record(price=-5),
    record(price=True),
    record(id=0),
])
def test_malformed_records_are_rejected(bad):
    with pytest.raises(EventDataError):
        load_events([bad])


def test_duplicate_ids_are_rejected():
    with pytest.raises(EventDataError):
        load_events([record(id=1), record(id=1, title="Other")])


def test_cli_prints_json_for_the_sample_file():
    result = subprocess.run(
        [sys.executable, str(CLI), "--from", "2026-10-20", "--to", "2026-10-31", "--file", str(SAMPLE)],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert [item["id"] for item in output] == [3, 1, 5]
    assert set(output[0]) == {"id", "title", "venue", "start", "source_url"}


def test_cli_prints_empty_list_with_exit_zero():
    result = subprocess.run(
        [sys.executable, str(CLI), "--from", "2030-01-01", "--to", "2030-01-02", "--file", str(SAMPLE)],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert result.returncode == 0
    assert json.loads(result.stdout) == []


def test_cli_rejects_bad_date_with_exit_two():
    result = subprocess.run(
        [sys.executable, str(CLI), "--from", "24/10/2026", "--to", "2026-10-31", "--file", str(SAMPLE)],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert result.returncode == 2


def test_cli_rejects_reversed_range_with_exit_two():
    result = subprocess.run(
        [sys.executable, str(CLI), "--from", "2026-10-31", "--to", "2026-10-20", "--file", str(SAMPLE)],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert result.returncode == 2


def test_cli_rejects_malformed_file_with_exit_one(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text(json.dumps([record(source_url="http://example.com")]), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(CLI), "--from", "2026-10-20", "--to", "2026-10-31", "--file", str(bad_file)],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert result.returncode == 1
