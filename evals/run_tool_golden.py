"""Record actual offline tool golden outcomes; never substitutes for remote CI evidence."""
from datetime import datetime, timezone
import json
from pathlib import Path

import yaml

from src.act import call_tool
from src.tools import tools_for


def run(owner="Archi-lee-Sun"):
    root = Path(__file__).resolve().parents[1]
    path = root / "evals" / "tools" / f"{owner}.yaml"
    specification = yaml.safe_load(path.read_text(encoding="utf-8"))
    rows = []
    for case in specification["cases"]:
        outcome = call_tool({"id": case["id"], "name": case["tool"], "arguments": json.dumps(case["arguments"])},
                            tools_for(case.get("caller")), case.get("caller"))
        if case["expect"] == "ok":
            passed = outcome["ok"] and all(outcome["result"].get(k) == v for k, v in case.get("result_has", {}).items())
        else:
            passed = not outcome["ok"] and all(p.casefold() in outcome["error"].casefold()
                                               for p in case.get("error_has", []))
        rows.append({"id": case["id"], "type": case["type"], "why": case["why"],
                     "expected": case["expect"], "passed": passed, "actual": outcome})
    return {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "owner": owner,
            "mode": "offline-real-executor", "model_calls": 0, "passed": sum(r["passed"] for r in rows),
            "total": len(rows), "cases": rows}


if __name__ == "__main__":
    report = run()
    output = Path(__file__).resolve().parent / "results" / "2026-11-23-Archi-lee-Sun-tools.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{report['passed']}/{report['total']} actual cases passed; report: {output.name}; zero model calls")
    raise SystemExit(0 if report["passed"] == report["total"] else 1)
