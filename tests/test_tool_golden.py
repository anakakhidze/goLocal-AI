"""Golden set for the search_events tool, in the course format (Lab-5 templates/test_tool_golden.py).

Runs every file in evals/tools/*.yaml through call_tool(). No model, no API key, no network.
Runs in the CI job on every pull request; a failing case blocks the merge.
"""

from pathlib import Path

import pytest
import yaml

from src.tools.registry import ToolError, call_tool

ROOT = Path(__file__).resolve().parents[1]
FILES = sorted((ROOT / "evals" / "tools").glob("*.yaml"))
CASES = [
    (f.stem, case)
    for f in FILES
    for case in yaml.safe_load(f.read_text(encoding="utf-8"))["cases"]
]


def run_case(case):
    """Return {ok, result} or {ok, error}, the same way the model would see it."""
    try:
        result = call_tool(case["tool"], case["arguments"])
        return {"ok": True, "result": {"ids": [event["external_id"] for event in result]}}
    except ToolError as error:
        return {"ok": False, "error": str(error)}


def subset(expected: dict, actual) -> bool:
    """Every key in `expected` is in `actual` with the same value."""
    return isinstance(actual, dict) and all(k in actual and actual[k] == v for k, v in expected.items())


@pytest.mark.parametrize("owner, case", CASES, ids=[f"{o}:{c['id']}" for o, c in CASES])
def test_tool_golden_case(owner, case):
    out = run_case(case)
    if case["expect"] == "ok":
        assert out["ok"], f"{owner}:{case['id']} should succeed but was refused: {out.get('error')}"
        assert subset(case.get("result_has", {}), out["result"]), f"result was {out['result']}"
    else:
        assert not out["ok"], f"{owner}:{case['id']} should be refused but ran: {out.get('result')}"
        for phrase in case.get("error_has", []):
            assert phrase.lower() in out["error"].lower(), f"error was: {out['error']}"
        assert "Traceback" not in out["error"]


def test_every_file_has_five_cases_including_bad_input_and_adversarial():
    assert FILES, "expected at least one golden file in evals/tools/"
    for f in FILES:
        cases = yaml.safe_load(f.read_text(encoding="utf-8"))["cases"]
        types = [c["type"] for c in cases]
        assert len(cases) >= 5, f"{f.name}: {len(cases)} cases, HW2 needs 5"
        assert "adversarial" in types and "bad-input" in types, f"{f.name}: needs a bad-input and an adversarial case"
        assert types.count("normal") >= 3, f"{f.name}: needs at least 3 normal cases"
