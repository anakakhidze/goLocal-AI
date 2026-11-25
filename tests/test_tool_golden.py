"""Every student's actual YAML cases run through the production executor in required CI."""
from collections import Counter
import json
from pathlib import Path

import pytest
import yaml

from src.act import call_tool
from src.tools import tools_for

ROOT = Path(__file__).resolve().parents[1]
FILES = sorted((ROOT / "evals" / "tools").glob("*.yaml"))
CASES = [(f.stem, case) for f in FILES for case in yaml.safe_load(f.read_text(encoding="utf-8"))["cases"]]


@pytest.mark.parametrize("owner,case", CASES, ids=[f"{o}:{c['id']}" for o, c in CASES])
def test_tool_golden_case(owner, case):
    out = call_tool({"id": case["id"], "name": case["tool"], "arguments": json.dumps(case["arguments"])},
                    tools_for(case.get("caller")), case.get("caller"))
    if case["expect"] == "ok":
        assert out["ok"], f"{owner}:{case['id']}: {out['error']}"
        assert all(out["result"].get(k) == v for k, v in case.get("result_has", {}).items())
    else:
        assert not out["ok"], f"{owner}:{case['id']} executed when it should refuse"
        for phrase in case.get("error_has", []):
            assert phrase.casefold() in out["error"].casefold()


def test_golden_files_exist_and_have_the_required_real_cases():
    assert FILES, "A missing golden directory must not silently pass CI"
    for path in FILES:
        spec = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert spec["tool_owner"] == path.stem
        cases = spec["cases"]
        counts = Counter(c["type"] for c in cases)
        assert len(cases) >= 5 and counts["normal"] >= 3
        assert counts["bad-input"] >= 1 and counts["adversarial"] >= 1
        assert len({c["id"] for c in cases}) == len(cases)
        assert all(c.get("why") and c["expect"] in {"ok", "refused"} for c in cases)
