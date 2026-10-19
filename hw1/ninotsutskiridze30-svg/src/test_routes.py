from copy import deepcopy
from datetime import date
import json
from pathlib import Path
import subprocess
import sys

import pytest

from decision import decide
from extractor import offline_extract, process


TEXT = "KIU Robotics Club, Open Build Night, Thursday 22 October 2026, 18:00, Lab B204"
TODAY = date(2026, 10, 18)
ROOMS = {"B204"}


def run(raw=None, text=TEXT, today=TODAY, rooms=ROOMS):
    return decide(offline_extract(text) if raw is None else raw, text, today, rooms)


def codes(result):
    assert all(flag["reason"].strip() for flag in result["flags"])
    return {flag["code"] for flag in result["flags"]}


def test_clean_announcement_is_normalized_and_accepted():
    result = run()
    assert result["route"] == "accepted"
    assert result["flags"] == []
    assert {key: field["value"] for key, field in result["fields"].items()} == {
        "title": "Open Build Night", "date": "2026-10-22", "time": "18:00", "location": "B204"}
    assert all(field["evidence"] in TEXT for field in result["fields"].values())


def test_offline_date_removed_routes_to_review():
    result = process(TEXT.replace("Thursday 22 October 2026, ", ""), TODAY, ROOMS)
    assert result["route"] == "review"
    assert result["fields"]["date"] == {"value": "", "evidence": "", "confidence": 0.0}
    assert any(flag["code"] == "missing_required" and flag["field"] == "date"
               for flag in result["flags"])


def test_offline_quiet_hours_are_rejected():
    result = process("Quiet hours in the library are 22:00 to 08:00", TODAY, ROOMS)
    assert result["route"] == "rejected"
    assert all(field["value"] == "" for field in result["fields"].values())


@pytest.mark.parametrize("field", ["title", "date", "location"])
def test_required_field_missing_is_empty_review(field):
    raw = offline_extract(TEXT)
    raw[field] = {"value": "", "evidence": "", "confidence": 1.0}
    result = run(raw)
    assert result["route"] == "review"
    assert result["fields"][field]["value"] == ""
    assert "missing_required" in codes(result)


@pytest.mark.parametrize("field", ["title", "date", "location", "time"])
@pytest.mark.parametrize("evidence", ["", "invented evidence"])
def test_absent_evidence_never_prefills_even_high_confidence(field, evidence):
    raw = offline_extract(TEXT)
    raw[field]["evidence"] = evidence
    raw[field]["confidence"] = 1.0
    result = run(raw)
    assert result["route"] == "review"
    assert result["fields"][field] == {"value": "", "evidence": "", "confidence": 0.0}
    assert "no_evidence" in codes(result)


def test_real_evidence_must_support_the_value():
    raw = offline_extract(TEXT)
    raw["date"]["value"] = "2026-10-23"
    result = run(raw)
    assert result["route"] == "review"
    assert result["fields"]["date"]["value"] == ""
    assert "unsupported_value" in codes(result)


@pytest.mark.parametrize("text,today,rooms,code", [
    (TEXT, date(2026, 10, 23), ROOMS, "past_date"),
    (TEXT.replace("Thursday", "Friday"), TODAY, ROOMS, "weekday_mismatch"),
    (TEXT, TODAY, {"A112"}, "unknown_room"),
])
def test_soft_flags_request_confirmation(text, today, rooms, code):
    result = run(text=text, today=today, rooms=rooms)
    assert result["route"] == "confirm"
    assert code in codes(result)
    assert result["fields"]["date"]["value"] == "2026-10-22"


@pytest.mark.parametrize("confidence,route", [(0.59, "confirm"), (0.6, "accepted")])
def test_confidence_threshold_after_evidence_checks(confidence, route):
    raw = offline_extract(TEXT)
    raw["title"]["confidence"] = confidence
    result = run(raw)
    assert result["route"] == route
    assert ("low_confidence" in codes(result)) == (confidence < 0.6)


@pytest.mark.parametrize("bad", [None, {}, {"is_event": "yes"}, {"is_event": True, "extra": 1},
    {"is_event": True, "title": {"value": 3}},
    {"is_event": True, "title": {"confidence": 1.1}},
    {"is_event": True, "date": {"confidence": float("nan")}}])
def test_schema_errors_route_to_review_with_empty_fields(bad):
    result = decide(bad, TEXT, TODAY, ROOMS)
    assert result["route"] == "review"
    assert "invalid_extraction" in codes(result)
    assert all(field["value"] == "" for field in result["fields"].values())


def test_notice_rejected_and_fake_extractor_is_injectable(monkeypatch):
    monkeypatch.delenv("EVENT_MODEL_API_KEY", raising=False)
    calls = []
    def fake(text):
        calls.append(text)
        return {"is_event": False}
    result = process("Quiet hours in the library are 22:00 to 08:00", TODAY, ROOMS, extractor=fake)
    assert len(calls) == 1
    assert result["route"] == "rejected"
    assert "not_event" in codes(result)
    assert all(field["value"] == "" for field in result["fields"].values())


def test_review_precedes_soft_flags_and_does_not_mutate_input():
    raw = offline_extract(TEXT)
    raw["date"]["evidence"] = ""
    raw["title"]["confidence"] = 0.1
    original = deepcopy(raw)
    result = run(raw)
    assert result["route"] == "review"
    assert {"no_evidence", "low_confidence"} <= codes(result)
    assert raw == original


def test_optional_time_missing_does_not_block_acceptance():
    result = run(text=TEXT.replace(", 18:00", ""))
    assert result["route"] == "accepted"
    assert result["fields"]["time"]["value"] == ""


def test_invalid_calendar_date_is_empty_review():
    result = run(text=TEXT.replace("22 October", "32 October"))
    assert result["route"] == "review"
    assert "invalid_value" in codes(result)
    assert result["fields"]["date"]["value"] == ""


def test_am_pm_and_room_case_normalization():
    result = run(text=TEXT.replace("18:00", "6:00 PM").replace("Lab B204", "room b204"))
    assert result["route"] == "accepted"
    assert result["fields"]["time"]["value"] == "18:00"
    assert result["fields"]["location"]["value"] == "B204"


def test_cli_serializes_route_without_api_key(monkeypatch):
    monkeypatch.delenv("EVENT_MODEL_API_KEY", raising=False)
    script = Path(__file__).with_name("cli.py")
    run_cli = subprocess.run([sys.executable, str(script), TEXT, "--today", "2026-10-18"],
                             capture_output=True, text=True)
    assert run_cli.returncode == 0, run_cli.stderr
    assert json.loads(run_cli.stdout)["route"] == "accepted"
