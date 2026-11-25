"""Golden set for the search_events tool. Runs every file in evals/tools/ through call_tool().

No model, no API key, no network. Runs in the CI job on every pull request.
"""

from pathlib import Path

import pytest
import yaml

from src.tools.registry import ToolError, call_tool

ROOT = Path(__file__).resolve().parents[1]
CASE_FILES = sorted((ROOT / "evals" / "tools").glob("*.yaml"))


def _cases():
    for path in CASE_FILES:
        for case in yaml.safe_load(path.read_text(encoding="utf-8"))["cases"]:
            yield pytest.param(case, id=f"{path.stem}:{case['name']}")


def test_golden_files_exist():
    assert CASE_FILES, "expected at least one golden file in evals/tools/"


@pytest.mark.parametrize("case", list(_cases()))
def test_golden_case(case):
    if "error_contains" in case["expect"]:
        with pytest.raises(ToolError) as raised:
            call_tool(case["tool"], case["arguments"])
        assert case["expect"]["error_contains"] in str(raised.value)
        assert "Traceback" not in str(raised.value)
    else:
        result = call_tool(case["tool"], case["arguments"])
        assert [event["id"] for event in result] == case["expect"]["ids"]
