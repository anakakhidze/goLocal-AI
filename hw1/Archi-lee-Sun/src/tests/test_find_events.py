"""Behavior tests for the individual event finder."""

from datetime import date
import json
from pathlib import Path
import socket
import subprocess
import sys

import pytest


SRC = Path(__file__).resolve().parents[1]
SCRIPT = SRC / "find_events.py"
sys.path.insert(0, str(SRC))
from find_events import find_events, load_snapshot  # noqa: E402


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )


def test_next_three_are_chronological_and_source_backed():
    result = find_events(date(2026, 10, 20))
    assert [event["id"] for event in result] == [
        "valerian-shiukashvili",
        "hans-zimmer-vs-john-williams",
        "harry-potter-mystery-ensemble",
    ]
    assert all(event["source_url"].startswith("https://") for event in result)
    assert all(event["starts_at"][:10] >= "2026-10-20" for event in result)


def test_sort_and_limit_do_not_depend_on_fixture_file_order():
    snapshot = load_snapshot()
    snapshot["events"].reverse()
    result = find_events(date(2026, 10, 20), snapshot=snapshot)
    assert [event["id"] for event in result] == [
        "valerian-shiukashvili",
        "hans-zimmer-vs-john-williams",
        "harry-potter-mystery-ensemble",
    ]


def test_venue_filter_is_case_insensitive_and_excludes_other_venues():
    result = find_events(date(2026, 10, 20), "  king david  ")
    assert [event["id"] for event in result] == ["echo-halloween"]


def test_no_upcoming_events_returns_empty_list():
    assert find_events(date(2026, 11, 1)) == []


def test_lookup_works_with_network_blocked(monkeypatch: pytest.MonkeyPatch):
    def block_network(*_args, **_kwargs):
        raise AssertionError("offline lookup attempted a network call")

    monkeypatch.setattr(socket.socket, "connect", block_network)
    assert find_events(date(2026, 10, 20))


def test_start_date_is_inclusive():
    result = find_events(date(2026, 10, 31))
    assert [event["id"] for event in result] == ["tim-burton-mystery-ensemble"]


def test_invalid_date_fails_before_search():
    result = run_cli("--on-or-after", "2026-02-30")
    assert result.returncode == 2
    assert "date must be YYYY-MM-DD" in result.stderr
    assert not result.stdout


def test_blank_venue_is_rejected():
    result = run_cli("--on-or-after", "2026-10-20", "--venue", " ")
    assert result.returncode == 2
    assert "venue must not be blank" in result.stderr


def test_cli_reports_snapshot_and_original_source():
    result = run_cli("--on-or-after", "2026-10-30", "--venue", "King David")
    assert result.returncode == 0
    body = json.loads(result.stdout)
    assert body["snapshot_date"] == "2026-10-19"
    assert body["time_zone"] == "Asia/Tbilisi"
    assert [event["id"] for event in body["events"]] == ["echo-halloween"]
    assert body["events"][0]["source_url"] == "https://tkt.ge/en/Show/35438"
    assert "Historical snapshot" in body["notice"]


def test_cli_preserves_georgian_event_title_on_windows():
    result = run_cli("--on-or-after", "2026-10-30")
    assert result.returncode == 0
    body = json.loads(result.stdout)
    assert body["events"][0]["title"] == "ერისიონი — ქართული საგანძური"


def test_duplicate_fixture_id_is_rejected(tmp_path: Path):
    snapshot = load_snapshot()
    snapshot["events"].append(snapshot["events"][0].copy())
    file = tmp_path / "events.json"
    file.write_text(json.dumps(snapshot), encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate event id"):
        load_snapshot(file)


@pytest.mark.parametrize(
    ("field", "value"),
    [("source_url", ""), ("starts_at", "2026-02-30T20:00")],
)
def test_malformed_fixture_record_is_rejected(
    tmp_path: Path, field: str, value: str
):
    snapshot = load_snapshot()
    snapshot["events"][0][field] = value
    file = tmp_path / "events.json"
    file.write_text(json.dumps(snapshot), encoding="utf-8")
    with pytest.raises(ValueError):
        load_snapshot(file)
